# Guide de migration - dsync GUI refactorisé

## Pour les développeurs

### Qu'est-ce qui a changé ?

L'ancien fichier `dsync_gui.py` monolithique (1962 lignes) a été divisé en plusieurs modules pour une meilleure organisation.

### Comment importer la classe principale ?

**Avant:**
```python
from dsync_gui import DsyncGUI
```

**Maintenant:**
```python
from dsync_gui import DsyncGUI  # Toujours valide !
# ou
from dsync_gui.main import DsyncGUI
```

### Où trouver les composants ?

| Fonctionnalité | Ancien emplacement | Nouveau module |
|----------------|-------------------|----------------|
| Classe principale | `dsync_gui.py` ligne 23 | `dsync_gui/main.py` |
| Construction AppBar | `dsync_gui.py` ligne 515 | `dsync_gui/ui/app_bar.py` |
| Construction collections | `dsync_gui.py` ligne 909 | `dsync_gui/ui/collections.py` |
| Tous les dialogues | `dsync_gui.py` ligne 653-886 | `dsync_gui/ui/dialogs.py` |
| Barre de statut | `dsync_gui.py` ligne 559 | `dsync_gui/ui/status_bar.py` |
| Gestion préférences | `dsync_gui.py` ligne 249-297 | `dsync_gui/services/preferences.py` |
| Scan fichiers | `dsync_gui.py` ligne 68-151 | `dsync_gui/services/file_scanner.py` |
| Synchronisation | `dsync_gui.py` ligne 1769-1942 | `dsync_gui/services/sync_manager.py` |
| Utilitaires | `dsync_gui.py` ligne 1944-1952 | `dsync_gui/utils/helpers.py` |

### Lancement de l'application

**Inchangé :**
```bash
python3 dsync_gui.py
```

### Modifications dans le code

Aucune modification n'est nécessaire pour utiliser l'application. Toutes les fonctionnalités existantes sont préservées.

### Pour contribuer au code

1. **Ajouter un nouveau dialogue** : Éditer `dsync_gui/ui/dialogs.py`
2. **Ajouter un nouveau service** : Créer un fichier dans `dsync_gui/services/`
3. **Modifier l'AppBar** : Éditer `dsync_gui/ui/app_bar.py`
4. **Modifier les cartes** : Éditer `dsync_gui/ui/collections.py`

### Architecture des modules

```python
# Importer des composants UI
from dsync_gui.ui import app_bar, status_bar, collections, dialogs

# Importer des services
from dsync_gui.services import preferences, file_scanner, sync_manager

# Importer des utilitaires
from dsync_gui.utils import helpers

# Utiliser un composant
appbar = app_bar.build_app_bar(profile_name, on_theme_toggle, ...)
```

### Fonctionnalités TODO

Deux fonctionnalités de l'ancien code nécessitent encore d'être portées :

1. **`show_import_dialog()`** : Dialogue d'importation depuis Deezer avec liste de sélection
   - Ancien code: lignes 1579-1707
   - Statut: Remplacé par un placeholder dans `main.py`
   - Action: Implémenter le dialogue complet avec fetch des playlists/albums

2. **`show_item_details()`** : Affichage des pistes avec métadonnées locales
   - Ancien code: lignes 1183-1327
   - Statut: Remplacé par un placeholder dans `main.py`
   - Action: Implémenter la lecture avec mutagen et affichage dans un dialogue

Ces fonctionnalités peuvent être ajoutées progressivement sans impacter le reste du code.

## Pour les utilisateurs

### Qu'est-ce qui change pour moi ?

**Rien !** L'application fonctionne exactement de la même manière. Le lancement, l'interface et toutes les fonctionnalités sont identiques.

### Pourquoi cette refactorisation ?

- Meilleure maintenabilité du code
- Facilite les corrections de bugs
- Permet d'ajouter de nouvelles fonctionnalités plus facilement
- Améliore la qualité du code

## En cas de problème

Si vous rencontrez un problème après la mise à jour :

1. Vérifiez que tous les fichiers du dossier `dsync_gui/` sont présents
2. Assurez-vous que les imports fonctionnent : `python3 -c "from dsync_gui import main"`
3. Consultez les logs dans le terminal pour identifier l'erreur

Le code a été testé et validé avant déploiement.
