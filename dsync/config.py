"""
Gestion de la configuration du projet.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any
import toml


class Config:
    """Gestionnaire de configuration pour dsync."""
    
    def __init__(self, config_path: str = None):
        """
        Initialise la configuration.
        
        Args:
            config_path: Chemin vers le fichier config.toml (optionnel)
        """
        if config_path is None:
            config_path = self._find_config_file()
        
        self.config_path = config_path
        self._data = self._load_config()
    
    def _find_config_file(self) -> str:
        """Trouve le fichier config.toml dans le répertoire du script."""
        # Cherche d'abord dans le répertoire courant
        current_dir = os.getcwd()
        config_path = os.path.join(current_dir, "config.toml")
        
        if os.path.exists(config_path):
            return config_path
        
        # Sinon, cherche dans le répertoire du module
        module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(module_dir, "config.toml")
        
        if os.path.exists(config_path):
            return config_path
        
        print(f"❌ Erreur : config.toml introuvable.")
        print(f"   Cherché dans : {current_dir} et {module_dir}")
        sys.exit(1)
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Charge le fichier de configuration TOML.
        
        Returns:
            Dictionnaire contenant la configuration
        """
        try:
            return toml.load(self.config_path)
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {self.config_path}: {e}")
            sys.exit(1)
    
    @property
    def deezer_arl(self) -> str:
        """Retourne le token ARL Deezer."""
        return self._data.get('deezer', {}).get('arl', '')
    
    @property
    def base_path(self) -> str:
        """Retourne le chemin de base pour le stockage."""
        return self._data.get('storage', {}).get('base_path', './downloads')
    
    @property
    def audio_format(self) -> str:
        """Retourne le format audio souhaité (FLAC, MP3_320, MP3_128)."""
        return self._data.get('storage', {}).get('format', 'MP3_320')
    
    @property
    def bitrate_code(self) -> int:
        """
        Convertit le format audio en code bitrate pour deemix.
        
        Returns:
            Code bitrate (9=FLAC, 3=MP3_320, 1=MP3_128)
        """
        bitrate_map = {
            "FLAC": 9,
            "MP3_320": 3,
            "MP3_128": 1
        }
        return bitrate_map.get(self.audio_format, 3)
    
    def validate(self) -> bool:
        """
        Valide la configuration.
        
        Returns:
            True si la configuration est valide
        """
        if not self.deezer_arl:
            print("❌ Erreur : Token ARL Deezer manquant dans config.toml")
            return False
        
        if not self.base_path:
            print("❌ Erreur : Chemin de stockage manquant dans config.toml")
            return False
        
        return True
