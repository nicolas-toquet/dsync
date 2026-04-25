#!/usr/bin/env python3
"""
Script de vérification rapide de l'installation modulaire de dsync GUI
"""

import sys
import os

def check_structure():
    """Vérifie que tous les fichiers nécessaires sont présents."""
    print("🔍 Vérification de la structure modulaire...")
    
    required_files = [
        'dsync_gui.py',
        'dsync_gui/__init__.py',
        'dsync_gui/main.py',
        'dsync_gui/ui/__init__.py',
        'dsync_gui/ui/app_bar.py',
        'dsync_gui/ui/status_bar.py',
        'dsync_gui/ui/collections.py',
        'dsync_gui/ui/dialogs.py',
        'dsync_gui/services/__init__.py',
        'dsync_gui/services/preferences.py',
        'dsync_gui/services/file_scanner.py',
        'dsync_gui/services/sync_manager.py',
        'dsync_gui/utils/__init__.py',
        'dsync_gui/utils/helpers.py',
    ]
    
    missing = []
    for filepath in required_files:
        if not os.path.exists(filepath):
            missing.append(filepath)
            print(f"  ❌ Manquant: {filepath}")
        else:
            print(f"  ✅ {filepath}")
    
    if missing:
        print(f"\n❌ {len(missing)} fichier(s) manquant(s)")
        return False
    else:
        print(f"\n✅ Tous les fichiers sont présents ({len(required_files)} fichiers)")
        return True

def check_imports():
    """Vérifie que tous les imports fonctionnent."""
    print("\n🔍 Vérification des imports...")
    
    try:
        from dsync_gui import main, DsyncGUI
        print("  ✅ Import dsync_gui")
        
        from dsync_gui.ui import app_bar, status_bar, collections, dialogs
        print("  ✅ Import dsync_gui.ui")
        
        from dsync_gui.services import preferences, file_scanner, sync_manager
        print("  ✅ Import dsync_gui.services")
        
        from dsync_gui.utils import helpers
        print("  ✅ Import dsync_gui.utils")
        
        print("\n✅ Tous les imports fonctionnent")
        return True
    except Exception as e:
        print(f"\n❌ Erreur d'import: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_syntax():
    """Vérifie la syntaxe de tous les fichiers Python."""
    print("\n🔍 Vérification de la syntaxe...")
    
    import ast
    
    python_files = []
    for root, dirs, files in os.walk('dsync_gui'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    python_files.append('dsync_gui.py')
    
    errors = []
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                ast.parse(f.read())
            print(f"  ✅ {filepath}")
        except SyntaxError as e:
            errors.append((filepath, e))
            print(f"  ❌ {filepath}: {e}")
    
    if errors:
        print(f"\n❌ {len(errors)} erreur(s) de syntaxe")
        return False
    else:
        print(f"\n✅ Syntaxe correcte pour tous les fichiers ({len(python_files)} fichiers)")
        return True

def main():
    """Point d'entrée du script de vérification."""
    print("=" * 60)
    print("  Vérification de l'installation modulaire dsync GUI")
    print("=" * 60)
    print()
    
    checks = [
        ("Structure", check_structure),
        ("Syntaxe", check_syntax),
        ("Imports", check_imports),
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("  RÉSUMÉ")
    print("=" * 60)
    for name, result in results:
        status = "✅ OK" if result else "❌ ÉCHEC"
        print(f"  {name:20s}: {status}")
    
    all_ok = all(r for _, r in results)
    
    if all_ok:
        print("\n🎉 Tout fonctionne ! L'application est prête à être lancée.")
        print("   Lancez avec: python3 dsync_gui.py")
        return 0
    else:
        print("\n⚠️  Certaines vérifications ont échoué. Consultez les détails ci-dessus.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
