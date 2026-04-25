"""Gestionnaire de synchronisation - Fonctions utilitaires."""

import os
from typing import Dict
from dsync.config import Config
from dsync.synchronizer import PlaylistSynchronizer


def create_temp_config(arl: str, base_path: str, format_type: str) -> tuple[str, Config, PlaylistSynchronizer]:
    """
    Crée une configuration temporaire pour la synchronisation.
    
    Args:
        arl: Token ARL Deezer
        base_path: Chemin de base pour le téléchargement
        format_type: Format audio (FLAC, MP3_320, etc.)
    
    Returns:
        tuple: (config_path, config, synchronizer)
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Remonter de 2 niveaux (dsync_gui/services -> dsync_gui -> root)
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    config_path = os.path.join(root_dir, 'config.toml')
    
    config_content = f"""[deezer]
arl = "{arl.strip()}"

[storage]
base_path = "{base_path}"
format = "{format_type}"
"""
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
        f.flush()
        os.fsync(f.fileno())
    
    config = Config(config_path=config_path)
    synchronizer = PlaylistSynchronizer(config)
    
    return config_path, config, synchronizer


def sync_item(synchronizer: PlaylistSynchronizer, item_id: str, item_type: str) -> bool:
    """
    Synchronise un item (playlist ou album).
    
    Args:
        synchronizer: Instance de PlaylistSynchronizer
        item_id: ID de l'item
        item_type: "playlist" ou "album"
    
    Returns:
        bool: True si succès
    """
    if item_type == "playlist":
        return synchronizer.sync_playlist(item_id)
    else:
        return synchronizer.sync_album(item_id)
