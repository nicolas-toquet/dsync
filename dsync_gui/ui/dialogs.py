"""Gestion de tous les dialogues de l'application."""

import flet as ft
from typing import Dict, List, Callable


def build_welcome_dialog(on_configure) -> ft.AlertDialog:
    """Construit le dialogue d'accueil pour la configuration initiale."""
    return ft.AlertDialog(
        modal=True,
        title=ft.Row(
            [
                ft.Icon(ft.Icons.INFO_OUTLINE, size=28, color=ft.Colors.BLUE_400),
                ft.Text("Configuration initiale", size=20, weight=ft.FontWeight.BOLD),
            ],
            spacing=10,
        ),
        content=ft.Text(
            "Bienvenue ! Pour commencer, configurez votre token ARL et votre dossier de téléchargement.",
            size=14,
        ),
        actions=[
            ft.Button(
                "Configurer maintenant",
                on_click=on_configure,
            ),
        ],
    )


def build_settings_dialog(
    prefs: Dict,
    is_dark_mode: bool,
    on_save,
    on_pick_folder,
    format_dropdown_ref: ft.Ref,
    path_field_ref: ft.Ref,
    arl_field_ref: ft.Ref,
) -> ft.AlertDialog:
    """
    Construit le dialogue des paramètres.
    
    Args:
        prefs: Préférences utilisateur
        is_dark_mode: Mode sombre activé ou non
        on_save: Callback pour enregistrer les préférences
        on_pick_folder: Callback pour choisir un dossier
        format_dropdown_ref: Référence vers le Dropdown de format
        path_field_ref: Référence vers le TextField de chemin
        arl_field_ref: Référence vers le TextField ARL
    
    Returns:
        AlertDialog configuré
    """
    # 1. Dropdown format audio (en premier)
    format_dropdown = ft.Dropdown(
        ref=format_dropdown_ref,
        label="Format audio",
        value=prefs.get('format', 'MP3_320'),
        options=[
            ft.dropdown.Option("FLAC", "FLAC (Qualité maximale)"),
            ft.dropdown.Option("MP3_320", "MP3 320kbps (Haute qualité)"),
            ft.dropdown.Option("MP3_128", "MP3 128kbps (Qualité standard)"),
        ],
        on_change=lambda e: on_save(),
    )
    
    # 2. Champ chemin de téléchargement
    path_field = ft.TextField(
        ref=path_field_ref,
        label="Dossier de téléchargement",
        value=prefs.get('base_path', ''),
        on_change=lambda e: on_save(),
    )
    
    browse_button = ft.Button(
        "Parcourir",
        icon=ft.Icons.FOLDER_OPEN,
        on_click=on_pick_folder,
    )
    
    # 3. Champ ARL (en dernier avec explication détaillée)
    arl_field = ft.TextField(
        ref=arl_field_ref,
        label="Token ARL Deezer (obligatoire)",
        password=True,
        can_reveal_password=True,
        value=prefs.get('arl', ''),
        on_change=lambda e: on_save(),
        multiline=False,
    )
    
    # Explication détaillée pour récupérer l'ARL
    arl_help = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Comment récupérer votre ARL :",
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_400 if is_dark_mode else ft.Colors.BLUE_700,
                ),
                ft.Text(
                    "1. Ouvrez deezer.com dans votre navigateur",
                    size=11,
                ),
                ft.Text(
                    "2. Connectez-vous à votre compte Deezer",
                    size=11,
                ),
                ft.Text(
                    "3. Ouvrez les outils développeur (F12 ou Cmd+Option+I sur Mac)",
                    size=11,
                ),
                ft.Text(
                    "4. Allez dans l'onglet 'Application' (Chrome) ou 'Stockage' (Firefox)",
                    size=11,
                ),
                ft.Text(
                    "5. Dans le menu de gauche : Cookies > https://www.deezer.com",
                    size=11,
                ),
                ft.Text(
                    "6. Cherchez la ligne 'arl' et copiez sa valeur",
                    size=11,
                ),
                ft.Text(
                    "7. Collez cette valeur dans le champ ci-dessus",
                    size=11,
                ),
                ft.Container(height=5),
                ft.Text(
                    "⚠️ L'ARL est personnel et confidentiel, ne le partagez pas !",
                    size=10,
                    italic=True,
                    color=ft.Colors.ORANGE_400 if is_dark_mode else ft.Colors.ORANGE_700,
                ),
            ],
            spacing=3,
        ),
        padding=10,
        bgcolor=ft.Colors.BLUE_GREY_900 if is_dark_mode else ft.Colors.BLUE_50,
        border_radius=5,
    )
    
    return ft.AlertDialog(
        title=ft.Row(
            [
                ft.Icon(ft.Icons.SETTINGS, size=24),
                ft.Text("Paramètres", size=20, weight=ft.FontWeight.BOLD),
            ],
            spacing=10,
        ),
        content=ft.Column(
            [
                # Format audio en premier
                ft.Text("Format audio", size=14, weight=ft.FontWeight.BOLD),
                format_dropdown,
                ft.Container(height=15),
                
                # Dossier de téléchargement
                ft.Text("Dossier de téléchargement", size=14, weight=ft.FontWeight.BOLD),
                path_field,
                browse_button,
                ft.Container(height=15),
                
                # Token ARL avec explication
                ft.Text("Authentification Deezer", size=14, weight=ft.FontWeight.BOLD),
                arl_field,
                ft.Container(height=5),
                arl_help,
            ],
            tight=True,
            width=600,
            scroll=ft.ScrollMode.AUTO,
        ),
        actions=[
            ft.Button(
                "Enregistrer et fermer",
                icon=ft.Icons.CHECK,
                on_click=on_save,
            ),
        ],
    )


def build_profiles_dialog(
    prefs: Dict,
    on_switch_profile: Callable,
    on_add_profile: Callable,
    on_delete_profile: Callable,
    on_close: Callable,
) -> ft.AlertDialog:
    """
    Construit le dialogue des profils.
    
    Args:
        prefs: Préférences utilisateur
        on_switch_profile: Callback pour changer de profil (reçoit profile_name)
        on_add_profile: Callback pour ajouter un profil
        on_delete_profile: Callback pour supprimer le profil actuel
        on_close: Callback pour fermer le dialogue
    
    Returns:
        AlertDialog configuré
    """
    # Liste des profils
    profiles = prefs.get('profiles', [{'name': 'Défaut', 'deezer_id': ''}])
    current_profile = prefs.get('current_profile_name', 'Défaut')
    
    profile_tiles = []
    for profile in profiles:
        is_selected = profile['name'] == current_profile
        profile_tiles.append(
            ft.ListTile(
                leading=ft.Icon(ft.Icons.PERSON),
                title=ft.Text(profile['name'], weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL),
                subtitle=ft.Text(f"ID: {profile['deezer_id']}" if profile['deezer_id'] else "Pas d'ID Deezer", size=11),
                trailing=ft.Icon(ft.Icons.CHECK_CIRCLE, color=ft.Colors.GREEN_400) if is_selected else None,
                selected=is_selected,
                on_click=lambda e, p=profile: on_switch_profile(p['name']),
            )
        )
    
    return ft.AlertDialog(
        title=ft.Row(
            [
                ft.Icon(ft.Icons.PEOPLE, size=24),
                ft.Text("Profils", size=20, weight=ft.FontWeight.BOLD),
            ],
            spacing=10,
        ),
        content=ft.Column(
            [
                ft.Column(
                    profile_tiles,
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                ),
                ft.Divider(),
                ft.Row(
                    [
                        ft.Button(
                            "Nouveau",
                            icon=ft.Icons.ADD,
                            on_click=on_add_profile,
                        ),
                        ft.OutlinedButton(
                            "Supprimer",
                            icon=ft.Icons.DELETE_OUTLINE,
                            on_click=on_delete_profile,
                        ),
                    ],
                    spacing=10,
                ),
            ],
            tight=True,
            width=400,
            height=400,
        ),
        actions=[
            ft.Button(
                "Fermer",
                on_click=on_close,
            ),
        ],
    )


def build_add_profile_dialog(
    on_add: Callable,
    on_cancel: Callable,
    name_field_ref: ft.Ref,
    deezer_id_field_ref: ft.Ref,
) -> ft.AlertDialog:
    """
    Construit le dialogue pour ajouter un nouveau profil.
    
    Args:
        on_add: Callback pour ajouter (reçoit e)
        on_cancel: Callback pour annuler
        name_field_ref: Référence vers le TextField nom
        deezer_id_field_ref: Référence vers le TextField deezer_id
    
    Returns:
        AlertDialog configuré
    """
    name_field = ft.TextField(
        ref=name_field_ref,
        label="Nom du profil",
        hint_text="ex: Famille",
        autofocus=True,
    )
    
    deezer_id_field = ft.TextField(
        ref=deezer_id_field_ref,
        label="ID Deezer (optionnel)",
        hint_text="ex: 4564471282",
    )
    
    return ft.AlertDialog(
        title=ft.Text("Ajouter un profil", size=18, weight=ft.FontWeight.BOLD),
        content=ft.Column(
            [
                name_field,
                deezer_id_field,
                ft.Text(
                    "💡 L'ID Deezer permet d'importer automatiquement les playlists/albums du profil.",
                    size=11,
                    color=ft.Colors.GREY_600,
                ),
            ],
            tight=True,
            width=400,
        ),
        actions=[
            ft.TextButton("Annuler", on_click=on_cancel),
            ft.Button("Ajouter", on_click=on_add),
        ],
    )


def build_add_item_dialog(
    item_type: str,
    on_add: Callable,
    on_cancel: Callable,
    id_field_ref: ft.Ref,
) -> ft.AlertDialog:
    """
    Construit le dialogue pour ajouter manuellement une playlist ou un album.
    
    Args:
        item_type: "playlist" ou "album"
        on_add: Callback pour ajouter
        on_cancel: Callback pour annuler
        id_field_ref: Référence vers le TextField ID
    
    Returns:
        AlertDialog configuré
    """
    label_text = "ID de la playlist" if item_type == 'playlist' else "ID de l'album"
    id_field = ft.TextField(
        ref=id_field_ref,
        label=label_text,
        hint_text="123456789",
        autofocus=True,
    )
    
    return ft.AlertDialog(
        title=ft.Text(f"Ajouter {'une playlist' if item_type == 'playlist' else 'un album'}"),
        content=ft.Column(
            [
                id_field,
                ft.Text(
                    "💡 Trouvez l'ID dans l'URL Deezer :\n"
                    f"deezer.com/{'playlist' if item_type == 'playlist' else 'album'}/123456789",
                    size=11,
                    color=ft.Colors.GREY_600,
                ),
            ],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton("Annuler", on_click=on_cancel),
            ft.TextButton("Ajouter", on_click=on_add),
        ],
    )
