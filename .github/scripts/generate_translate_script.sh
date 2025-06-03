#!/bin/bash

# Dieses Skript generiert die 'translate.py' Datei im Root des Repositories.
# Es wird von GitHub Actions aufgerufen.

# Der Python-Code für translate.py
read -r -d '' PYTHON_SCRIPT << EOM
import os
import yaml
import sys
from argparse import Namespace

# Fügt den 'src'-Ordner des geklonten Repos zum Python-Suchpfad hinzu.
# Dies ist notwendig, da Free-Markdown-Translator kein installierbares Paket ist.
sys.path.append('Free-Markdown-Translator/src') 
from MarkdownTranslator import MdTranslater

def main():
    config_path = '.github/config.yml'
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found. Please ensure it's committed and located at .github/config.yml in your repository root.")
        sys.exit(1) # Beende das Skript mit Fehler, wenn die Config nicht gefunden wird
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    args = Namespace(**config)
    # KORREKTUR: Die Übersetzung startet DIREKT hier im Konstruktor!
    # Es ist KEINE separate Methode wie .run() oder .run_translation() nötig.
    translator = MdTranslater(args) 

if __name__ == "__main__":
    main()
EOM

# Schreibe den Python-Code in die Datei translate.py
echo "$PYTHON_SCRIPT" > translate.py

echo "translate.py successfully generated:"
cat translate.py