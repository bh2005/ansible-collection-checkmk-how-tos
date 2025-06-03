import os
import textwrap
import sys
import glob 
from argparse import Namespace
from dataclasses import asdict

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
                        # HIER IST DIE WESENTLICHE ÄNDERUNG:
                        # Das Muster (z.B. 'DE/*.md') wird direkt verwendet,
                        # da es den Pfad (DE/) bereits enthält.
                        # KEIN os.path.join(actual_src_dir, pattern) mehr!
                        found_files_full_paths = glob.glob(pattern) 
                        
                        for full_path in found_files_full_paths:
                            # Wir müssen den Pfad relativ zum src_dir machen.
                            # Wenn full_path 'DE/my_file.md' ist und actual_src_dir 'DE',
                            # dann ist relative_path_to_src_dir 'my_file.md'.
                            relative_path_to_src_dir = os.path.relpath(full_path, actual_src_dir)
                            markdown_files.append(relative_path_to_src_dir)
            
            if not markdown_files:
                print(f"Warnung: Keine Markdown-Dateien im Verzeichnis '{actual_src_dir}' mit den Mustern '{loaded_config.src_filenames}' gefunden. Bitte überprüfen Sie den Pfad und die Muster.", file=sys.stderr)
                # EXIT 0, wenn keine Dateien gefunden werden, damit der Workflow nicht als Fehler markiert wird,
                # obwohl keine Übersetzung nötig war.
                sys.exit(0)

            # --- Schritt 3: args-Objekt für den Translator vorbereiten ---
            config_as_dict = asdict(loaded_config)
            args_for_translator = Namespace(**config_as_dict)
            args_for_translator.f = None 

            # Update src_filenames in args_for_translator with the dynamically found files
            args_for_translator.src_filenames = markdown_files
            
            # Debugging-Ausgaben:
            print(f"DEBUG: Geladene Konfiguration (initial): {asdict(loaded_config)}", file=sys.stderr)
            print(f"DEBUG: Vorbereitete args für Translator (final): {asdict(args_for_translator)}", file=sys.stderr)
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