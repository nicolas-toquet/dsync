import os
import sys
import toml
import deemix
import pkgutil
from pathlib import Path
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3

# --- 1. FONCTIONS DE CONFIGURATION ---
def load_config():
    """Charge le fichier de configuration TOML"""
    config_path = os.path.join(os.path.dirname(__file__), "config.toml")
    if not os.path.exists(config_path):
        print(f"❌ Erreur : {config_path} introuvable.")
        sys.exit(1)
    return toml.load(config_path)

# --- 2. FONCTION D'IMPORT DYNAMIQUE ---
def find_class_in_package(package, class_name):
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = __import__(name, fromlist=[class_name])
            if hasattr(module, class_name):
                return getattr(module, class_name)
        except (ImportError, AttributeError):
            continue
    return None

# Initialisation des composants Deemix
DeezerInterface = find_class_in_package(deemix, 'Deezer') 
Downloader = find_class_in_package(deemix, 'Downloader')
generateDownloadObject = find_class_in_package(deemix, 'generateDownloadObject')
loadSettings = find_class_in_package(deemix, 'load')

# --- 3. CLASSES ET UTILITAIRES ---
class LogListener:
    @classmethod
    def send(cls, key, value=None):
        if key == 'info': print(f"ℹ️ {value}")
        elif key == 'downloading': print(f"📥 Téléchargement : {value.get('title')}")
        elif key == 'finished': print(f"✅ Terminé : {value.get('title')}")

def tag_file_with_id(filepath, track_id):
    """ Enregistre l'ID Deezer dans les métadonnées du fichier """
    try:
        if filepath.endswith('.mp3'):
            audio = EasyID3(filepath)
            audio['website'] = str(track_id)
            audio.save()
        elif filepath.endswith('.flac'):
            audio = FLAC(filepath)
            audio['deezer_id'] = str(track_id)
            audio.save()
    except Exception as e:
        print(f"⚠️ Erreur tag {filepath}: {e}")

def get_id_from_tags(filepath):
    """ Lit l'ID Deezer depuis les métadonnées """
    try:
        if filepath.endswith('.mp3'):
            return EasyID3(filepath).get('website', [None])[0]
        elif filepath.endswith('.flac'):
            return FLAC(filepath).get('deezer_id', [None])[0]
    except:
        return None

# --- 4. LOGIQUE DE SYNCHRONISATION ---
def sync_playlist(playlist_id):
    config = load_config()
    listener = LogListener()
    
    dz = DeezerInterface()
    dz.login_via_arl(config['deezer']['arl'])

    print(f"📡 Analyse de la playlist {playlist_id}...")
    playlist_data = dz.api.get_playlist(playlist_id)
    tracks = dz.api.get_playlist_tracks(playlist_id)
    
    if not tracks:
        print("❌ Impossible de récupérer les morceaux.")
        return

    # Extraction robuste des IDs (en isolant la clé 'data')
    deezer_track_ids = set()
    
    # On vérifie si tracks est un dictionnaire avec une clé 'data' (cas habituel de l'API)
    actual_tracks = tracks.get('data', tracks) if isinstance(tracks, dict) else tracks

    for t in actual_tracks:
        if hasattr(t, 'id'): tid = str(t.id)
        elif isinstance(t, dict): tid = str(t.get('id'))
        else: tid = str(t)
        
        if tid.isdigit(): # On ne garde que ce qui est un nombre (on ignore 'data', 'next', etc.)
            deezer_track_ids.add(tid)
    
    playlist_title = playlist_data.title if hasattr(playlist_data, 'title') else playlist_data.get('title')
    base_path = config['storage']['base_path']
    expected_path = os.path.join(base_path, f"{playlist_id} - {playlist_title}")
    os.makedirs(expected_path, exist_ok=True)

    # --- ÉTAPE A : NETTOYAGE DES OBSOLÈTES ---
    print("🔍 Scan du dossier local pour nettoyage...")
    already_downloaded_ids = set()
    
    for filename in os.listdir(expected_path):
        if filename.endswith(('.mp3', '.flac')):
            full_path = os.path.join(expected_path, filename)
            # On tente de lire l'ID dans les tags, sinon on prend le début du nom (compatibilité)
            f_id = get_id_from_tags(full_path) or filename.split(' - ')[0]
            
            if f_id in deezer_track_ids:
                already_downloaded_ids.add(str(f_id))
            else:
                print(f"🗑️ Supprimé de Deezer -> Nettoyage : {filename}")
                os.remove(full_path)

    # --- ÉTAPE B : FILTRAGE ET TÉLÉCHARGEMENT ---
    settings = loadSettings()
    settings['downloadLocation'] = expected_path
    settings['createPlaylistFolder'] = False
    settings['tracknameTemplate'] = "%artist% - %title%" # Format propre
    settings['fallbackBitrate'] = True # Évite les erreurs si le 320 n'est pas dispo
    
    bitrate_map = {"FLAC": 9, "MP3_320": 3, "MP3_128": 1}
    bitrate = bitrate_map.get(config['storage'].get('format'), 3)

    ids_to_download = [tid for tid in deezer_track_ids if tid not in already_downloaded_ids]

    if not ids_to_download:
        print("✅ Tous les morceaux sont déjà présents (vérifié par tags).")
    else:
        print(f"🚀 {len(ids_to_download)} nouveaux morceaux à télécharger...")
        for track_id in ids_to_download:
            url = f"https://www.deezer.com/track/{track_id}"
            try:
                downloadObject = generateDownloadObject(dz, url, bitrate, {}, listener)
                if not isinstance(downloadObject, list): downloadObject = [downloadObject]
                for obj in downloadObject:
                    Downloader(dz, obj, settings, listener).start()
                
                # --- ÉTAPE C : TAGGING IMMÉDIAT ---
                # On cherche le fichier qui vient d'être créé pour lui mettre son tag
                # Comme on ne connaît pas le nom exact, on tag tout ce qui n'a pas encore d'ID
                for filename in os.listdir(expected_path):
                    if filename.endswith(('.mp3', '.flac')):
                        fp = os.path.join(expected_path, filename)
                        if get_id_from_tags(fp) is None:
                            tag_file_with_id(fp, track_id)
            except Exception as e:
                print(f"⚠️ Erreur sur la piste {track_id}: {e}")

    print("\n✨ Synchronisation terminée !")

# --- 5. POINT D'ENTRÉE ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        sync_playlist(sys.argv[1])
    else:
        print("Usage: python3 sync_deezer.py <PLAYLIST_ID>")