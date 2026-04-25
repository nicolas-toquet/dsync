# dsync GUI - Structure modulaire

## Vue d'ensemble

L'interface graphique de dsync a été refactorisée en une architecture modulaire pour améliorer la maintenabilité et la clarté du code.

## Structure des fichiers

```
dsync/
├── dsync_gui.py                 # Point d'entrée principal (simplifié)
└── dsync_gui/                   # Package principal
    ├── __init__.py              # Exports du package
    ├── main.py                  # Classe principale DsyncGUI
    ├── ui/                      # Composants d'interface utilisateur
    │   ├── __init__.py
    │   ├── app_bar.py           # AppBar avec navigation
    │   ├── status_bar.py        # Barre de progression et statut
    │   ├── collections.py       # Grilles de playlists/albums
    │   └── dialogs.py           # Tous les dialogues (settings, profils, etc.)
    ├── services/                # Logique métier
    │   ├── __init__.py
    │   ├── preferences.py       # Gestion des préférences utilisateur
    │   ├── file_scanner.py      # Scan des dossiers locaux
    │   └── sync_manager.py      # Opérations de synchronisation
    └── utils/                   # Utilitaires
        ├── __init__.py
        └── helpers.py           # Fonctions utilitaires (snackbar, UI update)
```

## Modules

### 📱 UI (Interface utilisateur)

#### `ui/app_bar.py`
- `build_app_bar()` : Construit la barre supérieure avec thème, profils, paramètres
- `build_fab()` : Bouton flottant pour synchroniser tout

#### `ui/status_bar.py`
- `build_status_bar()` : Barre de progression en bas de l'écran

#### `ui/collections.py`
- `build_collections_panel()` : Panneau principal avec grilles
- `build_item_card()` : Carte individuelle pour playlist/album avec boutons d'action

#### `ui/dialogs.py`
- `build_welcome_dialog()` : Dialogue de bienvenue
- `build_settings_dialog()` : Dialogue des paramètres (ARL, format, chemin)
- `build_profiles_dialog()` : Dialogue de gestion des profils
- `build_add_profile_dialog()` : Dialogue d'ajout de profil
- `build_add_item_dialog()` : Dialogue d'ajout manuel de playlist/album

### ⚙️ Services (Logique métier)

#### `services/preferences.py`
- `load_preferences()` : Charge les préférences depuis JSON
- `save_preferences()` : Sauvegarde les préférences
- `get_profile_base_path()` : Retourne le chemin avec profil

#### `services/file_scanner.py`
- `scan_existing_items()` : Scanne les dossiers Playlists/ et Albums/
- `parse_folder_name()` : Parse un dossier et lit le fichier .info

#### `services/sync_manager.py`
- `create_temp_config()` : Crée une config temporaire pour Deezer
- `sync_item()` : Synchronise un item (playlist ou album)

### 🛠️ Utils (Utilitaires)

#### `utils/helpers.py`
- `show_snackbar()` : Affiche un message temporaire
- `force_ui_update()` : Force le rafraîchissement de l'UI

### 🏛️ Main (Classe principale)

#### `main.py`
Classe `DsyncGUI` contenant :
- Gestion de l'état (playlists, albums, is_syncing)
- Orchestration des composants UI
- Callbacks pour les événements utilisateur
- Opérations Deezer (fetch, import, sync)
- Gestion des dialogues

## Lancement

```bash
python3 dsync_gui.py
```

## Avantages de cette architecture

1. **Séparation des responsabilités** : UI, logique métier, et utilitaires sont séparés
2. **Maintenabilité** : Chaque fichier fait ~50-300 lignes au lieu de 2000
3. **Réutilisabilité** : Les composants peuvent être réutilisés ou testés indépendamment
4. **Clarté** : La navigation dans le code est plus intuitive
5. **Extensibilité** : Ajout de nouvelles fonctionnalités facilité

## Migration depuis l'ancien code

L'ancien fichier `dsync_gui.py` (1962 lignes) a été remplacé par un simple point d'entrée qui importe la nouvelle structure modulaire. Toutes les fonctionnalités ont été préservées.

## TODO (fonctionnalités incomplètes dans la refactorisation)

- [ ] `show_import_dialog()` : Dialogue d'importation Deezer avec sélection multiple
- [ ] `show_item_details()` : Affichage des pistes avec métadonnées locales (mutagen)

Ces fonctionnalités étaient présentes dans l'ancien code mais nécessitent des ajustements pour s'intégrer dans la nouvelle architecture modulaire.
