"""Gestion des préférences utilisateur."""

import os
import json
from pathlib import Path
from typing import Dict

PREFS_FILE = "dsync_preferences.json"


def load_preferences() -> Dict:
    """Charge les préférences sauvegardées."""
    if os.path.exists(PREFS_FILE):
        try:
            with open(PREFS_FILE, 'r') as f:
                prefs = json.load(f)
                # S'assurer que la liste des profils existe
                if 'profiles' not in prefs:
                    prefs['profiles'] = [{'name': 'Défaut', 'deezer_id': ''}]
                else:
                    # Convertir l'ancien format si nécessaire (rétrocompatibilité)
                    if prefs['profiles'] and isinstance(prefs['profiles'][0], str):
                        prefs['profiles'] = [{'name': p, 'deezer_id': ''} for p in prefs['profiles']]
                
                if 'current_profile_name' not in prefs:
                    prefs['current_profile_name'] = 'Défaut'
                
                if 'dark_mode' not in prefs:
                    prefs['dark_mode'] = False
                
                return prefs
        except:
            pass
    return {
        'arl': '',
        'base_path': str(Path.home() / 'Music' / 'Deezer'),
        'format': 'MP3_320',
        'profiles': [{'name': 'Défaut', 'deezer_id': ''}],
        'current_profile_name': 'Défaut',
        'dark_mode': False,
    }


def save_preferences(prefs: Dict, arl_field=None, path_field=None, format_dropdown=None, is_dark_mode=False):
    """Sauvegarde les préférences."""
    # Les champs sont maintenant dans les dialogs, donc on ne les met à jour que s'ils existent
    if arl_field:
        prefs['arl'] = arl_field.value
    if path_field:
        prefs['base_path'] = path_field.value
    if format_dropdown:
        prefs['format'] = format_dropdown.value
    
    prefs['dark_mode'] = is_dark_mode
    
    try:
        with open(PREFS_FILE, 'w') as f:
            json.dump(prefs, f, indent=2)
    except Exception as e:
        print(f"Erreur lors de la sauvegarde : {e}")


def get_profile_base_path(prefs: Dict) -> str:
    """Retourne le chemin de base incluant le dossier du profil actuel."""
    base_path = prefs.get('base_path', str(Path.home() / 'Music' / 'Deezer'))
    profile_folder = prefs.get('current_profile_folder', '')
    
    if profile_folder:
        return os.path.join(base_path, profile_folder)
    
    return base_path
