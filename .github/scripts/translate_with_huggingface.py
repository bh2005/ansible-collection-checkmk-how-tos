import os
import sys
import yaml
import glob
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import nltk

# Lade NLTK-Daten für Satzsegmentierung
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)

# Standardkonfiguration (Fallback, falls config.yaml fehlt)
CONFIG = {
    "src_language": "de",
    "target_langs": ["en", "fr", "es"],
    "src_dir": "DE",
    "output_dir": "DEV",
    "insert_warnings": True,
    "warnings_mapping": {
        "en": "Warning: This page is translated by machine, which may lead to poor quality or incorrect information, please read with caution!",
        "fr": "Avertissement : Cette page est traduite par machine, ce qui peut entraîner une mauvaise qualité ou des informations incorrectes, veuillez lire avec prudence !",
        "es": "Advertencia: ¡Esta página está traducida por máquina, lo que puede llevar a baja calidad o información incorrecta, lea con precaución!"
    },
    "translation_models": {
        "de-en": "Helsinki-NLP/opus-mt-de-en",
        "de-fr": "Helsinki-NLP/opus-mt-de-fr",
        "de-es": "Helsinki-NLP/opus-mt-de-es",
        # Optional: "multi": "facebook/m2m100_418M"
    },
    "max_chunk_length": 400  # Puffer für 512 Token-Limit
}

# Globale Variablen für Übersetzer und Tokenizer
TRANSLATORS = {}
TOKENIZERS = {}

def initialize_translators(config: dict):
    """Initialisiert die Übersetzer-Pipelines für alle Zielsprachen."""
    print("Initialisiere Hugging Face Übersetzer-Pipelines...")
    src_lang = config['src_language']
    use_multilingual = 'multi' in config['translation_models']

    for target_lang in config['target_langs']:
        model_key = 'multi' if use_multilingual else f"{src_lang}-{target_lang}"
        model_name = config['translation_models'].get(model_key)

        if not model_name:
            print(f"WARNUNG: Kein Modell für '{model_key}' gefunden. Sprache '{target_lang}' wird übersprungen.", file=sys.stderr)
            continue

        print(f"Lade Modell: {model_name} für {src_lang} nach {target_lang}...")
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
            TRANSLATORS[target_lang] = pipeline(
                "translation", model=model, tokenizer=tokenizer,
                src_lang=src_lang if use_multilingual else None,
                tgt_lang=target_lang if use_multilingual else None,
                device=-1
            )
            TOKENIZERS[target_lang] = tokenizer
            print(f"Modell {model_name} erfolgreich geladen.")
        except Exception as e:
            print(f"FEHLER: Modell {model_name} konnte nicht geladen werden: {e}. Sprache '{target_lang}' wird übersprungen.", file=sys.stderr)
            TRANSLATORS[target_lang] = None
            TOKENIZERS[target_lang] = None

def chunk_text(text: str, max_chunk_length: int, tokenizer) -> list:
    """Zerlegt Text in Chunks basierend auf Satzgrenzen und Token-Limit."""
    if not text.strip():
        return [""]

    sentences = nltk.sent_tokenize(text, language=CONFIG['src_language'])
    chunks = []
    current_chunk_sentences = []
    current_chunk_length = 0
    max_chunk_length = min(max_chunk_length, tokenizer.model_max_length - 50)  # Dynamischer Puffer

    for sentence in sentences:
        sentence_tokens_length = len(tokenizer.encode(sentence))

        if current_chunk_length + sentence_tokens_length <= max_chunk_length:
            current_chunk_sentences.append(sentence)
            current_chunk_length += sentence_tokens_length
        else:
            if current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
            current_chunk_sentences = [sentence]
            current_chunk_length = sentence_tokens_length

            if sentence_tokens_length > max_chunk_length:
                print(f"WARNUNG: Satz zu lang ({sentence_tokens_length} > {max_chunk_length}). Wird abgeschnitten.", file=sys.stderr)
                chunks.append(sentence)
                current_chunk_sentences = []
                current_chunk_length = 0

    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))

    return chunks

def translate_text(text: str, src_lang: str, target_lang: str) -> str:
    """Übersetzt Text mit Hugging Face, unter Berücksichtigung von Chunking."""
    if not text.strip():
        return ""

    translator = TRANSLATORS.get(target_lang)
    tokenizer = TOKENIZERS.get(target_lang)

    if not translator or not tokenizer:
        print(f"Fehler: Übersetzer/Tokenizer für {target_lang} nicht verfügbar.", file=sys.stderr)
        return f"[[Übersetzungsfehler: Kein Übersetzer für {target_lang}]] {text}"

    chunks = chunk_text(text, CONFIG['max_chunk_length'], tokenizer)
    translated_chunks = []

    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append("")
            continue
        print(f"  Übersetze Chunk {i+1}/{len(chunks)} nach {target_lang} (Länge: {len(tokenizer.encode(chunk))} Tokens)...")
        try:
            translated_result = translator(chunk, max_length=CONFIG['max_chunk_length'] + 100)
            translated_chunks.append(translated_result[0]['translation_text'])
        except Exception as e:
            print(f"FEHLER bei Chunk-Übersetzung nach {target_lang} (Chunk {i+1}): {e}", file=sys.stderr)
            translated_chunks.append(f"[[Chunk-Übersetzungsfehler: {e}]] {chunk}")

    return "\n\n".join(translated_chunks)

def process_markdown_file(file_path: str, config: dict):
    """Verarbeitet eine Markdown-Datei: Liest, übersetzt und schreibt neue Dateien."""
    print(f"Verarbeite Datei: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    front_matter = {}
    main_content = content

    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) > 2:
            try:
                front_matter = yaml.safe_load(parts[1]) or {}
                main_content = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"Warnung: YAML Fehler im Front Matter von {file_path}: {e}", file=sys.stderr)

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
    # Lade Konfiguration
    config_file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if not os.path.exists(config_file_path):
        config_file_path = 'config.yaml'  # Fallback auf Root-Verzeichnis

    loaded_config = {}
    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)
            CONFIG.update(loaded_config)
            print(f"Konfiguration aus {config_file_path} geladen.")
        except yaml.YAMLError as e:
            print(f"Fehler beim Laden von {config_file_path}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"WARNUNG: Konfigurationsdatei '{config_file_path}' nicht gefunden. Verwende Standardkonfiguration.", file=sys.stderr)

    initialize_translators(CONFIG)

    src_dir = CONFIG['src_dir']
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