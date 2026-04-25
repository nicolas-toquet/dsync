"""Gestion des collections (grilles, cartes, boutons) pour playlists et albums."""

import flet as ft
from typing import Dict, List


def build_collections_panel(
    playlists_grid: ft.GridView,
    albums_grid: ft.GridView,
    on_import_playlists,
    on_import_albums,
    on_add_playlist,
    on_add_album,
    on_refresh_playlists,
    on_refresh_albums,
) -> ft.Column:
    """
    Construit le panneau principal avec les grilles de playlists et albums.
    
    Args:
        playlists_grid: GridView pour les playlists
        albums_grid: GridView pour les albums
        on_import_playlists: Callback pour importer les playlists
        on_import_albums: Callback pour importer les albums
        on_add_playlist: Callback pour ajouter une playlist manuellement
        on_add_album: Callback pour ajouter un album manuellement
        on_refresh_playlists: Callback pour rafraîchir les playlists
        on_refresh_albums: Callback pour rafraîchir les albums
    
    Returns:
        Column avec les deux sections (playlists et albums)
    """
    # Section Playlists
    playlists_section = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.QUEUE_MUSIC_ROUNDED, size=32, color=ft.Colors.BLUE_400),
                    ft.Text(
                        "Mes Playlists",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        icon_size=28,
                        tooltip="Importer mes playlists depuis Deezer",
                        on_click=on_import_playlists,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE,
                        icon_size=28,
                        tooltip="Ajouter une playlist manuellement",
                        on_click=on_add_playlist,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            ft.Container(height=15),
            playlists_grid,
        ],
        spacing=0,
    )
    
    # Section Albums
    albums_section = ft.Column(
        [
            ft.Row(
                [
                    ft.Icon(ft.Icons.ALBUM_ROUNDED, size=32, color=ft.Colors.PURPLE_400),
                    ft.Text(
                        "Mes Albums",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD,
                        icon_size=28,
                        tooltip="Importer mes albums favoris depuis Deezer",
                        on_click=on_import_albums,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.ADD_CIRCLE,
                        icon_size=28,
                        tooltip="Ajouter un album manuellement",
                        on_click=on_add_album,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            ft.Container(height=15),
            albums_grid,
        ],
        spacing=0,
    )
    
    # Charger les items
    on_refresh_playlists()
    on_refresh_albums()
    
    return ft.Column(
        [
            playlists_section,
            ft.Divider(height=40),
            albums_section,
        ],
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )


def build_item_card(
    item: Dict,
    item_type: str,
    on_sync,
    on_info,
    on_delete,
    page: ft.Page,
    fetch_cover_url_callback,
) -> ft.Container:
    """
    Construit une carte pour une playlist ou un album.
    
    Args:
        item: Dictionnaire avec id, title, cover_url
        item_type: "playlist" ou "album"
        on_sync: Callback pour synchroniser
        on_info: Callback pour afficher les détails
        on_delete: Callback pour supprimer
        page: Page Flet
        fetch_cover_url_callback: Callback async pour récupérer l'URL de couverture
    
    Returns:
        Container avec la carte
    """
    import threading
    import asyncio
    
    # Image de couverture
    cover_url = item.get('cover_url', '')
    
    # Si pas de cover_url, créer un placeholder et charger en arrière-plan
    if cover_url:
        cover = ft.Image(
            src=cover_url,
            width=150,
            height=150,
            fit=ft.BoxFit.COVER,
            border_radius=ft.BorderRadius.all(5),
        )
    else:
        # Placeholder en attendant le chargement
        cover_ref = ft.Ref[ft.Image]()
        
        # Icône différente selon le type
        placeholder_icon = ft.Icons.QUEUE_MUSIC_ROUNDED if item_type == 'playlist' else ft.Icons.ALBUM_ROUNDED
        placeholder_color = ft.Colors.BLUE_300 if item_type == 'playlist' else ft.Colors.PURPLE_300
        
        cover = ft.Container(
            width=150,
            height=150,
            bgcolor=ft.Colors.GREY_300,
            border_radius=ft.BorderRadius.all(5),
            content=ft.Icon(
                placeholder_icon,
                size=60,
                color=placeholder_color,
            ),
            alignment=ft.alignment.Alignment(0, 0),
            ref=cover_ref,
        )
        
        # Charger la pochette en arrière-plan
        async def load_cover():
            url = await fetch_cover_url_callback(item['id'], item_type)
            if url:
                item['cover_url'] = url
                # Mettre à jour l'affichage
                if cover_ref.current:
                    cover_ref.current.content = ft.Image(
                        src=url,
                        width=150,
                        height=150,
                        fit=ft.BoxFit.COVER,
                    )
                    cover_ref.current.bgcolor = None
                    page.update()
        
        # Lancer le chargement dans un thread
        threading.Thread(target=lambda: asyncio.run(load_cover()), daemon=True).start()
    
    # Bouton de synchronisation
    sync_button = ft.IconButton(
        icon=ft.Icons.SYNC_ROUNDED,
        icon_size=16,
        icon_color=ft.Colors.GREY_600,
        tooltip="Synchroniser",
        on_click=lambda e: on_sync(item, item_type),
        style=ft.ButtonStyle(padding=0),
    )
    
    # Bouton d'information
    info_button = ft.IconButton(
        icon=ft.Icons.INFO_OUTLINE_ROUNDED,
        icon_size=16,
        icon_color=ft.Colors.GREY_600,
        tooltip="Détails",
        on_click=lambda e: on_info(item, item_type),
        style=ft.ButtonStyle(padding=0),
    )
    
    # Bouton de suppression
    delete_button = ft.IconButton(
        icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
        icon_size=16,
        icon_color=ft.Colors.GREY_600,
        tooltip="Supprimer",
        on_click=lambda e: on_delete(item['id'], item_type),
        style=ft.ButtonStyle(padding=0),
    )
    
    # Barre de boutons au-dessus de la pochette
    buttons_bar = ft.Row(
        [
            sync_button,
            info_button,
            delete_button,
        ],
        spacing=5,
        alignment=ft.MainAxisAlignment.CENTER,
    )
    
    # Titre
    title = ft.Text(
        item.get('title', f"{item_type.capitalize()} {item['id']}"),
        size=12,
        weight=ft.FontWeight.BOLD,
        max_lines=2,
        overflow=ft.TextOverflow.ELLIPSIS,
        text_align=ft.TextAlign.CENTER,
        width=150,
    )
    
    # Barre de progression (cachée par défaut)
    progress_bar_ref = ft.Ref[ft.ProgressBar]()
    progress_bar = ft.ProgressBar(
        ref=progress_bar_ref,
        width=150,
        height=3,
        visible=False,
    )
    
    # Stocker la référence dans l'item pour y accéder plus tard
    item['_progress_bar_ref'] = progress_bar_ref
    
    return ft.Container(
        content=ft.Column(
            [
                buttons_bar,
                ft.Container(height=2),
                cover,
                ft.Container(height=3),
                progress_bar,
                ft.Container(height=2),
                title,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        border_radius=ft.BorderRadius.all(8),
        padding=5,
    )
