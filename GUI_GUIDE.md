# Guide de l'interface graphique dsync

## 🖥️ Pour les utilisateurs (vos amis)

### Installation - ZERO configuration nécessaire !

1. **Téléchargez** le fichier que vous avez reçu :
   - Windows : `dsync.exe`
   - Mac : `dsync.app`

2. **Double-cliquez** sur le fichier

3. **C'est tout !** L'application se lance

### Utilisation

#### 1. Première configuration

**Token ARL Deezer** (une seule fois) :
1. Allez sur [deezer.com](https://www.deezer.com) et connectez-vous
2. Appuyez sur `F12` (ouvre les outils développeur)
3. Allez dans l'onglet **Application** (ou **Stockage**)
4. Dans la barre latérale : **Cookies** → **deezer.com**
5. Cherchez le cookie `arl` et copiez sa **valeur**
6. Collez cette valeur dans le champ "Token ARL Deezer"

**Dossier de téléchargement** :
- Cliquez sur l'icône 📁 pour choisir où sauvegarder vos morceaux
- Par défaut : `Musique/Deezer`

**Format audio** :
- FLAC : Qualité maximale (fichiers plus gros)
- MP3 320kbps : Haute qualité (recommandé)
- MP3 128kbps : Qualité standard (fichiers plus petits)

#### 2. Ajouter des playlists et albums

**Méthode 1 : Importer depuis votre compte Deezer** (recommandé)

1. Cliquez sur l'icône 📥 (téléchargement) à côté de "Mes Playlists" ou "Mes Albums"
2. L'application récupère automatiquement toutes vos playlists/albums
3. Cochez celles que vous souhaitez synchroniser
4. Cliquez sur "Importer"

**Méthode 2 : Ajouter manuellement par ID**

1. Allez sur Deezer et ouvrez votre playlist ou album
2. L'URL ressemble à : `https://www.deezer.com/fr/playlist/1234567890`
3. Copiez juste le **numéro** à la fin (ex: `1234567890`)
4. Cliquez sur l'icône ➕ à côté de "Mes Playlists" ou "Mes Albums"
5. Collez l'ID et validez

#### 3. Synchroniser

**Synchronisation unique :**
- Cliquez sur une carte de playlist/album pour la synchroniser individuellement

**Synchronisation globale :**
- Cliquez sur le bouton "Synchroniser tout" dans le panneau de configuration
- Toutes vos playlists et albums seront synchronisés les uns après les autres

#### 4. Attendre la synchronisation

- Une barre de progression s'affiche
- Les messages vous indiquent l'avancement
- Quand c'est terminé : ✅ Message de confirmation !

#### 5. Retrouver vos morceaux

Vos fichiers sont organisés dans :
```
Dossier choisi/
├── Playlists/
│   └── [ID] - [Nom de la playlist]/
│       ├── Artiste - Titre 1.mp3
│       ├── Artiste - Titre 2.mp3
│       └── cover.jpg
└── Albums/
    └── [ID] - [Nom de l'album]/
        ├── Artiste - Titre 1.mp3
        ├── Artiste - Titre 2.mp3
        └── cover.jpg
```

### 💡 Astuces

- **Configuration sauvegardée** : Vos paramètres sont mémorisés
- **Importation automatique** : Utilisez l'import Deezer pour récupérer toutes vos playlists/albums en un clic
- **Re-synchronisation** : Lancez à nouveau pour récupérer les nouveaux morceaux
- **Nettoyage automatique** : Les morceaux retirés de la playlist sont supprimés localement
- **Gestion visuelle** : Cliquez sur la croix rouge d'une carte pour supprimer une playlist/album
- **Pochettes** : Les pochettes sont automatiquement téléchargées et affichées

### ⚠️ Problèmes courants

**"Configuration invalide"**
→ Vérifiez votre token ARL (il expire parfois, récupérez-en un nouveau)

**"Erreur de connexion"**
→ Vérifiez votre connexion internet

**"Impossible de récupérer les morceaux"**
→ Vérifiez que l'ID de playlist est correct

**"Erreur d'authentification"**
→ Votre compte Deezer doit être Premium

---

## 👨‍💻 Pour le développeur (vous)

### Compiler l'exécutable

#### Prérequis
- Python 3.10+ installé
- Un terminal

#### Étapes

1. **Cloner ou télécharger le projet**
```bash
cd dsync
```

2. **Créer un environnement virtuel**
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Tester l'interface localement** (optionnel)
```bash
python dsync_gui.py
```

5. **Compiler l'exécutable**
```bash
python build.py
```

Le script va :
- ✅ Installer PyInstaller
- ✅ Nettoyer les builds précédents
- ✅ Compiler l'application
- ✅ Créer un fichier standalone dans `dist/`

6. **Résultat**

Vous trouverez l'exécutable dans :
```
dist/
└── dsync.exe (Windows)
    ou
└── dsync.app (Mac)
    ou
└── dsync (Linux)
```

Taille approximative : 80-150 MB

### Distribution

**Pour Windows :**
- Compilez sur Windows
- Envoyez `dist/dsync.exe`

**Pour Mac :**
- Compilez sur Mac
- Envoyez `dist/dsync.app`
- ⚠️ Sur Mac récent, l'utilisateur devra peut-être autoriser l'app dans Préférences Système

**Pour Linux :**
- Compilez sur Linux
- Envoyez `dist/dsync`
- L'utilisateur devra peut-être faire `chmod +x dsync`

### Compilation multi-plateforme

PyInstaller génère un exécutable **pour la plateforme sur laquelle il tourne**.

**Solutions :**

1. **GitHub Actions** (recommandé) :
   - Compilez automatiquement pour Windows, Mac et Linux
   - Voir : `.github/workflows/build.yml` (à créer)

2. **Machines virtuelles** :
   - VM Windows pour compiler la version Windows
   - VM Mac pour compiler la version Mac

3. **Services cloud** :
   - [GitHub Actions](https://github.com/features/actions) (gratuit)
   - [AppVeyor](https://www.appveyor.com/)
   - [Travis CI](https://travis-ci.org/)

### Personnalisation

#### Changer l'icône

1. Créez/téléchargez une icône :
   - Windows : fichier `.ico`
   - Mac : fichier `.icns`

2. Modifiez `build.py` :
```python
"--icon=path/to/icon.ico",  # Remplacez NONE
```

#### Changer les couleurs

Modifiez `dsync_gui.py` :
```python
# Ligne ~15
self.page.theme_mode = ft.ThemeMode.DARK  # Mode sombre

# Lignes avec ft.colors.BLUE_400
# Remplacez par d'autres couleurs : RED_400, GREEN_400, PURPLE_400, etc.
```

#### Ajouter un logo

```python
# Dans build_ui(), ajoutez :
logo = ft.Image(
    src="path/to/logo.png",
    width=100,
    height=100
)
```

### Debug

**Mode développement** :
```bash
python dsync_gui.py
```

**Voir les erreurs de l'exécutable** :
- Compilez sans `--windowed` pour voir la console
- Les logs sont dans la zone "Afficher les détails"

### Structure du code

```python
class DsyncGUI:
    __init__()           # Initialisation de l'interface
    load_preferences()   # Charge les préférences sauvegardées
    save_preferences()   # Sauvegarde les préférences
    build_ui()           # Construit tous les éléments visuels
    validate_inputs()    # Vérifie les champs avant sync
    start_sync()         # Lance la sync dans un thread
    run_sync()           # Exécute la synchronisation
    add_log()            # Ajoute un message dans les logs
```

### Dépendances GUI

- **flet** : Framework UI moderne (basé sur Flutter)
- **threading** : Pour ne pas bloquer l'interface pendant la sync
- **json** : Pour sauvegarder les préférences utilisateur

---

## 🎨 Captures d'écran

L'interface inclut :
- 📝 Formulaire de configuration (ARL, dossier, format)
- 🎵 Champ pour l'ID de playlist
- 🔄 Bouton de synchronisation
- 📊 Barre de progression
- 📋 Zone de logs détaillés (repliable)
- 💾 Sauvegarde automatique des préférences

---

## 🔮 Améliorations futures possibles

- [ ] Icône personnalisée
- [x] Support de plusieurs playlists/albums en même temps
- [x] Importation automatique depuis le compte Deezer
- [x] Interface visuelle avec pochettes
- [ ] Historique des synchronisations
- [ ] Mode sombre/clair
- [ ] Notifications système
- [ ] Auto-update de l'app
- [ ] Statistiques (morceaux téléchargés, espace disque, etc.)
- [ ] Export de playlist vers d'autres formats
- [ ] Recherche de playlists/albums dans l'interface

---

## 📞 Support

Pour toute question ou problème :
1. Vérifiez la section "Problèmes courants" ci-dessus
2. Consultez les logs détaillés dans l'application
3. Contactez le développeur avec la copie des logs
