"""
Utilitaires divers pour dsync.
"""

import pkgutil
from typing import Any, Optional


class LogListener:
    """Écouteur de logs pour les événements de téléchargement."""
    
    @classmethod
    def send(cls, key: str, value: Optional[dict] = None):
        """
        Affiche les messages de log formatés.
        
        Args:
            key: Type de message (info, downloading, finished, etc.)
            value: Données associées au message
        """
        if key == 'info':
            print(f"ℹ️  {value}")
        elif key == 'downloading':
            if value and isinstance(value, dict):
                title = value.get('title', 'Inconnu')
                print(f"📥 Téléchargement : {title}")
        elif key == 'finished':
            if value and isinstance(value, dict):
                title = value.get('title', 'Inconnu')
                print(f"✅ Terminé : {title}")
        elif key == 'error':
            if value and isinstance(value, dict):
                message = value.get('message', 'Erreur inconnue')
                print(f"❌ Erreur : {message}")


def find_class_in_package(package: Any, class_name: str) -> Optional[type]:
    """
    Recherche dynamique d'une classe dans un package Python.
    
    Cette fonction parcourt récursivement tous les modules d'un package
    pour trouver une classe par son nom. Utile pour s'adapter aux
    différentes versions de bibliothèques tierces.
    
    Args:
        package: Le package Python à explorer
        class_name: Nom de la classe à trouver
    
    Returns:
        La classe trouvée, ou None si introuvable
    
    Example:
        >>> import requests
        >>> Session = find_class_in_package(requests, 'Session')
    """
    for loader, name, is_pkg in pkgutil.walk_packages(
        package.__path__, 
        package.__name__ + "."
    ):
        try:
            module = __import__(name, fromlist=[class_name])
            if hasattr(module, class_name):
                return getattr(module, class_name)
        except (ImportError, AttributeError):
            continue
    return None


def format_track_info(track: Any) -> str:
    """
    Formate les informations d'un morceau pour l'affichage.
    
    Args:
        track: Objet ou dictionnaire contenant les infos du morceau
    
    Returns:
        Chaîne formatée avec artiste et titre
    """
    if isinstance(track, dict):
        artist = track.get('artist', {}).get('name', 'Artiste inconnu')
        title = track.get('title', 'Titre inconnu')
    else:
        artist = getattr(track, 'artist', {}).get('name', 'Artiste inconnu') if hasattr(track, 'artist') else 'Artiste inconnu'
        title = getattr(track, 'title', 'Titre inconnu') if hasattr(track, 'title') else 'Titre inconnu'
    
    return f"{artist} - {title}"
