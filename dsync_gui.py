#!/usr/bin/env python3
"""
dsync GUI - Point d'entrée pour l'interface graphique

Ce fichier sert de point d'entrée pour lancer l'application graphique refactorisée.
L'implémentation réelle se trouve dans le package dsync_gui/.

Usage:
    python dsync_gui.py
    ou
    python3 dsync_gui.py
"""

import flet as ft
from dsync_gui.main import main

if __name__ == "__main__":
    print("🚀 Lancement de dsync GUI (version modulaire)...")
    ft.run(main)
