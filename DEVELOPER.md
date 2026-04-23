# Guide du développeur - dsync

## 📐 Architecture

### Vue d'ensemble

Le projet est organisé en modules indépendants avec des responsabilités claires :

```
sync_deezer.py          → Point d'entrée CLI
    ↓
dsync/synchronizer.py   → Orchestration de la sync
    ↓
    ├─ dsync/config.py         → Configuration
    ├─ dsync/deezer_client.py  → API Deezer
    └─ dsync/metadata.py       → Tags audio
```

### Description des modules

#### `config.py`
- Chargement du fichier `config.toml`
- Validation des paramètres
- Conversion format → bitrate
- Recherche automatique du fichier de config

#### `utils.py`
- `LogListener` : Affichage des messages formatés
- `find_class_in_package()` : Import dynamique pour deemix
- Helpers pour le formatage

#### `metadata.py`
- `MetadataManager` : Gestion des tags audio
- Support MP3 (ID3) et FLAC
- Lecture/écriture de l'ID Deezer dans les métadonnées
- Extraction d'ID depuis les noms de fichiers (fallback)

#### `deezer_client.py`
- `DeezerClient` : Interface avec l'API Deezer
- Connexion via ARL
- Récupération des playlists et morceaux
- Création des objets de téléchargement
- Gestion des settings deemix

#### `synchronizer.py`
- `PlaylistSynchronizer` : Logique principale
- 3 étapes :
  1. **Cleanup** : Suppression des fichiers obsolètes
  2. **Download** : Téléchargement des nouveaux morceaux
  3. **Tagging** : Ajout de l'ID Deezer dans les métadonnées

#### `sync_deezer.py`
- Point d'entrée CLI minimaliste
- Validation des arguments
- Gestion des erreurs globales
- Messages d'aide

## 🔧 Ajout de fonctionnalités

### Ajouter un nouveau format audio

1. Modifier `dsync/config.py` :
```python
@property
def bitrate_code(self) -> int:
    bitrate_map = {
        "FLAC": 9,
        "MP3_320": 3,
        "MP3_128": 1,
        "NOUVEAU_FORMAT": X  # ← Ajouter ici
    }
```

2. Mettre à jour la documentation dans le README

### Ajouter un nouveau champ de métadonnées

Modifier `dsync/metadata.py` :

```python
@staticmethod
def tag_file_with_id(filepath: str, track_id: str) -> bool:
    if filepath.endswith('.mp3'):
        audio = EasyID3(filepath)
        audio['website'] = str(track_id)
        audio['nouveau_champ'] = "valeur"  # ← Ici
        audio.save()
```

### Ajouter des logs supplémentaires

Modifier `dsync/utils.py` :

```python
@classmethod
def send(cls, key: str, value: Optional[dict] = None):
    # Ajouter un nouveau type de message
    elif key == 'nouveau_type':
        print(f"🆕 Nouveau : {value}")
```

## 🧪 Tests

### Tests manuels

```bash
# 1. Vérification de l'installation
python3 check_installation.py

# 2. Test avec une playlist
python3 sync_deezer.py <PLAYLIST_ID>

# 3. Test de la configuration
python3 -c "from dsync.config import Config; c = Config(); print(c.deezer_arl)"
```

### Tests unitaires (à implémenter)

Structure suggérée :
```
tests/
├── __init__.py
├── test_config.py
├── test_metadata.py
├── test_deezer_client.py
└── test_synchronizer.py
```

## 📦 Packaging

### Installation en mode développement

```bash
pip install -e .
```

Nécessite un fichier `setup.py` :

```python
from setuptools import setup, find_packages

setup(
    name="dsync",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "deemix>=3.6.6",
        "mutagen>=1.47.0",
        "toml>=0.10.2",
    ],
    entry_points={
        'console_scripts': [
            'dsync=sync_deezer:main',
        ],
    },
)
```

## 🐛 Débogage

### Mode verbose

Pour ajouter un mode verbose, modifier `sync_deezer.py` :

```python
import logging

if '--verbose' in sys.argv:
    logging.basicConfig(level=logging.DEBUG)
```

### Afficher les objets deemix

```python
import pprint
pprint.pprint(vars(download_object))
```

## 🔐 Sécurité

### Bonnes pratiques

- ✅ Le fichier `config.toml` est dans `.gitignore`
- ✅ Ne jamais logger le token ARL
- ✅ Utiliser des variables d'environnement en production

### Variables d'environnement

Modifier `config.py` pour supporter :

```python
@property
def deezer_arl(self) -> str:
    return os.getenv('DEEZER_ARL') or self._data.get('deezer', {}).get('arl', '')
```

## 📚 Ressources

- [API Deezer](https://developers.deezer.com/api)
- [Documentation deemix](https://gitlab.com/RemixDev/deemix-py)
- [Mutagen documentation](https://mutagen.readthedocs.io/)
- [PEP 8 Style Guide](https://pep8.org/)

## 🤝 Contribution

### Workflow Git

```bash
# Créer une branche
git checkout -b feature/ma-fonctionnalite

# Faire vos modifications
# ...

# Commit
git add .
git commit -m "feat: Description de la fonctionnalité"

# Push
git push origin feature/ma-fonctionnalite
```

### Convention de commits

- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Documentation
- `refactor:` Refactoring sans changement de comportement
- `test:` Ajout/modification de tests
- `chore:` Tâches de maintenance
