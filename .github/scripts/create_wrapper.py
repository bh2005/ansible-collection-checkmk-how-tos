import os
import textwrap
import sys
from argparse import Namespace # Für das args-Objekt

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import sys
        from argparse import Namespace
        
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
                # Diese Funktion gibt ein 'Configration'-Dataclass-Objekt zurück, das alle Einstellungen enthält.
                loaded_config = get_config(config_file_path)
                
                # 2. Ein leeres Namespace-Objekt erstellen.
                # Der MdTranslater erwartet ein Namespace-Objekt als 'args'.
                args_for_translator = Namespace()

                # 3. Die geladene Konfiguration manuell in das Namespace-Objekt übertragen.
                # Die Namen der Attribute im Namespace müssen genau den Erwartungen des MdTranslater entsprechen.
                # Die meisten Felder der Configration-Dataclass können direkt übernommen werden.
                for field in loaded_config.__dataclass_fields__:
                    setattr(args_for_translator, field, getattr(loaded_config, field))
                
                # Wichtige Überprüfung für 'f' (Einzeldatei) vs. 'src_filenames' (Muster)
                # Das Tool scheint 'f' zu erwarten, wenn eine einzelne Datei übersetzt wird.
                # Da wir 'src_filenames' nutzen, sollte 'f' nicht gesetzt sein oder None sein,
                # damit das Tool die 'src_filenames'-Liste in der Konfiguration verwendet.
                # Standardmäßig ist 'f' nicht in der Configration-Dataclass, also müssen wir es nicht explizit auf None setzen,
                # solange es nicht in der config.yaml oder durch parse_args hinzugefügt wurde.
                # Wenn wir die Configration direkt als args übergeben, hat es kein 'f' Attribut,
                # es sei denn, es wird als Kommandozeilenargument übergeben.

                # 4. Den MdTranslater mit dem vorbereiteten args-Objekt instanziieren.
                # Jetzt wird der MdTranslater mit einem Objekt initialisiert,
                # das alle seine erwarteten Konfigurationsparameter als Attribute enthält.
                translator = MdTranslater(args=args_for_translator) 
                
                # 5. Die Hauptmethode des Übersetzers aufrufen, um die Übersetzung zu starten.
                translator.main() 
                
            except Exception as e:
                print(f"Fehler während der Übersetzung: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))