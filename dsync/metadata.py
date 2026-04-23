"""
Gestion des métadonnées audio (tags ID3 et FLAC).
"""

from pathlib import Path
from typing import Optional
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from mutagen.mp3 import MP3


class MetadataManager:
    """Gestionnaire de métadonnées pour les fichiers audio."""
    
    @staticmethod
    def tag_file_with_id(filepath: str, track_id: str) -> bool:
        """
        Enregistre l'ID Deezer dans les métadonnées du fichier audio.
        
        Args:
            filepath: Chemin vers le fichier audio
            track_id: ID Deezer du morceau
        
        Returns:
            True si le tag a été ajouté avec succès, False sinon
        """
        try:
            if filepath.endswith('.mp3'):
                audio = EasyID3(filepath)
                audio['website'] = str(track_id)
                audio.save()
            elif filepath.endswith('.flac'):
                audio = FLAC(filepath)
                audio['deezer_id'] = str(track_id)
                audio.save()
            else:
                print(f"⚠️  Format non supporté : {filepath}")
                return False
            return True
        except Exception as e:
            print(f"⚠️  Erreur lors du tagging de {filepath}: {e}")
            return False
    
    @staticmethod
    def get_id_from_tags(filepath: str) -> Optional[str]:
        """
        Lit l'ID Deezer depuis les métadonnées du fichier audio.
        
        Args:
            filepath: Chemin vers le fichier audio
        
        Returns:
            L'ID Deezer si trouvé, None sinon
        """
        try:
            if filepath.endswith('.mp3'):
                audio = EasyID3(filepath)
                website = audio.get('website', [None])
                return website[0] if website else None
            elif filepath.endswith('.flac'):
                audio = FLAC(filepath)
                deezer_id = audio.get('deezer_id', [None])
                return deezer_id[0] if deezer_id else None
        except Exception:
            return None
        
        return None
    
    @staticmethod
    def is_audio_file(filepath: str) -> bool:
        """
        Vérifie si un fichier est un fichier audio supporté.
        
        Args:
            filepath: Chemin vers le fichier
        
        Returns:
            True si c'est un fichier audio supporté
        """
        return filepath.endswith(('.mp3', '.flac'))
    
    @staticmethod
    def get_track_id_from_filename(filename: str) -> Optional[str]:
        """
        Extrait l'ID du morceau depuis le nom de fichier (méthode de fallback).
        
        Format attendu : "TRACK_ID - Artist - Title.ext"
        
        Args:
            filename: Nom du fichier
        
        Returns:
            L'ID si trouvé et valide, None sinon
        """
        try:
            # Essaie d'extraire l'ID depuis le début du nom de fichier
            parts = filename.split(' - ')
            if parts and parts[0].isdigit():
                return parts[0]
        except Exception:
            pass
        
        return None
