"""AppBar de l'application avec boutons thème, profils et paramètres."""

import flet as ft


def build_app_bar(
    current_profile_name: str,
    on_theme_toggle,
    on_profiles_click,
    on_settings_click
) -> ft.AppBar:
    """
    Construit l'AppBar avec les boutons de navigation.
    
    Args:
        current_profile_name: Nom du profil actuel
        on_theme_toggle: Callback pour le changement de thème
        on_profiles_click: Callback pour ouvrir les profils
        on_settings_click: Callback pour ouvrir les paramètres
    
    Returns:
        AppBar configuré
    """
    return ft.AppBar(
        title=ft.Text("dsync - Synchronisation Deezer", size=20, weight=ft.FontWeight.BOLD),
        center_title=False,
        actions=[
            ft.Container(
                content=ft.Text(
                    f"Profil: {current_profile_name}",
                    size=14,
                    color=ft.Colors.GREEN_400,
                ),
                padding=ft.padding.symmetric(horizontal=10),
            ),
            ft.IconButton(
                icon=ft.Icons.BRIGHTNESS_6,
                tooltip="Changer le thème",
                on_click=on_theme_toggle,
            ),
            ft.IconButton(
                icon=ft.Icons.PERSON,
                tooltip="Profils",
                on_click=on_profiles_click,
            ),
            ft.IconButton(
                icon=ft.Icons.SETTINGS,
                tooltip="Paramètres",
                on_click=on_settings_click,
            ),
        ],
    )


def build_fab(on_click) -> ft.FloatingActionButton:
    """
    Construit le FloatingActionButton pour synchroniser tout.
    
    Args:
        on_click: Callback lors du clic
    
    Returns:
        FloatingActionButton configuré
    """
    return ft.FloatingActionButton(
        icon=ft.Icons.SYNC,
        tooltip="Synchroniser tout",
        on_click=on_click,
        bgcolor=ft.Colors.PRIMARY,
    )
