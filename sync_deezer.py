#!/usr/bin/env python3
"""
dsync - Synchroniseur de playlists Deezer

Point d'entrée principal pour la synchronisation de playlists Deezer.
Ce script charge la configuration et lance la synchronisation.

Usage:
    python3 sync_deezer.py <PLAYLIST_ID>

Example:
    python3 sync_deezer.py 1234567890
"""

import sys
from dsync.config import Config
from dsync.synchronizer import PlaylistSynchronizer


def main():
    """Point d'entrée principal du programme."""
    if len(sys.argv) < 2:
        print("❌ Erreur : ID de playlist manquant\n")
        print("Usage: python3 sync_deezer.py <PLAYLIST_ID>")
        print("\nExemple:")
        print("  python3 sync_deezer.py 1234567890")
        print("\nPour trouver l'ID d'une playlist :")
        print("  https://www.deezer.com/fr/playlist/1234567890")
        print("                                    ^^^^^^^^^^")
        sys.exit(1)
    
    playlist_id = sys.argv[1]
    
    # Validation de l'ID
    if not playlist_id.isdigit():
        print(f"❌ Erreur : '{playlist_id}' n'est pas un ID valide")
        print("L'ID de playlist doit être un nombre")
        sys.exit(1)
    
    try:
        # Chargement de la configuration
        config = Config()
        
        # Validation de la configuration
        if not config.validate():
            sys.exit(1)
        
        # Création du synchroniseur
        synchronizer = PlaylistSynchronizer(config)
        
        # Lancement de la synchronisation
        success = synchronizer.sync_playlist(playlist_id)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Synchronisation interrompue par l'utilisateur")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erreur inattendue : {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()