"""Gestionnaire de scan des dossiers et parsing."""

import os
import json
from typing import Dict, List, Optional


def scan_existing_items(base_path: str, profile_folder: str) -> tuple[List[Dict], List[Dict]]:
    """
    Scanne les dossiers Playlists/ et Albums/ pour découvrir les items existants.
    
    Returns:
        tuple: (playlists, albums) - deux listes de dictionnaires
    """
    playlists = []
    albums = []
    
    # Si un profil est sélectionné, scanner son dossier spécifique
    if profile_folder:
        base_path = os.path.join(base_path, profile_folder)
    
    # Scanner les playlists
    playlists_path = os.path.join(base_path, 'Playlists')
    if os.path.exists(playlists_path):
        for folder_name in os.listdir(playlists_path):
            folder_path = os.path.join(playlists_path, folder_name)
            if os.path.isdir(folder_path):
                item_info = parse_folder_name(folder_name, folder_path)
                if item_info:
                    # Vérifier si pas déjà dans la liste
                    if not any(p['id'] == item_info['id'] for p in playlists):
                        playlists.append(item_info)
    
    # Scanner les albums
    albums_path = os.path.join(base_path, 'Albums')
    if os.path.exists(albums_path):
        for folder_name in os.listdir(albums_path):
            folder_path = os.path.join(albums_path, folder_name)
            if os.path.isdir(folder_path):
                item_info = parse_folder_name(folder_name, folder_path)
                if item_info:
                    # Vérifier si pas déjà dans la liste
                    if not any(a['id'] == item_info['id'] for a in albums):
                        albums.append(item_info)
    
    return playlists, albums


def parse_folder_name(folder_name: str, folder_path: str) -> Optional[Dict]:
    """
    Parse un nom de dossier et récupère les informations depuis le fichier .info
    
    Args:
        folder_name: Nom du dossier (ex: "15179529003 - Titre")
        folder_path: Chemin complet du dossier
    
    Returns:
        Dict avec id, title, cover_url ou None si invalide
    """
    try:
        # Nouveau format : uniquement l'ID comme nom de dossier
        # Les informations sont dans le fichier .info
        info_file = os.path.join(folder_path, '.info')
        
        if os.path.exists(info_file):
            # Lire les métadonnées depuis le fichier .info
            with open(info_file, 'r', encoding='utf-8') as f:
                info_data = json.load(f)
                item_id = info_data.get('id', folder_name)
                title = info_data.get('title', f"Item {item_id}")
        else:
            # Ancien format : "[ID] - [Titre]" (rétrocompatibilité)
            if ' - ' in folder_name:
                parts = folder_name.split(' - ', 1)
                item_id = parts[0].strip()
                title = parts[1].strip() if len(parts) > 1 else f"Item {item_id}"
            else:
                # Dossier avec uniquement l'ID mais pas de fichier .info
                item_id = folder_name.strip()
                title = f"Item {item_id}"
            
            # Vérifier que l'ID est bien numérique
            if not item_id.isdigit():
                return None
        
        # Chercher la pochette locale
        cover_url = ''
        cover_file = os.path.join(folder_path, 'cover.jpg')
        if os.path.exists(cover_file):
            cover_url = cover_file
        
        return {
            'id': item_id,
            'title': title,
            'cover_url': cover_url,
        }
    except Exception as e:
        print(f"Erreur lors du parsing de '{folder_name}': {e}")
        return None
