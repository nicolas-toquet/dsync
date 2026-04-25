"""Barre de statut en bas de l'application."""

import flet as ft


def build_status_bar(progress_bar: ft.Ref, status_text: ft.Ref) -> ft.Container:
    """
    Construit la barre de statut avec progress bar et texte.
    
    Args:
        progress_bar: Référence vers la ProgressBar
        status_text: Référence vers le Text
    
    Returns:
        Container avec la barre de statut
    """
    return ft.Container(
        content=ft.Column(
            [
                ft.ProgressBar(
                    ref=progress_bar,
                    value=None,
                    visible=False,
                ),
                ft.Text(
                    ref=status_text,
                    value="Prêt",
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
            ],
            spacing=5,
            tight=True,
        ),
        padding=ft.padding.all(10),
        border=ft.border.only(top=ft.border.BorderSide(1, ft.Colors.GREY_300)),
    )
