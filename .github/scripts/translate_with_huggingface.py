# .github/scripts/translate_with_huggingface.py
import os
import sys
import yaml
import glob
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM

# --- Konfiguration (wird aus config.yaml geladen, hier als Fallback/Struktur) ---
CONFIG = {
    "src_language": "de",
    "target_langs": ["en", "fr", "es"],
    "src_dir": "DE",
    "output_dir": "DEV",
    "insert_warnings": True,
    "warnings_mapping": {
        "en": "Warning: This page is translated by MACHINE, which may lead to POOR QUALITY or INCORRECT INFORMATION, please read with CAUTION!",
        "fr": "Avertissement : Cette page est traduite par MACHINE, ce qui peut entraîner une MAUVAISE QUALITÉ ou des INFORMATIONS INCORRECTES, veuillez lire avec PRUDENCE !",
        "es": "Advertencia: ¡Esta página está traducida por MÁQUINA, lo que puede llevar a BAJA CALIDAD o INFORMACIÓN INCORRECTA, lea con PRECAUCIÓN!"
    },
    # Hier definieren wir die zu verwendenden Modelle
    "translation_models": {
        "de-en": "Helsinki-NLP/opus-mt-de-en",
        "de-fr": "Helsinki-NLP/opus-mt-de-fr",
        "de-es": "Helsinki-NLP/opus-mt-de-es",
        # Füge weitere Paare hinzu, falls nötig
    }
}

# Globale Variable für die geladenen Übersetzer-Pipelines
TRANSLATORS = {}

def initialize_translators(config: dict):
    """Initialisiert die Übersetzer-Pipelines für alle Zielsprachen."""
    print("Initialisiere Hugging Face Übersetzer-Pipelines...")
    src_lang = config['src_language']
    
    for target_lang in config['target_langs']:
        model_key = f"{src_lang}-{target_lang}"
        model_name = config['translation_models'].get(model_key)
        
        if not model_name:
            print(f"WARNUNG: Kein Hugging Face Modell für '{model_key}' in der Konfiguration gefunden. Diese Sprache wird übersprungen.", file=sys.stderr)
            continue
            
        print(f"Lade Modell: {model_name} für {src_lang} nach {target_lang}...")
        try:
            # Manchmal ist es besser, Tokenizer und Modell separat zu laden
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            # Verwende die pipeline-Funktion für Einfachheit
            # device='cuda' wenn GPU verfügbar, sonst -1 für CPU
            TRANSLATORS[target_lang] = pipeline("translation", model=model, tokenizer=tokenizer, device=-1) 
            print(f"Modell {model_name} erfolgreich geladen.")
        except Exception as e:
            print(f"FEHLER: Modell {model_name} konnte nicht geladen werden: {e}. Diese Sprache wird übersprungen.", file=sys.stderr)
            TRANSLATORS[target_lang] = None # Markiere als fehlgeschlagen, um Fehler später abzufangen

def translate_text(text: str, src_lang: str, target_lang: str) -> str:
    """Übersetzt einen Text mit Hugging Face."""
    if not text.strip():
        return "" # Leere Strings nicht übersetzen

    translator = TRANSLATORS.get(target_lang)
    if not translator:
        print(f"Fehler: Übersetzer für {target_lang} nicht verfügbar.", file=sys.stderr)
        return f"[[Übersetzungsfehler: Übersetzer nicht initialisiert für {target_lang}]] {text}"

    try:
        # Die Pipeline gibt eine Liste von Dictionaries zurück, z.B. [{'translation_text': '...'}]
        translated_result = translator(text)
        translated_text = translated_result[0]['translation_text']
        return translated_text
    except Exception as e:
        print(f"Fehler bei der Übersetzung von Text nach {target_lang}: {e}", file=sys.stderr)
        return f"[[Übersetzungsfehler: {e}]] {text}"

def process_markdown_file(file_path: str, config: dict):
    """
    Verarbeitet eine einzelne Markdown-Datei:
    Liest Front Matter und Inhalt, übersetzt den Inhalt und schreibt neue Dateien.
    """
    print(f"Verarbeite Datei: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    front_matter = {}
    main_content = content

    # Einfaches Front Matter Parsing
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            try:
                front_matter = yaml.safe_load(parts[1]) or {}
                main_content = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"Warnung: YAML Fehler im Front Matter von {file_path}: {e}", file=sys.stderr)
                front_matter = {}
                main_content = content
        else:
            pass 

    base_filename = os.path.basename(file_path)
    relative_dir = os.path.relpath(os.path.dirname(file_path), config['src_dir'])

    for target_lang in config['target_langs']:
        # Überspringe Sprachen, für die kein Übersetzer geladen werden konnte
        if TRANSLATORS.get(target_lang) is None:
            print(f"Überspringe {base_filename} nach {target_lang}, da Übersetzer nicht initialisiert wurde.", file=sys.stderr)
            continue

        target_dir = os.path.join(config['output_dir'], target_lang, relative_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        target_file_path = os.path.join(target_dir, base_filename)
        
        translated_content = translate_text(main_content, config['src_language'], target_lang)

        # Front Matter wieder hinzufügen
        output_content = ""
        if front_matter:
            output_content += "---\n"
            output_content += yaml.dump(front_matter, allow_unicode=True, default_flow_style=False)
            output_content += "---\n"
        
        # Warnung hinzufügen
        if config['insert_warnings'] and target_lang in config['warnings_mapping']:
            output_content += config['warnings_mapping'][target_lang] + "\n\n"
        
        output_content += translated_content

        with open(target_file_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Übersetzt nach {target_lang}: {target_file_path}")

def main():
    # Lade Konfiguration aus config.yaml
    config_file_path = 'config.yaml'
    loaded_config = {}
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
            CONFIG.update(loaded_config)
            print("Konfiguration aus config.yaml geladen.")
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden von config.yaml: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("WARNUNG: config.yaml nicht gefunden. Verwende Standardkonfiguration.", file=sys.stderr)
    
    # Initialisiere alle benötigten Übersetzer-Pipelines
    initialize_translators(CONFIG)

    src_dir = CONFIG['src_dir']
    
    # Finde alle Markdown-Dateien im Quellverzeichnis (rekursiv, falls Unterordner vorhanden)
    # ** bedeutet beliebige Unterordner, recursive=True ist nötig
    markdown_files = glob.glob(os.path.join(src_dir, '**', '*.md'), recursive=True)
    
    if not markdown_files:
        print(f"Keine Markdown-Dateien im Verzeichnis '{src_dir}' gefunden. Nichts zu übersetzen.")
        sys.exit(0)

    print(f"Gefundene Dateien zur Übersetzung: {markdown_files}")

    for md_file in markdown_files:
        process_markdown_file(md_file, CONFIG)

    print("Übersetzungsprozess abgeschlossen.")

if __name__ == "__main__":
    main()