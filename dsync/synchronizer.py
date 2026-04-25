"""
Logique principale de synchronisation des playlists.
"""

import os
from typing import Set, List

from .config import Config
from .deezer_client import DeezerClient
from .metadata import MetadataManager
from .utils import LogListener


class PlaylistSynchronizer:
    """Synchroniseur de playlists Deezer."""
    
    def __init__(self, config: Config):
        """
        Initialise le synchroniseur.
        
        Args:
            config: Configuration du projet
        """
        self.config = config
        self.metadata_manager = MetadataManager()
        self.listener = LogListener()
        self.client = DeezerClient(config.deezer_arl)
    
    def sync_playlist(self, playlist_id: str) -> bool:
        """
        Synchronise une playlist Deezer.
        
        Args:
            playlist_id: ID de la playlist à synchroniser
        
        Returns:
            True si la synchronisation réussit
        """
        print(f"\n{'='*60}")
        print(f"🎵 Synchronisation de la playlist {playlist_id}")
        print(f"{'='*60}\n")
        
        # Connexion à Deezer
        if not self.client.connect():
            return False
        
        # Récupération des informations de la playlist
        playlist_info = self.client.get_playlist_info(playlist_id)
        if not playlist_info:
            return False
        
        playlist_title = self._get_item_title(playlist_info, 'Playlist')
        print(f"📋 Playlist : {playlist_title}")
        
        # Récupération des morceaux
        print(f"📡 Analyse de la playlist...")
        deezer_track_ids = self.client.get_playlist_tracks(playlist_id)
        
        if not deezer_track_ids:
            print("❌ Aucun morceau à synchroniser")
            return False
        
        print(f"✅ {len(deezer_track_ids)} morceaux trouvés dans la playlist")
        
        # Préparation du dossier de destination
        download_path = self._prepare_download_path(playlist_id, playlist_title, "playlist")
        
        # Étape 1 : Nettoyage des morceaux obsolètes
        already_downloaded_ids = self._cleanup_obsolete_tracks(
            download_path, 
            deezer_track_ids
        )
        
        # Étape 2 : Téléchargement des nouveaux morceaux
        ids_to_download = [
            tid for tid in deezer_track_ids 
            if tid not in already_downloaded_ids
        ]
        
        if not ids_to_download:
            print("\n✅ Tous les morceaux sont déjà présents")
        else:
            self._download_new_tracks(
                ids_to_download,
                download_path
            )
        
        print(f"\n{'='*60}")
        print("✨ Synchronisation terminée !")
        print(f"{'='*60}\n")
        
        return True
    
    def sync_album(self, album_id: str) -> bool:
        """
        Synchronise un album Deezer.
        
        Args:
            album_id: ID de l'album à synchroniser
        
        Returns:
            True si la synchronisation réussit
        """
        print(f"\n{'='*60}")
        print(f"💿 Synchronisation de l'album {album_id}")
        print(f"{'='*60}\n")
        
        # Connexion à Deezer
        if not self.client.connect():
            return False
        
        # Récupération des informations de l'album
        album_info = self.client.get_album_info(album_id)
        if not album_info:
            return False
        
        album_title = self._get_item_title(album_info, 'Album')
        print(f"💿 Album : {album_title}")
        
        # Récupération des morceaux
        print(f"📡 Analyse de l'album...")
        deezer_track_ids = self.client.get_album_tracks(album_id)
        
        if not deezer_track_ids:
            print("❌ Aucun morceau à synchroniser")
            return False
        
        print(f"✅ {len(deezer_track_ids)} morceaux trouvés dans l'album")
        
        # Préparation du dossier de destination
        download_path = self._prepare_download_path(album_id, album_title, "album")
        
        # Étape 1 : Nettoyage des morceaux obsolètes
        already_downloaded_ids = self._cleanup_obsolete_tracks(
            download_path, 
            deezer_track_ids
        )
        
        # Étape 2 : Téléchargement des nouveaux morceaux
        ids_to_download = [
            tid for tid in deezer_track_ids 
            if tid not in already_downloaded_ids
        ]
        
        if not ids_to_download:
            print("\n✅ Tous les morceaux sont déjà présents")
        else:
            self._download_new_tracks(
                ids_to_download,
                download_path
            )
        
        print(f"\n{'='*60}")
        print("✨ Synchronisation terminée !")
        print(f"{'='*60}\n")
        
        return True
    
    def _get_item_title(self, item_info, default_prefix: str = 'Item') -> str:
        """Extrait le titre d'un item (playlist ou album)."""
        if hasattr(item_info, 'title'):
            return item_info.title
        elif isinstance(item_info, dict):
            return item_info.get('title', f'{default_prefix} sans nom')
        return f'{default_prefix} sans nom'
    
    def _prepare_download_path(self, item_id: str, item_title: str, item_type: str = "playlist") -> str:
        """
        Prépare le dossier de destination pour les téléchargements.
        
        Args:
            item_id: ID de la playlist ou de l'album
            item_title: Titre de la playlist ou de l'album
            item_type: Type d'item ("playlist" ou "album")
        
        Returns:
            Chemin complet du dossier
        """
        # Créer le sous-dossier Playlists/ ou Albums/
        category_folder = "Playlists" if item_type == "playlist" else "Albums"
        category_path = os.path.join(self.config.base_path, category_folder)
        os.makedirs(category_path, exist_ok=True)
        
        # Chercher un dossier existant avec cet ID (peu importe le titre)
        existing_folder = None
        if os.path.exists(category_path):
            for folder in os.listdir(category_path):
                if folder.startswith(f"{item_id} - ") or folder == item_id:
                    existing_folder = folder
                    break
        
        # Créer le dossier avec le format ID - Titre
        folder_name = f"{item_id} - {item_title}"
        download_path = os.path.join(category_path, folder_name)
        
        # Si un ancien dossier existe avec un nom différent, le renommer
        if existing_folder and existing_folder != folder_name:
            old_path = os.path.join(category_path, existing_folder)
            if os.path.exists(old_path) and old_path != download_path:
                print(f"📝 Renommage du dossier : {existing_folder} → {folder_name}")
                os.rename(old_path, download_path)
        
        os.makedirs(download_path, exist_ok=True)
        
        # Sauvegarder les métadonnées dans un fichier .info pour référence
        info_file = os.path.join(download_path, '.info')
        import json
        info_data = {
            'id': item_id,
            'title': item_title,
            'type': item_type
        }
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info_data, f, ensure_ascii=False, indent=2)
        
        return download_path
    
    def _cleanup_obsolete_tracks(
        self, 
        download_path: str, 
        current_track_ids: Set[str]
    ) -> Set[str]:
        """
        Nettoie les morceaux qui ne sont plus dans la playlist.
        
        Args:
            download_path: Chemin du dossier des téléchargements
            current_track_ids: IDs des morceaux actuels dans la playlist
        
        Returns:
            Ensemble des IDs des morceaux déjà téléchargés
        """
        print("\n🔍 Scan du dossier local pour nettoyage...")
        
        already_downloaded = set()
        files_to_remove = []
        
        if not os.path.exists(download_path):
            return already_downloaded
        
        for filename in os.listdir(download_path):
            if not self.metadata_manager.is_audio_file(filename):
                continue
            
            full_path = os.path.join(download_path, filename)
            
            # Récupération de l'ID depuis les tags ou le nom de fichier
            file_id = self.metadata_manager.get_id_from_tags(full_path)
            if not file_id:
                file_id = self.metadata_manager.get_track_id_from_filename(filename)
            
            if file_id in current_track_ids:
                already_downloaded.add(file_id)
            else:
                files_to_remove.append((full_path, filename))
        
        # Suppression des fichiers obsolètes
        for full_path, filename in files_to_remove:
            try:
                os.remove(full_path)
                print(f"🗑️  Supprimé : {filename}")
            except Exception as e:
                print(f"⚠️  Impossible de supprimer {filename}: {e}")
        
        if files_to_remove:
            print(f"✅ {len(files_to_remove)} fichier(s) obsolète(s) supprimé(s)")
        else:
            print("✅ Aucun fichier obsolète")
        
        print(f"✅ {len(already_downloaded)} fichier(s) déjà téléchargé(s)")
        
        return already_downloaded
    
    def _download_new_tracks(self, track_ids: List[str], download_path: str):
        """
        Télécharge les nouveaux morceaux.
        
        Args:
            track_ids: Liste des IDs à télécharger
            download_path: Chemin de destination
        """
        print(f"\n🚀 Téléchargement de {len(track_ids)} nouveau(x) morceau(x)...\n")
        
        settings = self.client.get_download_settings(
            download_path,
            self.config.bitrate_code
        )
        
        success_count = 0
        error_count = 0
        
        for i, track_id in enumerate(track_ids, 1):
            print(f"[{i}/{len(track_ids)}] Traitement du morceau {track_id}...")
            
            try:
                # Création de l'objet de téléchargement
                download_obj = self.client.create_download_object(
                    track_id,
                    self.config.bitrate_code,
                    self.listener
                )
                
                # Gestion du cas où plusieurs objets sont retournés
                if not isinstance(download_obj, list):
                    download_obj = [download_obj]
                
                # Téléchargement
                for obj in download_obj:
                    self.client.download_track(obj, settings, self.listener)
                
                # Tagging du fichier téléchargé
                self._tag_newly_downloaded_file(download_path, track_id)
                
                success_count += 1
                
            except Exception as e:
                print(f"❌ Erreur sur la piste {track_id}: {e}")
                error_count += 1
        
        # Résumé
        print(f"\n📊 Résumé du téléchargement :")
        print(f"   ✅ Réussis : {success_count}")
        if error_count > 0:
            print(f"   ❌ Erreurs : {error_count}")
    
    def _tag_newly_downloaded_file(self, download_path: str, track_id: str):
        """
        Ajoute l'ID Deezer au fichier qui vient d'être téléchargé.
        
        Args:
            download_path: Dossier de téléchargement
            track_id: ID du morceau
        """
        try:
            # Recherche du fichier sans tag
            for filename in os.listdir(download_path):
                if not self.metadata_manager.is_audio_file(filename):
                    continue
                
                full_path = os.path.join(download_path, filename)
                existing_id = self.metadata_manager.get_id_from_tags(full_path)
                
                # Si le fichier n'a pas encore d'ID, on lui ajoute
                if existing_id is None:
                    self.metadata_manager.tag_file_with_id(full_path, track_id)
                    break
        except Exception as e:
            print(f"⚠️  Erreur lors du tagging : {e}")
