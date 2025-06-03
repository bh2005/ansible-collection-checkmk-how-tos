#!/bin/bash

# Dieses Skript generiert die 'translate.py' Datei im Root des Repositories.
# Es wird von GitHub Actions aufgerufen.

# Der Python-Code für translate.py
read -r -d '' PYTHON_SCRIPT << EOM
import sys

# Fügt den 'src'-Ordner des geklonten Repos zum Python-Suchpfad hinzu.
sys.path.append('Free-Markdown-Translator/src') 
from MarkdownTranslator import MdTranslater

def main():
    # KORREKTUR: MdTranslater wird ohne Argumente aufgerufen.
    # Er erwartet, dass er seine config.yaml selbst findet und lädt.
    translator = MdTranslater() 

if __name__ == "__main__":
    main()
EOM

echo "$PYTHON_SCRIPT" > translate.py
echo "translate.py successfully generated:"
cat translate.py