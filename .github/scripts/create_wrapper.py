import os
import textwrap
import sys

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import sys
        
        # Pfad zum src-Ordner des Free-Markdown-Translator-Projekts hinzufügen
        sys.path.append(os.path.join(os.getcwd(), 'Free-Markdown-Translator', 'src'))
        
        # Die benötigte Klasse importieren
        from MarkdownTranslator import MdTranslater

        def main():
            # Der MdTranslater-Konstruktor wird OHNE Argumente aufgerufen.
            # Er wird intern versuchen, die 'config.yaml' (die wir ins Root kopiert haben) zu finden und zu laden.
            # Diese Methode ist am saubersten, wenn das Tool seine eigene Konfiguration laden kann.
            try:
                translator = MdTranslater() 
                
                # Prüfen, ob src_filenames korrekt geladen wurde, bevor main() aufgerufen wird
                if not hasattr(translator.config, 'src_filenames') or not translator.config.src_filenames:
                    print("FEHLER: translator.config.src_filenames ist leer oder nicht gesetzt nach der Initialisierung.", file=sys.stderr)
                    sys.exit(1)
                
                # Die Hauptmethode des Übersetzers aufrufen, um die Übersetzung zu starten.
                translator.main() 
                
            except Exception as e:
                print(f"Fehler während der Übersetzung: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))