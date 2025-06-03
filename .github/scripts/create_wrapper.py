import os
import textwrap
import sys

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import sys

        # Fügt den 'src'-Ordner des geklonten Repos zum Python-Suchpfad hinzu.
        # Wichtig: os.getcwd() stellt sicher, dass der Pfad korrekt ist,
        # unabhängig davon, wo translate.py ausgeführt wird.
        sys.path.append(os.path.join(os.getcwd(), 'Free-Markdown-Translator', 'src'))
        
        # Importiere die MdTranslater-Klasse.
        # Diese Klasse wird die Konfiguration selbst laden, da wir ihr keine 'args' übergeben.
        from MarkdownTranslator import MdTranslater

        def main():
            # Der MdTranslater-Konstruktor wird jetzt OHNE Argumente aufgerufen.
            # Er wird intern die config.yaml (die wir ins Root kopiert haben) finden und nutzen.
            try:
                translator = MdTranslater() 
                translator.main() # Die eigentliche Startmethode des Translators
            except Exception as e:
                print(f"Error during translation: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))