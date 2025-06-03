import os
import textwrap
import sys
from argparse import Namespace
from dataclasses import asdict # Wir brauchen asdict wieder, um die Konfiguration als Diktat zu übertragen

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import sys
        from argparse import Namespace
        from dataclasses import asdict # Für die Konvertierung des Configration-Objekts

        # Pfad zum src-Ordner des Free-Markdown-Translator-Projekts hinzufügen
        sys.path.append(os.path.join(os.getcwd(), 'Free-Markdown-Translator', 'src'))
        
        # Die benötigten Module des Free-Markdown-Translator importieren
        from config import get_config # Zum Laden unserer YAML-Konfiguration
        from MarkdownTranslator import MdTranslater # Die Hauptklasse des Übersetzers

        def main():
            config_file_path = 'config.yaml' # Die kopierte Konfigurationsdatei im Root-Verzeichnis

            # Überprüfen, ob die Konfigurationsdatei existiert
            if not os.path.exists(config_file_path):
                print(f"Fehler: Konfigurationsdatei '{config_file_path}' nicht gefunden. Bitte stellen Sie sicher, dass sie ins Root-Verzeichnis kopiert wurde.", file=sys.stderr)
                sys.exit(1)
            
            try:
                # 1. Konfiguration mithilfe der get_config-Funktion des Tools laden.
                # Diese Funktion gibt ein 'Configration'-Dataclass-Objekt zurück.
                loaded_config = get_config(config_file_path)
                
                # 2. Das geladene Configration-Objekt in ein Dictionary umwandeln.
                # Dies ist nötig, um ein Namespace-Objekt daraus zu erstellen.
                config_dict = asdict(loaded_config)
                
                # 3. Ein Namespace-Objekt aus dem Dictionary erstellen.
                # Der MdTranslater erwartet ein Namespace-Objekt als 'args'.
                args_for_translator = Namespace(**config_dict)
                
                # 4. WICHTIG: Das 'f'-Attribut explizit auf None setzen.
                # Der MdTranslater versucht immer auf args.f zuzugreifen.
                # Da wir src_filenames verwenden, wird args.f nicht benötigt,
                # muss aber existieren, um einen AttributeError zu vermeiden.
                args_for_translator.f = None

                # 5. Den MdTranslater mit dem vorbereiteten args-Objekt instanziieren.
                translator = MdTranslater(args=args_for_translator) 
                
                # 6. Die Hauptmethode des Übersetzers aufrufen, um die Übersetzung zu starten.
                translator.main() 
                
            except Exception as e:
                print(f"Fehler während der Übersetzung: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))