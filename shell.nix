{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  # Les paquets qui seront présents dans ton terminal
  buildInputs = with pkgs; [
    python3
    python3Packages.pip
    python3Packages.virtualenv
    
    # Dépendances système pour compiler les librairies Python (deemix)
    openssl
    pkg-config
    stdenv.cc.cc.lib # Pour que les librairies C trouvent leurs fichiers
  ];

  # On définit des variables d'environnement pour aider Python à trouver OpenSSL
  shellHook = ''
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:$LD_LIBRARY_PATH"
    echo "--- Environnement de développement Deezer-Sync activé ---"
    python --version
  '';
}