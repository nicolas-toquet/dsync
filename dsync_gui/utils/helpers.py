"""Fonctions utilitaires pour l'interface graphique."""

import flet as ft


def show_snackbar(page: ft.Page, message: str, bgcolor: str):
    """Affiche un snackbar."""
    snackbar = ft.SnackBar(
        content=ft.Text(message, color=ft.Colors.WHITE),
        bgcolor=bgcolor,
    )
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()


def force_ui_update(page: ft.Page):
    """Force la mise à jour de l'interface utilisateur."""
    try:
        page.update()
    except Exception as e:
        print(f"Erreur lors de la mise à jour de l'UI : {e}")
