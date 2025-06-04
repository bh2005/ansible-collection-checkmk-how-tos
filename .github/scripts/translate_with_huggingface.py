# .github/scripts/translate_with_huggingface.py
import os
import sys
import yaml
import glob
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk # <-- Neu: Für Satzsegmentierung
"""
# Lade den Punkt-Tokenisierer für nltk einmalig
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt', quiet=True) # download, if not already present
"""
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
    "translation_models": {
        "de-en": "Helsinki-NLP/opus-mt-de-en",
        "de-fr": "Helsinki-NLP/opus-mt-de-fr",
        "de-es": "Helsinki-NLP/opus-mt-de-es",
    },
    "max_chunk_length": 400 # <-- Neu: Maximale Länge für Text-Chunks (etwas Puffer für 512 Token Limit)
}

# Globale Variable für die geladenen Übersetzer-Pipelines
TRANSLATORS = {}
# Globale Variable für Tokenizer-Objekte, benötigt für die Längenprüfung
TOKENIZERS = {} 

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
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            
            TRANSLATORS[target_lang] = pipeline("translation", model=model, tokenizer=tokenizer, device=-1) 
            TOKENIZERS[target_lang] = tokenizer # Speichere den Tokenizer
            print(f"Modell {model_name} erfolgreich geladen.")
        except Exception as e:
            print(f"FEHLER: Modell {model_name} konnte nicht geladen werden: {e}. Diese Sprache wird übersprungen.", file=sys.stderr)
            TRANSLATORS[target_lang] = None 
            TOKENIZERS[target_lang] = None


def chunk_text(text: str, max_chunk_length: int, tokenizer) -> list:
    """
    Zerlegt einen langen Text in kleinere Chunks, basierend auf Satzgrenzen
    und dem Token-Limit des Modells.
    """
    if not text.strip():
        return [""]

    sentences = nltk.sent_tokenize(text, language=CONFIG['src_language'])
    chunks = []
    current_chunk_sentences = []
    current_chunk_length = 0

    for sentence in sentences:
        # Schätze die Token-Länge des Satzes (nicht perfekt, aber ausreichend)
        sentence_tokens_length = len(tokenizer.encode(sentence))

        if current_chunk_length + sentence_tokens_length <= max_chunk_length:
            current_chunk_sentences.append(sentence)
            current_chunk_length += sentence_tokens_length
        else:
            # Wenn der aktuelle Satz den Chunk überfüllt, füge den bisherigen Chunk hinzu
            if current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
            
            # Starte einen neuen Chunk mit dem aktuellen Satz
            current_chunk_sentences = [sentence]
            current_chunk_length = sentence_tokens_length
            
            # Falls ein einzelner Satz bereits zu lang ist, teilen wir ihn notfalls per Zeichen
            # Dies sollte selten vorkommen, aber als Fallback
            if sentence_tokens_length > max_chunk_length:
                print(f"WARNUNG: Einzelner Satz ist länger als max_chunk_length ({sentence_tokens_length} > {max_chunk_length}). Er wird abgeschnitten.", file=sys.stderr)
                # Hier könnte man komplexere Logik einbauen, um den Satz zu zerlegen.
                # Für den Anfang lassen wir die Hugging Face Pipeline das Abschneiden übernehmen.
                # Oder man würde ihn in feste Zeichen-Chunks zerlegen (schlechter für Qualität).
                # Hier lassen wir ihn erstmal als eigenen Chunk, die Pipeline wird ihn kappen.
                chunks.append(" ".join(current_chunk_sentences)) # Füge den zu langen Satz als eigenen Chunk hinzu
                current_chunk_sentences = [] # Setze den aktuellen Chunk zurück
                current_chunk_length = 0
    
    # Füge den letzten verbleibenden Chunk hinzu
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))
    
    return chunks

def translate_text(text: str, src_lang: str, target_lang: str) -> str:
    """Übersetzt einen Text mit Hugging Face, unter Berücksichtigung von Chunking."""
    if not text.strip():
        return ""

    translator = TRANSLATORS.get(target_lang)
    tokenizer = TOKENIZERS.get(target_lang)

    if not translator or not tokenizer:
        print(f"Fehler: Übersetzer oder Tokenizer für {target_lang} nicht verfügbar.", file=sys.stderr)
        return f"[[Übersetzungsfehler: Übersetzer/Tokenizer nicht initialisiert für {target_lang}]] {text}"

    # Chunking anwenden
    chunks = chunk_text(text, CONFIG['max_chunk_length'], tokenizer)
    translated_chunks = []

    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append("")
            continue
            
        print(f"  Übersetze Chunk {i+1}/{len(chunks)} nach {target_lang} (Länge: {len(tokenizer.encode(chunk))} Tokens)...")
        try:
            # WICHTIG: Hier setzen wir max_length in der Pipeline, um das Modell nicht zu überfordern.
            # Dies ist die Obergrenze für die AUSGABE. Die Eingabe wird durch unser Chunking kontrolliert.
            translated_result = translator(chunk, max_length=CONFIG['max_chunk_length'] + 100) # +100 für möglichen Textzuwachs
            translated_chunk = translated_result[0]['translation_text']
            translated_chunks.append(translated_chunk)
        except Exception as e:
            print(f"FEHLER bei Chunk-Übersetzung nach {target_lang} (Chunk {i+1}): {e}", file=sys.stderr)
            translated_chunks.append(f"[[Chunk-Übersetzungsfehler: {e}]] {chunk}")

    return "\n\n".join(translated_chunks) # Füge die übersetzten Chunks wieder zusammen

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
        if TRANSLATORS.get(target_lang) is None:
            print(f"Überspringe {base_filename} nach {target_lang}, da Übersetzer nicht initialisiert wurde.", file=sys.stderr)
            continue

        target_dir = os.path.join(config['output_dir'], target_lang, relative_dir)
        os.makedirs(target_dir, exist_ok=True)
        
        target_file_path = os.path.join(target_dir, base_filename)
        
        translated_content = translate_text(main_content, config['src_language'], target_lang)

        output_content = ""
        if front_matter:
            output_content += "---\n"
            output_content += yaml.dump(front_matter, allow_unicode=True, default_flow_style=False)
            output_content += "---\n"
        
        if config['insert_warnings'] and target_lang in config['warnings_mapping']:
            output_content += config['warnings_mapping'][target_lang] + "\n\n"
        
        output_content += translated_content

        with open(target_file_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Übersetzt nach {target_lang}: {target_file_path}")

def main():
    # Lade Konfiguration aus config.yaml
    config_file_path = 'config.yaml'
    # Wenn config.yaml im selben Verzeichnis wie das Skript liegt:
    config_file_path = os.path.join(os.path.dirname(__file__), 'config.yaml') # <-- Dies ist der korrigierte Pfad für config.yaml, wenn es im Skript-Ordner liegt.
    
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
        print(f"WARNUNG: Konfigurationsdatei '{config_file_path}' nicht gefunden. Verwende Standardkonfiguration.", file=sys.stderr)
    
    initialize_translators(CONFIG)

    src_dir = CONFIG['src_dir']
    
    # Finde alle Markdown-Dateien im Quellverzeichnis (rekursiv, falls Unterordner vorhanden)
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