import os
import textwrap
import sys
import glob 
from argparse import Namespace # Für das args-Objekt
from dataclasses import asdict # Nur noch für loaded_config, nicht für args_for_translator

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import sys
        import glob
        from argparse import Namespace
        from dataclasses import asdict
        
        sys.path.append(os.path.join(os.getcwd(), 'Free-Markdown-Translator', 'src'))
        from config import get_config 
        from MarkdownTranslator import MdTranslater

        def main():
            config_file_path = 'config.yaml' 
            
            # --- Schritt 1: Konfiguration laden ---
            if not os.path.exists(config_file_path):
                print(f"Fehler: Konfigurationsdatei '{config_file_path}' nicht gefunden.", file=sys.stderr)
                sys.exit(1)
            try:
                loaded_config = get_config(config_file_path)
            except Exception as e:
                print(f"Fehler beim Laden der Konfigurationsdatei '{config_file_path}': {e}", file=sys.stderr)
                sys.exit(1)

            # --- Schritt 2: Markdown-Dateien dynamisch ermitteln ---
            actual_src_dir = loaded_config.src_dir if hasattr(loaded_config, 'src_dir') else 'DE'
            
            markdown_files = []
            if os.path.isdir(actual_src_dir):
                if hasattr(loaded_config, 'src_filenames') and loaded_config.src_filenames:
                    for pattern in loaded_config.src_filenames:
                        full_pattern = pattern # Muster direkt verwenden, da es den Pfad enthält (z.B. 'DE/*.md')
                        found_files_full_paths = glob.glob(full_pattern) 
                        
                        for full_path in found_files_full_paths:
                            relative_path_to_src_dir = os.path.relpath(full_path, actual_src_dir)
                            markdown_files.append(relative_path_to_src_dir)
            
            if not markdown_files:
                print(f"Warnung: Keine Markdown-Dateien im Verzeichnis '{actual_src_dir}' mit den Mustern '{loaded_config.src_filenames}' gefunden. Der Workflow wird beendet.", file=sys.stderr)
                sys.exit(0) 

            # --- Schritt 3: args-Objekt für den Translator vorbereiten ---
            config_as_dict = asdict(loaded_config)
            args_for_translator = Namespace(**config_as_dict)
            args_for_translator.f = None 

            args_for_translator.src_filenames = markdown_files
            
            # Debugging-Ausgaben (KORREKTUR HIER: vars() statt asdict() für Namespace-Objekt)
            print(f"DEBUG: Geladene Konfiguration (initial): {asdict(loaded_config)}", file=sys.stderr)
            print(f"DEBUG: Vorbereitete args für Translator (final): {vars(args_for_translator)}", file=sys.stderr) # HIER KORRIGIERT
            print(f"DEBUG: Gefundene Markdown-Dateien für Übersetzung: {args_for_translator.src_filenames}", file=sys.stderr)


            # --- Schritt 4: MdTranslater instanziieren und ausführen ---
            try:
                translator = MdTranslater(args=args_for_translator) 
                
                # Debugging nach Instanziierung:
                print(f"DEBUG: Translator interne src_filenames nach Instanziierung: {translator.config.src_filenames}", file=sys.stderr)
                print(f"DEBUG: Translator interne src_dir nach Instanziierung: {translator.config.src_dir}", file=sys.stderr)

                translator.main() 
                
            except Exception as e:
                print(f"Fehler während der Übersetzung: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))