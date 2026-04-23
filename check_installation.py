#!/usr/bin/env python3
"""
Script de test pour vérifier l'installation et la configuration de dsync.
"""

import sys
import os

def check_python_version():
    """Vérifie la version de Python."""
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ requis")
        return False
    return True

def check_dependencies():
    """Vérifie que les dépendances sont installées."""
    required = ['toml', 'deemix', 'mutagen']
    missing = []
    
    for module in required:
        try:
            __import__(module)
            print(f"✅ Module '{module}' installé")
        except ImportError:
            print(f"❌ Module '{module}' manquant")
            missing.append(module)
    
    if missing:
        print("\n💡 Installez les dépendances avec :")
        print("   pip install -r requirements.txt")
        return False
    return True

def check_config():
    """Vérifie la présence du fichier de configuration."""
    if os.path.exists('config.toml'):
        print("✅ Fichier config.toml trouvé")
        return True
    else:
        print("❌ Fichier config.toml manquant")
        print("\n💡 Créez config.toml à partir de l'exemple :")
        print("   cp config.toml.example config.toml")
        print("   # Puis éditez config.toml avec vos paramètres")
        return False

def check_modules():
    """Vérifie que les modules du package dsync sont accessibles."""
    try:
        from dsync import Config, PlaylistSynchronizer
        print("✅ Modules dsync importés avec succès")
        return True
    except ImportError as e:
        print(f"❌ Erreur d'import des modules dsync : {e}")
        return False

def main():
    """Fonction principale."""
    print("="*60)
    print("🔍 Vérification de l'installation dsync")
    print("="*60 + "\n")
    
    checks = [
        ("Version Python", check_python_version),
        ("Dépendances", check_dependencies),
        ("Configuration", check_config),
        ("Modules dsync", check_modules),
    ]
    
    all_ok = True
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        if not check_func():
            all_ok = False
    
    print("\n" + "="*60)
    if all_ok:
        print("✅ Installation OK ! Vous pouvez utiliser dsync")
        print("\n💡 Exemple d'utilisation :")
        print("   python3 sync_deezer.py 1234567890")
    else:
        print("⚠️  Veuillez corriger les erreurs ci-dessus")
    print("="*60)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())
