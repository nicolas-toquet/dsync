import os
import sys
import toml
import deemix
import pkgutil
from pathlib import Path

# --- FONCTION D'IMPORT DYNAMIQUE ---
def find_class_in_package(package, class_name):
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = __import__(name, fromlist=[class_name])
            if hasattr(module, class_name):
                return getattr(module, class_name)
        except (ImportError, AttributeError):
            continue
    return None

# Chargement automatique des outils
# Note: On cherche 'Deezer' dans le paquet deemix pour l'interface
DeezerInterface = find_class_in_package(deemix, 'Deezer') 
Downloader = find_class_in_package(deemix, 'Downloader')
generateDownloadObject = find_class_in_package(deemix, 'generateDownloadObject')
loadSettings = find_class_in_package(deemix, 'load') # Pour deemix.settings.load

if not all([DeezerInterface, Downloader, generateDownloadObject, loadSettings]):
    print("❌ Erreur : Certains composants de deemix sont introuvables.")
    exit(1)

# --- CLASSE LOGS (Indispensable pour le Downloader) ---
class LogListener:
    @classmethod
    def send(cls, key, value=None):
        # Affiche simplement les infos dans le terminal
        if key == 'info': print(f"ℹ️ {value}")
        elif key == 'downloading': print(f"📥 Téléchargement : {value.get('title')}")
        elif key == 'finished': print(f"✅ Terminé : {value.get('title')}")

# --- LOGIQUE DU SCRIPT ---

def load_config():
    if not os.path.exists("config.toml"):
        print("Erreur : config.toml introuvable.")
        sys.exit(1)
    return toml.load("config.toml")

def sync_playlist(playlist_id):
    config = load_config()
    listener = LogListener()
    
    dz = DeezerInterface()
    dz.login_via_arl(config['deezer']['arl'])

    print(f"📡 Récupération des données pour la playlist {playlist_id}...")
    
    # Récupération des infos et des pistes
    playlist_data = dz.api.get_playlist(playlist_id)
    tracks = dz.api.get_playlist_tracks(playlist_id)
    
    if not tracks:
        print("❌ Impossible de récupérer les morceaux. Abandon pour éviter une suppression accidentelle.")
        return

    # Correction de l'erreur d'index : on extrait les IDs proprement
    deezer_track_ids = set()
    for t in tracks:
        if hasattr(t, 'id'): tid = str(t.id) # Si c'est un objet
        elif isinstance(t, dict): tid = str(t.get('id')) # Si c'est un dict
        else: tid = str(t) # Si c'est déjà l'ID
        deezer_track_ids.add(tid)

    playlist_title = playlist_data.title if hasattr(playlist_data, 'title') else playlist_data.get('title')
    base_path = config['storage']['base_path']
    expected_path = os.path.join(base_path, f"{playlist_id} - {playlist_title}")
    
    if not os.path.exists(expected_path):
        os.makedirs(expected_path, exist_ok=True)

    # --- PHASE 1 : SUPPRESSION DU SURPLUS ---
    print("🔍 Comparaison avec le dossier local...")
    local_files = [f for f in os.listdir(expected_path) if f.endswith(('.mp3', '.flac'))]
    
    deleted_count = 0
    for filename in local_files:
        # On vérifie si l'ID (au début du nom) est toujours dans la playlist
        # On part du principe que le fichier commence par "ID - "
        file_id = filename.split(' - ')[0]
        
        if file_id not in deezer_track_ids:
            print(f"🗑️ Obsolète (supprimé de Deezer) : {filename}")
            os.remove(os.path.join(expected_path, filename))
            deleted_count += 1

    if deleted_count == 0:
        print("✅ Aucun fichier à supprimer.")

    # --- PHASE 2 : TÉLÉCHARGEMENT DES MANQUANTS ---
    print(f"🚀 Synchronisation vers : {expected_path}")
    
    settings = loadSettings()
    settings['downloadLocation'] = expected_path
    settings['createPlaylistFolder'] = False
    # Template CRUCIAL pour que la suppression fonctionne au prochain coup
    settings['tracknameTemplate'] = "%track_id% - %artist% - %title%"
    
    bitrate_map = {"FLAC": 9, "MP3_320": 3, "MP3_128": 1}
    bitrate = bitrate_map.get(config['storage'].get('format'), 3)

    url = f"https://www.deezer.com/playlist/{playlist_id}"
    downloadObject = generateDownloadObject(dz, url, bitrate, {}, listener)

    if isinstance(downloadObject, list):
        for obj in downloadObject:
            Downloader(dz, obj, settings, listener).start()
    else:
        Downloader(dz, downloadObject, settings, listener).start()

    print("\n✨ Synchronisation terminée !")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sync_playlist(sys.argv[1])
    else:
        print("Usage: python sync_deezer.py <PLAYLIST_ID>")