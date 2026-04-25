"""
dsync GUI - Interface graphique modulaire pour la synchronisation Deezer

Ce package contient l'interface graphique refactorisée en modules :
- ui/ : Composants d'interface (AppBar, StatusBar, Collections, Dialogs)
- services/ : Services métier (Preferences, FileScanner, SyncManager)
- utils/ : Utilitaires (Helpers)
- main.py : Classe principale DsyncGUI
"""

from dsync_gui.main import DsyncGUI, main

__all__ = ['DsyncGUI', 'main']
