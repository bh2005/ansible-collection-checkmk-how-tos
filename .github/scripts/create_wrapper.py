import os
import textwrap
import sys
import glob # Wird benötigt, um Dateien zu finden
from argparse import Namespace # Für das args-Objekt
from dataclasses import asdict # Um das Konfigurationsobjekt umzuwandeln

with open('translate.py', 'w', encoding='utf-8') as f:
    f.write(textwrap.dedent('''
        import os
        import sys
        import glob
        from argparse import Namespace
        from dataclasses import asdict
        
        # Fügt den 'src'-Ordner des geklonten Repos zum Python-Suchpfad hinzu.
        sys.path.append(os.path.join(os.getcwd(), 'Free-Markdown-Translator', 'src'))
        
        # Importiere die benötigten Module des Free-Markdown-Translator.
        from config import get_config 
        from MarkdownTranslator import MdTranslater

        def main():
            config_file_path = 'config.yaml' # Pfad zur Konfigurationsdatei (nach dem Kopieren ins Root)
            
            # --- Schritt 1: Konfiguration laden ---
            if not os.path.exists(config_file_path):
                print(f"Fehler: Konfigurationsdatei '{config_file_path}' nicht gefunden.", file=sys.stderr)
                sys.exit(1)
            try:
                # Lade die Konfiguration mit der Funktion des Tools.
                # Dies erstellt ein 'Configration'-Dataclass-Objekt.
                loaded_config = get_config(config_file_path)
            except Exception as e:
                print(f"Fehler beim Laden der Konfigurationsdatei '{config_file_path}': {e}", file=sys.stderr)
                sys.exit(1)

            # --- Schritt 2: Markdown-Dateien dynamisch ermitteln ---
            # Ermittle das Quellverzeichnis aus der geladenen Konfiguration.
            # Standardmäßig wird 'DE' verwendet, falls es nicht in der Konfigurationsdatei ist.
            actual_src_dir = loaded_config.src_dir if hasattr(loaded_config, 'src_dir') else 'DE'
            
            # Liste der tatsächlich zu übersetzenden Markdown-Dateien.
            markdown_files = []
            if os.path.isdir(actual_src_dir):
                # Wenn src_filenames in der Konfiguration definiert ist, verwende es als Muster.
                if hasattr(loaded_config, 'src_filenames') and loaded_config.src_filenames:
                    for pattern in loaded_config.src_filenames:
                        # Baue den vollständigen Pfad zum Muster (z.B. 'DE/*.md').
                        full_pattern = os.path.join(actual_src_dir, pattern)
                        # Finde alle Dateien, die dem Muster entsprechen.
                        found_files_full_paths = glob.glob(full_pattern)
                        
                        # Füge die Dateinamen relativ zum Quellverzeichnis hinzu.
                        # Das Tool erwartet Dateinamen wie 'meine_datei.md', nicht 'DE/meine_datei.md'.
                        for full_path in found_files_full_paths:
                            relative_path_to_src_dir = os.path.relpath(full_path, actual_src_dir)
                            markdown_files.append(relative_path_to_src_dir)
            
            if not markdown_files:
                print(f"Warnung: Keine Markdown-Dateien im Verzeichnis '{actual_src_dir}' mit den Mustern '{loaded_config.src_filenames}' gefunden.", file=sys.stderr)
                # Beende den Workflow hier, wenn keine Dateien gefunden wurden, da sonst nichts zu tun ist.
                sys.exit(0) # Exit with 0 for success if nothing to translate, but warns.

            # --- Schritt 3: args-Objekt für den Translator vorbereiten ---
            # Wandle das geladene Konfigurationsobjekt in ein Dictionary um.
            config_as_dict = asdict(loaded_config)
            
            # Erstelle ein Namespace-Objekt aus dem Dictionary.
            # Dies ist entscheidend, da der MdTranslater ein Namespace-Objekt erwartet.
            args_for_translator = Namespace(**config_as_dict)
            
            # WICHTIG: Das 'f'-Attribut explizit auf None setzen.
            # Dies verhindert den Fehler "'Namespace' object has no attribute 'f'".
            # 'f' wird nur für die Übersetzung einer einzelnen, direkt angegebenen Datei verwendet.
            args_for_translator.f = None

            # Aktualisiere die 'src_filenames' im args-Objekt mit den dynamisch gefundenen Dateien.
            args_for_translator.src_filenames = markdown_files
            
            # Debugging-Ausgaben zur Überprüfung:
            print(f"DEBUG: Geladene Konfiguration (initial): {asdict(loaded_config)}", file=sys.stderr)
            print(f"DEBUG: Vorbereitete args für Translator (final): {asdict(args_for_translator)}", file=sys.stderr)
            print(f"DEBUG: Gefundene Markdown-Dateien für Übersetzung: {args_for_translator.src_filenames}", file=sys.stderr)


            # --- Schritt 4: MdTranslater instanziieren und ausführen ---
            try:
                # Instanziiere den MdTranslater mit dem vorbereiteten 'args'-Objekt.
                # Dies sollte das Problem 'missing required argument' beheben.
                translator = MdTranslater(args=args_for_translator) 
                
                # Optionale Debug-Prüfung nach der Instanziierung:
                print(f"DEBUG: Translator interne src_filenames nach Instanziierung: {translator.config.src_filenames}", file=sys.stderr)
                print(f"DEBUG: Translator interne src_dir nach Instanziierung: {translator.config.src_dir}", file=sys.stderr)

                # Rufe die Hauptmethode des Übersetzers auf, um die Übersetzung zu starten.
                translator.main() 
                
            except Exception as e:
                print(f"Fehler während der Übersetzung: {e}", file=sys.stderr)
                sys.exit(1)

        if __name__ == "__main__":
            main()
    '''))