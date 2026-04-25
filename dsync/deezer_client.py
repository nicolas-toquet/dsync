"""
Client Deezer pour la récupération des playlists et des morceaux.
"""

import deemix
from typing import Set, Optional, Any
from .utils import find_class_in_package


class DeezerClient:
    """Client pour interagir avec l'API Deezer via deemix."""
    
    def __init__(self, arl_token: str):
        """
        Initialise le client Deezer.
        
        Args:
            arl_token: Token ARL pour l'authentification Deezer
        """
        self.arl_token = arl_token
        self._deezer_interface = None
        self._initialize_deemix_components()
    
    def _initialize_deemix_components(self):
        """Initialise les composants deemix via import dynamique."""
        self.DeezerInterface = find_class_in_package(deemix, 'Deezer')
        self.Downloader = find_class_in_package(deemix, 'Downloader')
        self.generateDownloadObject = find_class_in_package(deemix, 'generateDownloadObject')
        self.loadSettings = find_class_in_package(deemix, 'load')
        
        if not all([self.DeezerInterface, self.Downloader, 
                    self.generateDownloadObject, self.loadSettings]):
            raise ImportError("Impossible de charger les composants deemix requis")
    
    def connect(self) -> bool:
        """
        Se connecte à Deezer avec le token ARL.
        
        Returns:
            True si la connexion réussit
        """
        try:
            self._deezer_interface = self.DeezerInterface()
            self._deezer_interface.login_via_arl(self.arl_token)
            return True
        except Exception as e:
            print(f"❌ Erreur de connexion à Deezer : {e}")
            return False
    
    @property
    def interface(self):
        """Retourne l'interface Deezer."""
        if self._deezer_interface is None:
            raise RuntimeError("Client non connecté. Appelez connect() d'abord.")
        return self._deezer_interface
    
    def get_playlist_info(self, playlist_id: str) -> Optional[Any]:
        """
        Récupère les informations d'une playlist.
        
        Args:
            playlist_id: ID de la playlist Deezer
        
        Returns:
            Objet playlist ou None en cas d'erreur
        """
        try:
            return self.interface.api.get_playlist(playlist_id)
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de la playlist : {e}")
            return None
    
    def get_playlist_tracks(self, playlist_id: str) -> Set[str]:
        """
        Récupère les IDs de tous les morceaux d'une playlist.
        
        Args:
            playlist_id: ID de la playlist Deezer
        
        Returns:
            Ensemble des IDs de morceaux (sous forme de chaînes)
        """
        try:
            tracks = self.interface.api.get_playlist_tracks(playlist_id)
            
            if not tracks:
                print("⚠️  Aucun morceau trouvé dans la playlist")
                return set()
            
            return self._extract_track_ids(tracks)
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des morceaux : {e}")
            return set()
    
    def get_album_info(self, album_id: str) -> Optional[Any]:
        """
        Récupère les informations d'un album.
        
        Args:
            album_id: ID de l'album Deezer
        
        Returns:
            Objet album ou None en cas d'erreur
        """
        try:
            return self.interface.api.get_album(album_id)
        except Exception as e:
            print(f"❌ Erreur lors de la récupération de l'album : {e}")
            return None
    
    def get_user_playlists(self, user_id: Optional[str] = None) -> list:
        """
        Récupère toutes les playlists de l'utilisateur connecté ou d'un utilisateur spécifique.
        
        Args:
            user_id: ID de l'utilisateur (optionnel, sinon utilise l'utilisateur connecté)
        
        Returns:
            Liste de dictionnaires avec id, title et cover_url de chaque playlist
        """
        try:
            if not user_id:
                user_id = self.interface.current_user.get('id') if isinstance(self.interface.current_user, dict) else getattr(self.interface.current_user, 'id', None)
            
            if not user_id:
                print("❌ Impossible de récupérer l'ID de l'utilisateur")
                return []
            
            playlists_data = self.interface.api.get_user_playlists(user_id)
            playlists = []
            
            # Extraire les données selon le format
            items = playlists_data.get('data', []) if isinstance(playlists_data, dict) else playlists_data
            
            for playlist in items:
                playlist_id = str(playlist.get('id')) if isinstance(playlist, dict) else str(getattr(playlist, 'id', ''))
                title = playlist.get('title', f'Playlist {playlist_id}') if isinstance(playlist, dict) else getattr(playlist, 'title', f'Playlist {playlist_id}')
                cover_url = playlist.get('picture_medium', '') if isinstance(playlist, dict) else getattr(playlist, 'picture_medium', '')
                
                if playlist_id:
                    playlists.append({
                        'id': playlist_id,
                        'title': title,
                        'cover_url': cover_url,
                    })
            
            print(f"✅ {len(playlists)} playlists trouvées")
            return playlists
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des playlists utilisateur : {e}")
            return []
    
    def get_user_albums(self, user_id: Optional[str] = None) -> list:
        """
        Récupère tous les albums favoris de l'utilisateur connecté ou d'un utilisateur spécifique.
        
        Args:
            user_id: ID de l'utilisateur (optionnel, sinon utilise l'utilisateur connecté)
        
        Returns:
            Liste de dictionnaires avec id, title et cover_url de chaque album
        """
        try:
            if not user_id:
                user_id = self.interface.current_user.get('id') if isinstance(self.interface.current_user, dict) else getattr(self.interface.current_user, 'id', None)
            
            if not user_id:
                print("❌ Impossible de récupérer l'ID de l'utilisateur")
                return []
            
            albums_data = self.interface.api.get_user_albums(user_id)
            albums = []
            
            # Extraire les données selon le format
            items = albums_data.get('data', []) if isinstance(albums_data, dict) else albums_data
            
            for album in items:
                album_id = str(album.get('id')) if isinstance(album, dict) else str(getattr(album, 'id', ''))
                title = album.get('title', f'Album {album_id}') if isinstance(album, dict) else getattr(album, 'title', f'Album {album_id}')
                cover_url = album.get('cover_medium', '') if isinstance(album, dict) else getattr(album, 'cover_medium', '')
                
                if album_id:
                    albums.append({
                        'id': album_id,
                        'title': title,
                        'cover_url': cover_url,
                    })
            
            print(f"✅ {len(albums)} albums trouvés")
            return albums
            
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des albums utilisateur : {e}")
            return []
    
    def get_current_user_info(self) -> dict:
        """
        Récupère les informations de l'utilisateur actuellement connecté.
        
        Returns:
            Dictionnaire avec id et name de l'utilisateur
        """
        try:
            user_data = self.interface.current_user
            user_id = user_data.get('id') if isinstance(user_data, dict) else getattr(user_data, 'id', None)
            user_name = user_data.get('name', 'Utilisateur') if isinstance(user_data, dict) else getattr(user_data, 'name', 'Utilisateur')
            
            return {
                'id': str(user_id) if user_id else '',
                'name': user_name,
            }
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des infos utilisateur : {e}")
            return {'id': '', 'name': 'Utilisateur'}
    
    def get_album_tracks(self, album_id: str) -> Set[str]:
        """
        Récupère les IDs de tous les morceaux d'un album.
        
        Args:
            album_id: ID de l'album Deezer
        
        Returns:
            Ensemble des IDs de morceaux (sous forme de chaînes)
        """
        try:
            album_info = self.interface.api.get_album(album_id)
            
            if not album_info:
                print("⚠️  Album non trouvé")
                return set()
            
            # Les tracks d'un album sont dans album_info['tracks'] ou album_info.tracks
            tracks = album_info.get('tracks', {}).get('data', []) if isinstance(album_info, dict) else getattr(album_info, 'tracks', {}).get('data', [])
            
            if not tracks:
                print("⚠️  Aucun morceau trouvé dans l'album")
                return set()
            
            return self._extract_track_ids(tracks)
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des morceaux de l'album : {e}")
            return set()
    
    def _extract_track_ids(self, tracks: Any) -> Set[str]:
        """
        Extrait les IDs des morceaux depuis la réponse de l'API.
        
        Args:
            tracks: Données de morceaux de l'API
        
        Returns:
            Ensemble des IDs de morceaux valides
        """
        track_ids = set()
        
        # Si tracks est un dict avec une clé 'data', on l'extrait
        actual_tracks = tracks.get('data', tracks) if isinstance(tracks, dict) else tracks
        
        for track in actual_tracks:
            track_id = self._get_track_id(track)
            if track_id and track_id.isdigit():
                track_ids.add(track_id)
        
        return track_ids
    
    def _get_track_id(self, track: Any) -> Optional[str]:
        """
        Extrait l'ID d'un morceau depuis différents formats.
        
        Args:
            track: Morceau (objet, dict, ou ID direct)
        
        Returns:
            L'ID sous forme de chaîne, ou None
        """
        if hasattr(track, 'id'):
            return str(track.id)
        elif isinstance(track, dict):
            return str(track.get('id', ''))
        else:
            return str(track)
    
    def get_download_settings(self, download_path: str, bitrate_code: int) -> dict:
        """
        Génère les paramètres de téléchargement pour deemix.
        
        Args:
            download_path: Chemin de destination
            bitrate_code: Code de qualité (9=FLAC, 3=MP3_320, 1=MP3_128)
        
        Returns:
            Dictionnaire de paramètres
        """
        settings = self.loadSettings()
        settings['downloadLocation'] = download_path
        settings['createPlaylistFolder'] = False
        settings['tracknameTemplate'] = "%artist% - %title%"
        settings['fallbackBitrate'] = True
        
        return settings
    
    def create_download_object(self, track_id: str, bitrate: int, listener: Any):
        """
        Crée un objet de téléchargement pour un morceau.
        
        Args:
            track_id: ID du morceau Deezer
            bitrate: Code de qualité audio
            listener: Écouteur de logs
        
        Returns:
            Objet(s) de téléchargement
        """
        url = f"https://www.deezer.com/track/{track_id}"
        return self.generateDownloadObject(self.interface, url, bitrate, {}, listener)
    
    def download_track(self, download_object: Any, settings: dict, listener: Any):
        """
        Télécharge un morceau.
        
        Args:
            download_object: Objet de téléchargement
            settings: Paramètres de téléchargement
            listener: Écouteur de logs
        """
        self.Downloader(self.interface, download_object, settings, listener).start()
