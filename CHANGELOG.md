# Changelog - dsync

## [1.0.0] - 2026-04-23

### 🎉 Refactorisation majeure

#### Ajouts ✨

- **Architecture modulaire** : Code réorganisé en 6 modules indépendants
- **Package `dsync/`** : Structure professionnelle de package Python
  - `config.py` : Gestion de la configuration
  - `utils.py` : Utilitaires et logs
  - `metadata.py` : Gestion des tags audio
  - `deezer_client.py` : Interface API Deezer
  - `synchronizer.py` : Logique de synchronisation
  - `__init__.py` : Exports du package

- **Documentation complète** :
  - `README.md` : Guide utilisateur détaillé avec installation pas à pas
  - `DEVELOPER.md` : Guide pour les développeurs et contributeurs
  - `REFACTORING.md` : Résumé de la refactorisation
  - `CHANGELOG.md` : Historique des versions

- **Outils** :
  - `check_installation.py` : Script de vérification de l'installation
  - `config.toml.example` : Exemple de configuration commenté

- **Type hints** : Ajout de types sur toutes les fonctions
- **Docstrings** : Documentation Google-style sur toutes les classes/fonctions
- **Gestion d'erreurs** : Messages clairs et validation des entrées
- **Logs améliorés** : Émojis, compteurs de progression, résumés

#### Améliorations 🚀

- **Séparation des responsabilités** : Chaque module a un rôle précis
- **Testabilité** : Code modulaire facile à tester
- **Maintenabilité** : Structure claire et logique
- **Réutilisabilité** : Modules importables indépendamment
- **Messages d'aide** : Interface CLI améliorée avec aide détaillée
- **Validation** : Vérification de l'ID de playlist
- **Gestion Ctrl+C** : Interruption propre du programme

#### Changements 🔄

- **Point d'entrée** : `sync_deezer.py` simplifié (61 lignes vs 162)
- **Configuration** : Classe `Config` avec validation
- **Client Deezer** : Classe `DeezerClient` encapsulant toute l'API
- **Métadonnées** : Classe `MetadataManager` pour les tags
- **Synchronisation** : Classe `PlaylistSynchronizer` pour l'orchestration

#### Technique 🔧

- Architecture SOLID
- Principes Clean Code
- Respect PEP 8
- Properties Python pour accès config
- Gestion d'exceptions améliorée
- Import dynamique robuste

### 📊 Statistiques

- **Fichiers** : 1 → 13 (code + docs)
- **Modules Python** : 1 → 7
- **Lignes de code** : 162 → ~715
- **Classes** : 1 → 5
- **Documentation** : Basique → Complète

---

## [0.1.0] - 2026-04-23 (Version initiale)

### Fonctionnalités initiales

- Synchronisation de playlists Deezer
- Téléchargement des morceaux (FLAC, MP3)
- Nettoyage des fichiers obsolètes
- Tagging avec ID Deezer dans métadonnées
- Configuration via `config.toml`
- Support MP3 et FLAC

---

## Notes de migration

### De v0.1.0 vers v1.0.0

**Aucun changement breaking** ! L'interface reste identique :

```bash
# Fonctionne toujours de la même manière
python3 sync_deezer.py <PLAYLIST_ID>
```

**Nouveautés à utiliser** :

1. Vérifier l'installation :
   ```bash
   python3 check_installation.py
   ```

2. Utiliser l'exemple de config :
   ```bash
   cp config.toml.example config.toml
   ```

3. Importer les modules dans vos scripts :
   ```python
   from dsync import Config, PlaylistSynchronizer
   
   config = Config()
   sync = PlaylistSynchronizer(config)
   sync.sync_playlist("1234567890")
   ```

---

## Roadmap future

### v1.1.0 (Prévu)
- [ ] Tests unitaires
- [ ] Tests d'intégration
- [ ] CI/CD avec GitHub Actions

### v1.2.0 (Prévu)
- [ ] Mode verbose (`--verbose`)
- [ ] Mode silencieux (`--quiet`)
- [ ] Logs dans fichier

### v2.0.0 (Prévu)
- [ ] Support de plusieurs playlists simultanées
- [ ] Mode watch (synchronisation automatique)
- [ ] Interface web
- [ ] Export vers d'autres formats (M3U, etc.)

---

**Format du changelog** : [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/)
**Versioning** : [Semantic Versioning](https://semver.org/lang/fr/)
