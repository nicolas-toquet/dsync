#!/usr/bin/env python3
"""
dsync GUI - Interface graphique pour la synchronisation de playlists Deezer

Application standalone avec interface moderne - Version modulaire refactorisée.
"""

import flet as ft
import os
import json
import threading
import asyncio
from pathlib import Path
from typing import Dict, List, Optional

from dsync.config import Config
from dsync.synchronizer import PlaylistSynchronizer

# Imports des modules dsync_gui
from dsync_gui.utils.helpers import show_snackbar, force_ui_update
from dsync_gui.services import preferences, file_scanner, sync_manager
from dsync_gui.ui import app_bar, status_bar, collections, dialogs


class DsyncGUI:
    """Interface graphique principale pour dsync."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "dsync - Synchronisation Deezer"
        self.page.window.min_width = 1000
        self.page.window.min_height = 700
        self.page.window.maximized = True
        
        # État
        self.playlists: List[Dict] = []
        self.albums: List[Dict] = []
        self.is_syncing = False
        
        # Préférences
        self.prefs = preferences.load_preferences()
        self.is_dark_mode = self.prefs.get('dark_mode', False)
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        
        # Références pour les composants UI qui seront créés dynamiquement dans les dialogues
        self.format_dropdown = None
        self.path_field = None
        self.arl_field = None
        
        # Références pour la barre de statut
        self.progress_bar_ref = ft.Ref[ft.ProgressBar]()
        self.status_text_ref = ft.Ref[ft.Text]()
        
        # FilePicker pour sélection de dossier
        self.folder_picker = ft.FilePicker()
        self.folder_picker.on_result = self.on_folder_selected
        
        # Scanner les items existants
        self.scan_existing_items()
        
        # Construire l'interface
        self.build_ui()
        
        # Ajouter le FilePicker aux services
        self.page.services.append(self.folder_picker)
        self.page.update()
        
        # Vérifier la configuration au premier lancement
        self.check_initial_configuration()
    
    @property
    def progress_bar(self):
        """Accès facile à la progress_bar."""
        return self.progress_bar_ref.current
    
    @property
    def status_text(self):
        """Accès facile au status_text."""
        return self.status_text_ref.current
    
    def scan_existing_items(self):
        """Scanne les dossiers Playlists/ et Albums/ pour découvrir les items existants."""
        base_path = self.prefs.get('base_path', str(Path.home() / 'Music' / 'Deezer'))
        profile_folder = self.prefs.get('current_profile_folder', '')
        
        self.playlists, self.albums = file_scanner.scan_existing_items(base_path, profile_folder)
    
    def get_profile_base_path(self) -> str:
        """Retourne le chemin de base incluant le dossier du profil actuel."""
        return preferences.get_profile_base_path(self.prefs)
    
    def save_preferences(self):
        """Sauvegarde les préférences."""
        preferences.save_preferences(
            self.prefs,
            self.arl_field,
            self.path_field,
            self.format_dropdown,
            self.is_dark_mode
        )
    
    def force_ui_update(self):
        """Force la mise à jour de l'interface utilisateur."""
        force_ui_update(self.page)
    
    def show_snackbar(self, message: str, bgcolor: str):
        """Affiche un snackbar."""
        show_snackbar(self.page, message, bgcolor)
    
    def toggle_theme(self, e):
        """Bascule entre mode clair et sombre."""
        self.is_dark_mode = not self.is_dark_mode
        self.page.theme_mode = ft.ThemeMode.DARK if self.is_dark_mode else ft.ThemeMode.LIGHT
        self.prefs['dark_mode'] = self.is_dark_mode
        self.save_preferences()
        self.force_ui_update()
    
    def build_ui(self):
        """Construit l'interface utilisateur principale."""
        # AppBar avec boutons
        current_profile_name = self.prefs.get('current_profile_name', 'Défaut')
        appbar = app_bar.build_app_bar(
            current_profile_name,
            self.toggle_theme,
            self.open_profiles_drawer,
            self.open_settings_drawer,
        )
        
        # Zone principale avec les collections
        main_content = ft.Container(
            content=self.build_collections_panel(),
            expand=True,
            padding=20,
        )
        
        # Bouton flottant pour synchroniser tout
        fab = app_bar.build_fab(lambda e: self.start_sync_all())
        
        # Barre de statut
        status_bar_widget = status_bar.build_status_bar(
            self.progress_bar_ref,
            self.status_text_ref,
        )
        
        # Layout principal
        self.page.appbar = appbar
        self.page.floating_action_button = fab
        
        self.page.add(
            ft.Column(
                [
                    main_content,
                    status_bar_widget,
                ],
                spacing=0,
                expand=True,
            )
        )
    
    def update_appbar(self):
        """Met à jour l'AppBar avec le nom du profil actuel."""
        current_profile_name = self.prefs.get('current_profile_name', 'Défaut')
        self.page.appbar = app_bar.build_app_bar(
            current_profile_name,
            self.toggle_theme,
            self.open_profiles_drawer,
            self.open_settings_drawer,
        )
        self.page.update()
    
    def build_collections_panel(self) -> ft.Column:
        """Construit le panneau des collections."""
        # Créer les grilles
        self.playlists_grid = ft.GridView(
            expand=True,
            runs_count=6,
            max_extent=180,
            child_aspect_ratio=0.75,
            spacing=15,
            run_spacing=15,
        )
        
        self.albums_grid = ft.GridView(
            expand=True,
            runs_count=6,
            max_extent=180,
            child_aspect_ratio=0.75,
            spacing=15,
            run_spacing=15,
        )
        
        return collections.build_collections_panel(
            self.playlists_grid,
            self.albums_grid,
            lambda e: self.import_user_playlists(),
            lambda e: self.import_user_albums(),
            lambda e: self.show_add_dialog("playlist"),
            lambda e: self.show_add_dialog("album"),
            self.refresh_playlists,
            self.refresh_albums,
        )
    
    def refresh_playlists(self):
        """Rafraîchit l'affichage des playlists."""
        self.playlists_grid.controls.clear()
        
        for playlist in self.playlists:
            card = collections.build_item_card(
                playlist,
                "playlist",
                self.sync_single_item,
                self.show_item_details,
                self.remove_item,
                self.page,
                self.fetch_cover_url,
            )
            self.playlists_grid.controls.append(card)
        
        self.page.update()
    
    def refresh_albums(self):
        """Rafraîchit l'affichage des albums."""
        self.albums_grid.controls.clear()
        
        for album in self.albums:
            card = collections.build_item_card(
                album,
                "album",
                self.sync_single_item,
                self.show_item_details,
                self.remove_item,
                self.page,
                self.fetch_cover_url,
            )
            self.albums_grid.controls.append(card)
        
        self.page.update()
    
    # ========== Gestion des dialogues ==========
    
    def check_initial_configuration(self):
        """Vérifie que l'ARL et le chemin de téléchargement sont configurés au premier lancement."""
        arl = self.prefs.get('arl', '').strip()
        base_path = self.prefs.get('base_path', '').strip()
        
        if not arl or not base_path:
            welcome_dialog = dialogs.build_welcome_dialog(
                lambda e: self.close_welcome_and_open_settings(welcome_dialog)
            )
            self.page.overlay.append(welcome_dialog)
            welcome_dialog.open = True
            self.page.update()
    
    def close_welcome_and_open_settings(self, welcome_dialog):
        """Ferme le dialogue d'accueil et ouvre les paramètres."""
        welcome_dialog.open = False
        self.page.update()
        self.open_settings_drawer(None)
    
    def open_settings_drawer(self, e):
        """Ouvre le panneau des paramètres."""
        # Créer des références pour les champs
        format_dropdown_ref = ft.Ref[ft.Dropdown]()
        path_field_ref = ft.Ref[ft.TextField]()
        arl_field_ref = ft.Ref[ft.TextField]()
        
        dialog = dialogs.build_settings_dialog(
            self.prefs,
            self.is_dark_mode,
            self.close_settings_drawer,
            self.pick_folder,
            format_dropdown_ref,
            path_field_ref,
            arl_field_ref,
        )
        
        # Stocker les références
        self.format_dropdown = format_dropdown_ref.current
        self.path_field = path_field_ref.current
        self.arl_field = arl_field_ref.current
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_settings_drawer(self, e):
        """Ferme le panneau des paramètres après validation."""
        # Vérifier que les champs obligatoires sont remplis
        arl = self.prefs.get('arl', '').strip()
        base_path = self.prefs.get('base_path', '').strip()
        
        if not arl or not base_path:
            self.show_snackbar("❌ Veuillez remplir l'ARL et le chemin de téléchargement", ft.Colors.RED_400)
            return
        
        self.save_preferences()
        self.close_current_dialog(e)
    
    def open_profiles_drawer(self, e):
        """Ouvre le panneau des profils."""
        dialog = dialogs.build_profiles_dialog(
            self.prefs,
            self.switch_to_profile_from_dialog,
            lambda e: self.show_add_profile_dialog(),
            lambda e: self.delete_current_profile(),
            self.close_profiles_drawer,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_profiles_drawer(self, e):
        """Ferme le panneau des profils."""
        self.close_current_dialog(e)
    
    def close_current_dialog(self, e):
        """Ferme le dialogue actuellement ouvert."""
        for overlay in self.page.overlay:
            if isinstance(overlay, ft.AlertDialog) and overlay.open:
                overlay.open = False
        self.page.update()
    
    def close_all_dialogs(self):
        """Ferme et nettoie tous les dialogues ouverts."""
        # D'abord fermer tous les dialogues
        for overlay in self.page.overlay[:]:  # Copie de la liste pour éviter les modifications pendant l'itération
            if isinstance(overlay, ft.AlertDialog):
                overlay.open = False
        
        # Ensuite vider l'overlay
        self.page.overlay.clear()
        self.page.update()
    
    def show_add_profile_dialog(self):
        """Affiche le dialogue pour ajouter un nouveau profil."""
        name_field_ref = ft.Ref[ft.TextField]()
        deezer_id_field_ref = ft.Ref[ft.TextField]()
        
        def add_profile(e):
            name = name_field_ref.current.value.strip()
            deezer_id = deezer_id_field_ref.current.value.strip()
            
            if not name:
                self.show_snackbar("❌ Le nom du profil est obligatoire", ft.Colors.RED_400)
                return
            
            # Ajouter le profil
            profiles = self.prefs.get('profiles', [])
            profiles.append({'name': name, 'deezer_id': deezer_id})
            self.prefs['profiles'] = profiles
            
            # Définir ce nouveau profil comme profil actif
            self.prefs['current_profile_name'] = name
            self.prefs['current_profile_folder'] = name
            self.save_preferences()
            
            # Recharger les items pour le nouveau profil
            self.playlists.clear()
            self.albums.clear()
            self.scan_existing_items()
            self.refresh_playlists()
            self.refresh_albums()
            
            # Mettre à jour l'AppBar avec le nouveau nom de profil
            self.update_appbar()
            
            # Fermer TOUS les dialogues - NE PAS ROUVRIR
            self.close_all_dialogs()
            
            self.show_snackbar(f"✅ Profil '{name}' créé et activé !", ft.Colors.GREEN_400)
        
        dialog = dialogs.build_add_profile_dialog(
            add_profile,
            lambda e: self.close_dialog(dialog),
            name_field_ref,
            deezer_id_field_ref,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def delete_current_profile(self):
        """Supprime le profil actuellement sélectionné."""
        current_profile = self.prefs.get('current_profile_name', 'Défaut')
        profiles = self.prefs.get('profiles', [])
        
        if len(profiles) <= 1:
            self.show_snackbar("❌ Impossible de supprimer le dernier profil", ft.Colors.RED_400)
            return
        
        if current_profile == 'Défaut':
            self.show_snackbar("❌ Impossible de supprimer le profil par défaut", ft.Colors.RED_400)
            return
        
        # Supprimer le profil
        self.prefs['profiles'] = [p for p in profiles if p['name'] != current_profile]
        
        # Basculer vers le premier profil
        self.prefs['current_profile_name'] = self.prefs['profiles'][0]['name']
        self.prefs['current_profile_folder'] = self.prefs['profiles'][0]['name']
        self.save_preferences()
        
        # Recharger
        self.playlists.clear()
        self.albums.clear()
        self.scan_existing_items()
        self.refresh_playlists()
        self.refresh_albums()
        
        # Mettre à jour l'AppBar
        self.update_appbar()
        
        # Fermer tous les dialogues - NE PAS ROUVRIR
        self.close_all_dialogs()
        
        self.show_snackbar(f"✅ Profil '{current_profile}' supprimé", ft.Colors.GREEN_400)
    
    def switch_to_profile_from_dialog(self, profile_name: str):
        """Change de profil depuis le dialog et ferme le dialog."""
        self.prefs['current_profile_name'] = profile_name
        self.prefs['current_profile_folder'] = profile_name
        self.save_preferences()
        
        # Vider et recharger
        self.playlists.clear()
        self.albums.clear()
        self.scan_existing_items()
        
        # Rafraîchir l'affichage
        self.refresh_playlists()
        self.refresh_albums()
        
        # Mettre à jour l'AppBar avec le nouveau nom de profil
        self.update_appbar()
        
        # Fermer tous les dialogues proprement
        self.close_all_dialogs()
        
        self.show_snackbar(f"✅ Profil changé vers: {profile_name}", ft.Colors.GREEN_400)
        self.force_ui_update()
    
    def show_add_dialog(self, item_type: str):
        """Affiche la boîte de dialogue pour ajouter un item."""
        id_field_ref = ft.Ref[ft.TextField]()
        
        async def add_item(e):
            item_id = id_field_ref.current.value.strip()
            if not item_id or not item_id.isdigit():
                self.show_snackbar("❌ ID invalide", ft.Colors.RED_400)
                return
            
            dialog.open = False
            self.page.update()
            
            # Récupérer les métadonnées
            await self.fetch_and_add_item(item_id, item_type)
        
        dialog = dialogs.build_add_item_dialog(
            item_type,
            add_item,
            lambda e: self.close_dialog(dialog),
            id_field_ref,
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def close_dialog(self, dialog):
        """Ferme une boîte de dialogue."""
        dialog.open = False
        self.page.update()
    
    # ========== Opérations Deezer ==========
    
    async def fetch_and_add_item(self, item_id: str, item_type: str):
        """Récupère les métadonnées et ajoute l'item."""
        self.show_snackbar(f"🔍 Récupération des informations...", ft.Colors.BLUE_400)
        
        try:
            # Créer une config temporaire
            _, config, synchronizer = sync_manager.create_temp_config(
                self.prefs.get('arl', '').strip(),
                self.prefs.get('base_path', ''),
                self.prefs.get('format', 'MP3_320')
            )
            
            # Se connecter
            if not synchronizer.client.connect():
                self.show_snackbar(f"❌ Impossible de se connecter à Deezer", ft.Colors.RED_400)
                return
            
            # Récupérer les infos
            if item_type == "playlist":
                info = synchronizer.client.get_playlist_info(item_id)
                if info:
                    item = {
                        'id': item_id,
                        'title': info.get('title', f'Playlist {item_id}') if isinstance(info, dict) else getattr(info, 'title', f'Playlist {item_id}'),
                        'cover_url': info.get('picture_medium', '') if isinstance(info, dict) else getattr(info, 'picture_medium', ''),
                    }
                    
                    # Créer le dossier
                    base_path = self.get_profile_base_path()
                    category_path = os.path.join(base_path, "Playlists")
                    os.makedirs(category_path, exist_ok=True)
                    folder_name = f"{item['id']} - {item['title']}"
                    folder_path = os.path.join(category_path, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    
                    # Créer le fichier .info
                    info_file = os.path.join(folder_path, '.info')
                    with open(info_file, 'w', encoding='utf-8') as f:
                        json.dump({'id': item['id'], 'title': item['title'], 'type': 'playlist'}, f, indent=2)
                    
                    self.playlists.append(item)
                    self.refresh_playlists()
                    self.show_snackbar(f"✅ Playlist ajoutée ! Synchronisation...", ft.Colors.GREEN_400)
                    
                    # Lancer la synchro automatiquement
                    self.sync_single_item(item, item_type)
                else:
                    self.show_snackbar(f"❌ Playlist introuvable", ft.Colors.RED_400)
            else:  # album
                info = synchronizer.client.get_album_info(item_id)
                if info:
                    item = {
                        'id': item_id,
                        'title': info.get('title', f'Album {item_id}') if isinstance(info, dict) else getattr(info, 'title', f'Album {item_id}'),
                        'cover_url': info.get('cover_medium', '') if isinstance(info, dict) else getattr(info, 'cover_medium', ''),
                    }
                    
                    # Créer le dossier
                    base_path = self.get_profile_base_path()
                    category_path = os.path.join(base_path, "Albums")
                    os.makedirs(category_path, exist_ok=True)
                    folder_name = f"{item['id']} - {item['title']}"
                    folder_path = os.path.join(category_path, folder_name)
                    os.makedirs(folder_path, exist_ok=True)
                    
                    # Créer le fichier .info
                    info_file = os.path.join(folder_path, '.info')
                    with open(info_file, 'w', encoding='utf-8') as f:
                        json.dump({'id': item['id'], 'title': item['title'], 'type': 'album'}, f, indent=2)
                    
                    self.albums.append(item)
                    self.refresh_albums()
                    self.show_snackbar(f"✅ Album ajouté ! Synchronisation...", ft.Colors.GREEN_400)
                    
                    # Lancer la synchro automatiquement
                    self.sync_single_item(item, item_type)
                else:
                    self.show_snackbar(f"❌ Album introuvable", ft.Colors.RED_400)
                    
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"❌ Erreur : {str(e)}", ft.Colors.RED_400)
    
    async def fetch_cover_url(self, item_id: str, item_type: str) -> str:
        """Récupère l'URL de la pochette depuis Deezer ou le fichier local."""
        try:
            # D'abord vérifier si une pochette locale existe
            base_path = self.get_profile_base_path()
            category = "Playlists" if item_type == "playlist" else "Albums"
            
            # Chercher le dossier correspondant à l'item
            category_path = os.path.join(base_path, category)
            if os.path.exists(category_path):
                for folder_name in os.listdir(category_path):
                    if folder_name.startswith(f"{item_id} - "):
                        cover_file = os.path.join(category_path, folder_name, "cover.jpg")
                        if os.path.exists(cover_file):
                            return cover_file
            
            # Si pas de pochette locale, récupérer depuis Deezer
            _, config, synchronizer = sync_manager.create_temp_config(
                self.prefs.get('arl', '').strip(),
                self.prefs.get('base_path', ''),
                self.prefs.get('format', 'MP3_320')
            )
            
            if not synchronizer.client.connect():
                return ''
            
            if item_type == "playlist":
                info = synchronizer.client.get_playlist_info(item_id)
                cover_url = info.get('picture_medium', '') if isinstance(info, dict) else getattr(info, 'picture_medium', '')
            else:
                info = synchronizer.client.get_album_info(item_id)
                cover_url = info.get('cover_medium', '') if isinstance(info, dict) else getattr(info, 'cover_medium', '')
            
            return cover_url if cover_url else ''
            
        except Exception as e:
            print(f"Erreur lors de la récupération de la pochette pour {item_id}: {e}")
            return ''
    
    async def pick_folder(self, e):
        """Ouvre le sélecteur de dossier."""
        try:
            asyncio.create_task(
                self.folder_picker.get_directory_path(
                    dialog_title="Sélectionner le dossier de téléchargement"
                )
            )
        except Exception as ex:
            print(f"Erreur FilePicker: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"❌ Erreur lors de l'ouverture : {str(ex)}", ft.Colors.RED_400)
    
    def on_folder_selected(self, e):
        """Callback appelé quand un dossier est sélectionné."""
        try:
            if e.path:
                folder_path = e.path
                self.prefs['base_path'] = folder_path
                self.save_preferences()
                
                if hasattr(self, 'path_field') and self.path_field:
                    self.path_field.value = folder_path
                
                self.force_ui_update()
                self.show_snackbar(f"✅ Dossier sélectionné : {folder_path}", ft.Colors.GREEN_400)
        except Exception as ex:
            print(f"Erreur lors de la sélection: {ex}")
            import traceback
            traceback.print_exc()
            self.show_snackbar(f"❌ Erreur lors de la sélection : {str(ex)}", ft.Colors.RED_400)
    
    # ========== Importation depuis Deezer ==========
    
    def import_user_playlists(self):
        """Importe les playlists de l'utilisateur depuis Deezer."""
        self.show_import_dialog("playlist")
    
    def import_user_albums(self):
        """Importe les albums de l'utilisateur depuis Deezer."""
        self.show_import_dialog("album")
    
    def show_import_dialog(self, item_type: str):
        """Affiche le dialogue d'importation avec liste de sélection."""
        # TODO: Implémenter le dialogue d'importation complet
        # Pour l'instant, afficher un message
        self.show_snackbar("🚧 Fonctionnalité en cours d'implémentation", ft.Colors.BLUE_400)
    
    # ========== Détails d'un item ==========
    
    def show_item_details(self, item: Dict, item_type: str):
        """Affiche les détails d'une playlist ou d'un album."""
        # TODO: Implémenter l'affichage des détails avec lecture des fichiers locaux
        self.show_snackbar(f"ℹ️ Détails de {item.get('title', 'item')}", ft.Colors.BLUE_400)
    
    # ========== Suppression ==========
    
    def remove_item(self, item_id: str, item_type: str):
        """Supprime un item de la liste et du disque."""
        # Trouver l'item
        if item_type == "playlist":
            item = next((p for p in self.playlists if p['id'] == item_id), None)
            if item:
                self.playlists = [p for p in self.playlists if p['id'] != item_id]
        else:
            item = next((a for a in self.albums if a['id'] == item_id), None)
            if item:
                self.albums = [a for a in self.albums if a['id'] != item_id]
        
        if not item:
            return
        
        # Demander confirmation
        def confirm_delete(e):
            dialog.open = False
            self.page.update()
            
            try:
                base_path = self.get_profile_base_path()
                category = "Playlists" if item_type == "playlist" else "Albums"
                folder_name = f"{item['id']} - {item['title']}"
                folder_path = os.path.join(base_path, category, folder_name)
                
                if os.path.exists(folder_path):
                    import shutil
                    shutil.rmtree(folder_path)
                    self.show_snackbar(f"✅ Dossier supprimé", ft.Colors.GREEN_400)
                
                # Rafraîchir
                if item_type == "playlist":
                    self.refresh_playlists()
                else:
                    self.refresh_albums()
                    
            except Exception as ex:
                self.show_snackbar(f"❌ Erreur : {str(ex)}", ft.Colors.RED_400)
        
        def cancel_delete(e):
            dialog.open = False
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression"),
            content=ft.Text(
                f"Voulez-vous vraiment supprimer '{item['title']}' ?\n\n"
                f"⚠️ Cela supprimera également tous les fichiers téléchargés."
            ),
            actions=[
                ft.TextButton("Annuler", on_click=cancel_delete),
                ft.TextButton("Supprimer", on_click=confirm_delete),
            ],
        )
        
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    # ========== Synchronisation ==========
    
    def sync_single_item(self, item: Dict, item_type: str):
        """Synchronise un seul item."""
        if self.is_syncing:
            return
        
        # Afficher la barre de progression sur la carte
        progress_bar_ref = item.get('_progress_bar_ref')
        if progress_bar_ref and progress_bar_ref.current:
            progress_bar_ref.current.visible = True
            progress_bar_ref.current.value = None
            self.page.update()
        
        title = item.get('title', 'item')
        self.show_snackbar(f"🚀 Synchronisation de {title}...", ft.Colors.BLUE_400)
        
        self.is_syncing = True
        thread = threading.Thread(target=self.run_sync_single, args=(item, item_type), daemon=True)
        thread.start()
    
    def run_sync_single(self, item: Dict, item_type: str):
        """Exécute la synchronisation d'un seul item."""
        try:
            # Créer la config avec le chemin du profil
            base_path = self.get_profile_base_path()
            
            _, config, synchronizer = sync_manager.create_temp_config(
                self.prefs.get('arl', '').strip(),
                base_path,
                self.prefs.get('format', 'MP3_320')
            )
            
            # Synchroniser
            success = sync_manager.sync_item(synchronizer, item['id'], item_type)
            
            if success:
                self.show_snackbar(f"✅ {item.get('title', 'Item')} synchronisé !", ft.Colors.GREEN_400)
                self.scan_existing_items()
                self.refresh_playlists()
                self.refresh_albums()
            else:
                self.show_snackbar(f"❌ Échec de la synchronisation", ft.Colors.RED_400)
            
            self.page.update()
                
        except Exception as e:
            print(f"Erreur: {e}")
            self.show_snackbar(f"❌ Erreur : {str(e)}", ft.Colors.RED_400)
            self.page.update()
        
        finally:
            self.is_syncing = False
            
            # Cacher la barre de progression
            progress_bar_ref = item.get('_progress_bar_ref')
            if progress_bar_ref and progress_bar_ref.current:
                progress_bar_ref.current.visible = False
                self.page.update()
            
            self.page.update()
    
    def start_sync_all(self):
        """Démarre la synchronisation de tous les items."""
        if self.is_syncing:
            return
        
        if not self.playlists and not self.albums:
            self.show_snackbar("❌ Aucune playlist ou album à synchroniser", ft.Colors.ORANGE_400)
            return
        
        self.is_syncing = True
        self.progress_bar.visible = True
        self.status_text.value = "Synchronisation en cours..."
        self.status_text.color = ft.Colors.BLUE_400
        self.force_ui_update()
        
        thread = threading.Thread(target=self.run_sync_all, daemon=True)
        thread.start()
    
    def run_sync_all(self):
        """Exécute la synchronisation de tous les items."""
        try:
            # Créer la config
            base_path = self.get_profile_base_path()
            
            _, config, synchronizer = sync_manager.create_temp_config(
                self.prefs.get('arl', '').strip(),
                base_path,
                self.prefs.get('format', 'MP3_320')
            )
            
            total = len(self.playlists) + len(self.albums)
            current = 0
            success_count = 0
            
            # Synchroniser toutes les playlists
            for playlist in self.playlists:
                current += 1
                self.status_text.value = f"Synchronisation {current}/{total} : {playlist.get('title', 'playlist')}..."
                self.page.update()
                
                try:
                    if synchronizer.sync_playlist(playlist['id']):
                        success_count += 1
                except Exception as e:
                    print(f"Erreur playlist {playlist['id']}: {e}")
                
                self.page.update()
            
            # Synchroniser tous les albums
            for album in self.albums:
                current += 1
                self.status_text.value = f"Synchronisation {current}/{total} : {album.get('title', 'album')}..."
                self.page.update()
                
                try:
                    if synchronizer.sync_album(album['id']):
                        success_count += 1
                except Exception as e:
                    print(f"Erreur album {album['id']}: {e}")
                
                self.page.update()
            
            # Recharger
            self.scan_existing_items()
            self.refresh_playlists()
            self.refresh_albums()
            
            self.status_text.value = f"✅ Synchronisation terminée ! ({success_count}/{total} réussis)"
            self.status_text.color = ft.Colors.GREEN_400
            self.page.update()
            
        except Exception as e:
            self.status_text.value = f"❌ Erreur : {str(e)}"
            self.status_text.color = ft.Colors.RED_400
            self.page.update()
        
        finally:
            self.is_syncing = False
            self.progress_bar.visible = False
            self.page.update()


def main(page: ft.Page):
    """Point d'entrée de l'application."""
    DsyncGUI(page)


if __name__ == "__main__":
    ft.run(target=main)
