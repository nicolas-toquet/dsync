#!/usr/bin/env python3
"""
Script de build pour créer l'exécutable dsync.

Usage:
    python build.py
"""

import os
import sys
import platform
import subprocess
import shutil


def install_dependencies():
    """Installe les dépendances nécessaires pour le build."""
    print("📦 Installation des dépendances de build...")
    
    dependencies = [
        "pyinstaller",
        "flet"
    ]
    
    for dep in dependencies:
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
    
    print("✅ Dépendances installées\n")


def clean_build_dirs():
    """Nettoie les dossiers de build précédents."""
    print("🧹 Nettoyage des builds précédents...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['dsync_gui.spec']
    
    for directory in dirs_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"   Supprimé: {directory}")
    
    for file in files_to_clean:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Supprimé: {file}")
    
    print("✅ Nettoyage terminé\n")


def build_executable():
    """Compile l'application en exécutable."""
    print("🔨 Compilation de l'exécutable...")
    print("   Cela peut prendre quelques minutes...\n")
    
    # Détecter le système d'exploitation
    system = platform.system()
    
    # Options de base pour PyInstaller
    options = [
        "pyinstaller",
        "--name=dsync",
        "--onefile",
        "--windowed",  # Pas de console
        "--icon=NONE",  # Pas d'icône personnalisée pour l'instant
        "--clean",
        "--noconfirm",
        # Inclure les modules nécessaires
        "--hidden-import=flet",
        "--hidden-import=dsync",
        "--hidden-import=mutagen",
        "--hidden-import=deemix",
        # Collecter les données de flet
        "--collect-all=flet",
        "dsync_gui.py"
    ]
    
    try:
        subprocess.check_call(options)
        print("\n✅ Compilation terminée !")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors de la compilation: {e}")
        return False


def show_result():
    """Affiche les informations sur l'exécutable créé."""
    system = platform.system()
    
    if system == "Windows":
        exe_path = os.path.join("dist", "dsync.exe")
        exe_name = "dsync.exe"
    elif system == "Darwin":  # macOS
        exe_path = os.path.join("dist", "dsync.app")
        exe_name = "dsync.app"
    else:  # Linux
        exe_path = os.path.join("dist", "dsync")
        exe_name = "dsync"
    
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        
        print("\n" + "="*60)
        print("🎉 BUILD RÉUSSI !")
        print("="*60)
        print(f"\n📦 Exécutable créé : {exe_path}")
        print(f"💾 Taille : {size_mb:.1f} MB")
        print(f"\n📤 Distribution :")
        print(f"   1. Envoyez le fichier '{exe_name}' à vos amis")
        print(f"   2. Ils doublent-cliquent dessus, c'est tout !")
        print(f"\n⚠️  Note : L'exécutable est spécifique à {system}")
        if system != "Windows":
            print("      Pour Windows, vous devez compiler sur Windows")
        print("="*60 + "\n")
        
        return True
    else:
        print("\n❌ L'exécutable n'a pas été créé")
        return False


def main():
    """Fonction principale du script de build."""
    print("\n" + "="*60)
    print("🚀 dsync - Script de build")
    print("="*60 + "\n")
    
    # Vérifier qu'on est dans le bon répertoire
    if not os.path.exists("dsync_gui.py"):
        print("❌ Erreur : dsync_gui.py introuvable")
        print("   Lancez ce script depuis le répertoire racine du projet")
        sys.exit(1)
    
    # 1. Installer les dépendances
    try:
        install_dependencies()
    except Exception as e:
        print(f"❌ Erreur lors de l'installation des dépendances: {e}")
        sys.exit(1)
    
    # 2. Nettoyer les builds précédents
    clean_build_dirs()
    
    # 3. Compiler l'exécutable
    if not build_executable():
        sys.exit(1)
    
    # 4. Afficher le résultat
    if show_result():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
