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
