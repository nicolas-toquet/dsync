"""
dsync - Synchroniseur de playlists Deezer
"""

__version__ = "1.0.0"
__author__ = "dsync"

from .synchronizer import PlaylistSynchronizer
from .config import Config

__all__ = ["PlaylistSynchronizer", "Config"]
