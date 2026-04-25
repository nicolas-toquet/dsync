# dsync

Outil de synchronisation automatique de playlists Deezer vers votre disque local.

## 📋 Description

Ce script Python permet de :
- Télécharger automatiquement les morceaux d'une playlist Deezer
- Synchroniser les modifications (ajouts/suppressions de morceaux)
- Gérer plusieurs formats audio (FLAC, MP3 320kbps, MP3 128kbps)
- Éviter les doublons grâce aux métadonnées

## 🚀 Installation et configuration

### 1. Prérequis

- Python 3.10 ou supérieur (requis pour les dépendances récentes)
- Un compte Deezer Premium (requis pour le téléchargement)

### 2. Création de l'environnement virtuel

```bash
# Création du virtual environment
python3 -m venv venv

# Activation de l'environnement
# Sur macOS/Linux :
source venv/bin/activate
# Sur Windows :
# venv\Scripts\activate
```

### 3. Installation des dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

Créez un fichier `config.toml` à la racine du projet :

```toml
[deezer]
arl = "VOTRE_TOKEN_ARL_DEEZER"

[storage]
base_path = "/chemin/vers/votre/dossier/musique"
format = "MP3_320"  # Options: FLAC, MP3_320, MP3_128
```

#### Comment obtenir votre token ARL ?

1. Connectez-vous à [Deezer](https://www.deezer.com) dans votre navigateur
2. Ouvrez les outils de développement (F12)
3. Allez dans l'onglet "Application" ou "Stockage"
4. Cherchez les cookies du domaine `deezer.com`
5. Copiez la valeur du cookie `arl`

## 📖 Utilisation

```bash
# Activer l'environnement virtuel (si ce n'est pas déjà fait)
source venv/bin/activate

# Lancer la synchronisation d'une playlist
python3 sync_deezer.py <PLAYLIST_ID>
```

### Trouver l'ID d'une playlist

L'ID de la playlist se trouve dans l'URL Deezer :
```
https://www.deezer.com/fr/playlist/1234567890
                                    ^^^^^^^^^^
                                    C'est l'ID
```

### Exemple

```bash
python3 sync_deezer.py 1234567890
```

## 🔄 Fonctionnement

1. **Première exécution** : tous les morceaux de la playlist sont téléchargés
2. **Exécutions suivantes** :
   - Les nouveaux morceaux sont téléchargés
   - Les morceaux retirés de la playlist sont supprimés localement
   - Les morceaux existants ne sont pas re-téléchargés

## 📁 Structure des fichiers

```
dsync/
├── sync_deezer.py          # Point d'entrée (CLI)
├── dsync/                  # Package principal
│   ├── __init__.py        # Initialisation du package
│   ├── config.py          # Gestion de la configuration
│   ├── deezer_client.py   # Interface avec Deezer/Deemix
│   ├── metadata.py        # Gestion des tags audio
│   ├── synchronizer.py    # Logique de synchronisation
│   └── utils.py           # Utilitaires (logs, imports dynamiques)
├── config.toml            # Configuration (à créer)
├── requirements.txt       # Dépendances Python
├── venv/                  # Environnement virtuel (créé par vous)
└── README.md              # Ce fichier
```

Les morceaux seront téléchargés dans :
```
{base_path}/{PLAYLIST_ID} - {NOM_DE_LA_PLAYLIST}/
```

## 🛠️ Développement

### Architecture du code

Le projet suit une architecture modulaire professionnelle :

- **`config.py`** : Chargement et validation de la configuration TOML
- **`utils.py`** : LogListener pour les logs, imports dynamiques
- **`metadata.py`** : Lecture/écriture des tags ID3 (MP3) et FLAC
- **`deezer_client.py`** : Connexion à Deezer, récupération des playlists
- **`synchronizer.py`** : Orchestration de la synchronisation
  1. Nettoyage des fichiers obsolètes
  2. Téléchargement des nouveaux morceaux
  3. Marquage des métadonnées avec l'ID Deezer
- **`sync_deezer.py`** : Point d'entrée CLI simple et propre

### Principes appliqués

- ✅ **Séparation des responsabilités** : chaque module a un rôle précis
- ✅ **Type hints** : améliore la lisibilité et permet l'autocomplétion
- ✅ **Docstrings** : documentation claire de chaque fonction/classe
- ✅ **Gestion d'erreurs** : messages clairs et informations contextuelles
- ✅ **Testabilité** : modules indépendants faciles à tester

### Désactivation de l'environnement virtuel

```bash
deactivate
```

## ⚠️ Notes importantes

- Un compte Deezer Premium est **obligatoire**
- Le token ARL est personnel et confidentiel, ne le partagez pas
- Le fichier `config.toml` est ignoré par Git (`.gitignore`)
- Les téléchargements respectent les conditions d'utilisation de Deezer

## 📦 Dépendances principales

- `deemix` : Moteur de téléchargement Deezer
- `mutagen` : Manipulation des métadonnées audio
- `toml` : Lecture de la configuration
- `deezer-py` : API Deezer

## 🐛 Résolution de problèmes

**Erreur "config.toml introuvable"**
→ Créez le fichier `config.toml` à la racine du projet

**Erreur d'authentification**
→ Vérifiez que votre token ARL est valide et à jour

**Aucun téléchargement**
→ Vérifiez que vous avez un compte Deezer Premium actif
