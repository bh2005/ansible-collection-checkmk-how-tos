import os
import sys
import yaml
import glob
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import spacy # NEU: Importiere spaCy

# Standardkonfiguration (wird aus config.yaml geladen)
CONFIG = {
    "src_language": "de",
    "target_langs": ["en", "fr", "es"],
    "src_dir": "DE",
    "output_dir": "DEV",
    "insert_warnings": True,
    "warnings_mapping": {
        "en": "Warning: This page is translated by machine, which may lead to poor quality or incorrect information, please read with caution!",
        "fr": "Avertissement : Cette page est traduite par machine, ce qui peut entraîner une mauvaise qualité ou des informations incorrectes, veuillez lire avec prudence !",
        "es": "Advertencia: ¡Esta página está traducida por máquina, lo que puede llevar a baja qualität oder information incorrecta, lea con precaución!"
    },
    "translation_models": {
        "de-en": "Helsinki-NLP/opus-mt-de-en",
        "de-fr": "Helsinki-NLP/opus-mt-de-fr",
        "de-es": "Helsinki-NLP/opus-mt-de-es",
    },
    "max_chunk_length": 100  # Will be updated from config.yaml
}

TRANSLATORS = {}
TOKENIZERS = {}
SPACY_NLP_MODEL = None # Globale Variable für das spaCy Modell

def initialize_translators(config: dict):
    """Initialisiert die Übersetzer-Pipelines und das spaCy Modell für alle Zielsprachen."""
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
                device=-1 # Use CPU by default in CI/CD
            )
            TOKENIZERS[target_lang] = tokenizer
            print(f"Modell {model_name} erfolgreich geladen.")
        except Exception as e:
            print(f"FEHLER: Modell {model_name} konnte nicht geladen werden: {e}. Sprache '{target_lang}' wird übersprungen.", file=sys.stderr)
            TRANSLATORS[target_lang] = None
            TOKENIZERS[target_lang] = None
    
    # NEU: Lade spaCy Modell für die Quellsprache
    try:
        global SPACY_NLP_MODEL
        spacy_model_name = f"{src_lang}_core_news_sm" # Beispiel: de_core_news_sm
        print(f"Lade spaCy Modell: {spacy_model_name} für Satzsegmentierung...")
        SPACY_NLP_MODEL = spacy.load(spacy_model_name)
        print(f"spaCy Modell '{spacy_model_name}' erfolgreich geladen.")
    except Exception as e:
        print(f"FEHLER: spaCy Modell konnte nicht geladen werden: {e}. Die Satzsegmentierung wird auf Regex-Fallback beschränkt.", file=sys.stderr)
        SPACY_NLP_MODEL = None


def chunk_text(text: str, max_chunk_length_config: int, tokenizer) -> list:
    """
    Zerlegt einen langen Text in kleinere Chunks, basierend auf Satzgrenzen
    und dem Token-Limit des Modells. Verwendet spaCy für die Satzsegmentierung.
    max_chunk_length_config: Der Wert von max_chunk_length aus CONFIG (Benutzerpräferenz).
    """
    if not text.strip():
        return [""]

    sentences = []
    # NEU: Verwende spaCy für die Satzsegmentierung
    if SPACY_NLP_MODEL:
        try:
            doc = SPACY_NLP_MODEL(text)
            sentences = [sent.text for sent in doc.sents]
        except Exception as e:
            print(f"WARNUNG: spaCy Satzsegmentierung fehlgeschlagen ({e}). Fallback auf Regex-basierte Segmentierung.", file=sys.stderr)
            sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    else:
        print("WARNUNG: spaCy Modell nicht geladen. Fallback auf Regex-basierte Segmentierung für Satzsegmentierung.", file=sys.stderr)
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    # Fallback für den Fall, dass spaCy oder Regex keine Sätze findet
    if not sentences or (len(sentences) == 1 and len(sentences[0]) == len(text.strip())):
        print("WARNUNG: Satzsegmentierung unzureichend. Fallback auf Zeichen-basierte Segmentierung.", file=sys.stderr)
        # Calculate effective max chunk length based on model's actual max_length
        effective_max_chunk_length = min(max_chunk_length_config, tokenizer.model_max_length - 50)
        sentences = [text[i:i + effective_max_chunk_length] for i in range(0, len(text), effective_max_chunk_length)]


    chunks = []
    current_chunk_sentences = []
    
    # Effektive maximale Chunk-Länge basierend auf der tatsächlichen max_length des Modells
    # und einem Puffer für spezielle Tokens. Dies ist die harte Grenze für Chunks.
    # Opus-MT Modelle haben typischerweise eine max_length von 512. Ein Puffer von 50 ist konservativ.
    effective_max_chunk_length = min(max_chunk_length_config, tokenizer.model_max_length - 50) 

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Überprüfe die Token-Länge des aktuellen Satzes
        sentence_tokens_length = len(tokenizer.encode(sentence, truncation=True, max_length=effective_max_chunk_length))
        
        # Wenn ein einzelner Satz bereits zu lang für einen Chunk ist, füge ihn als separaten Chunk hinzu
        # und er wird vom Tokenizer des Modells gekürzt, wenn er an die Pipeline übergeben wird.
        if sentence_tokens_length > effective_max_chunk_length:
            if current_chunk_sentences: # Füge den vorherigen Chunk hinzu, falls nicht leer
                chunks.append(" ".join(current_chunk_sentences))
                current_chunk_sentences = []
            chunks.append(sentence) # Füge den langen Satz als eigenen Chunk hinzu
            print(f"WARNUNG: Einzelner Satz ist länger als effektive max_chunk_length ({sentence_tokens_length} > {effective_max_chunk_length}). Er wird vom Modell gekürzt.", file=sys.stderr)
            continue # Gehe zum nächsten Satz

        # Versuche, den Satz zum aktuellen Chunk hinzuzufügen
        prospective_chunk_content = " ".join(current_chunk_sentences + [sentence])
        
        # Überprüfe die Token-Länge des potenziellen Chunks
        prospective_chunk_tokens_length = len(tokenizer.encode(prospective_chunk_content, truncation=True, max_length=effective_max_chunk_length))

        if prospective_chunk_tokens_length <= effective_max_chunk_length:
            current_chunk_sentences.append(sentence)
        else:
            # Wenn das Hinzufügen des Satzes das Limit überschreitet, schließe den aktuellen Chunk ab
            if current_chunk_sentences:
                chunks.append(" ".join(current_chunk_sentences))
            
            # Starte einen neuen Chunk mit dem aktuellen Satz
            current_chunk_sentences = [sentence]
    
    # Füge den letzten verbleibenden Chunk hinzu
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

    # Verwende die maximale Länge des Modells für die Ausgabe, da dies die absolute Grenze ist.
    # Die Eingabe-Chunking-Logik kümmert sich um die Eingabelänge.
    output_max_length = tokenizer.model_max_length 

    chunks = chunk_text(text, CONFIG['max_chunk_length'], tokenizer) # Übergabe der ursprünglichen max_chunk_length für die Chunking-Logik
    translated_chunks = []

    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_chunks.append("")
            continue
        
        # Stelle sicher, dass der an den Übersetzer übergebene Chunk innerhalb des tatsächlichen Eingabelimits des Modells liegt
        # Verwende einen kleinen Puffer für interne Tokens (z.B. 10 Tokens)
        input_max_length_for_model = tokenizer.model_max_length - 10
        chunk_tokens = tokenizer.encode(chunk, truncation=True, max_length=input_max_length_for_model) 
        chunk_to_translate = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        
        chunk_tokens_length = len(tokenizer.encode(chunk_to_translate))
        print(f"  Übersetze Chunk {i+1}/{len(chunks)} nach {target_lang} (Länge: {chunk_tokens_length} Tokens)...")
        
        try:
            # Übergabe des gekürzten Chunks und der bestimmten output_max_length
            translated_result = translator(chunk_to_translate, max_length=output_max_length)
            translated_chunks.append(translated_result[0]['translation_text'])
        except Exception as e:
            print(f"FEHLER bei Chunk-Übersetzung nach {target_lang} (Chunk {i+1}): {e}", file=sys.stderr)
            translated_chunks.append(f"[[Chunk-Übersetzungsfehler: {e}]] {chunk}")

    return "\n\n".join(translated_chunks)

def process_markdown_file(file_path: str):
    """Verarbeitet eine Markdown-Datei: Liest, übersetzt und schreibt neue Dateien."""
    print(f"\nVerarbeite Datei: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    front_matter = {}
    main_content = content

    if content.startswith('---'):
        try:
            parts = content.split('---', 2)
            if len(parts) > 2:
                front_matter = yaml.safe_load(parts[1]) or {}
                main_content = parts[2].strip()
        except yaml.YAMLError as e:
            print(f"Warnung: YAML Fehler in {file_path}: {e}", file=sys.stderr)

    base_filename = os.path.basename(file_path)
    relative_dir = os.path.relpath(os.path.dirname(file_path), CONFIG['src_dir'])

    for target_lang in CONFIG['target_langs']:
        if TRANSLATORS.get(target_lang) is None:
            print(f"Überspringe {base_filename} nach {target_lang}, da Übersetzer nicht initialisiert wurde.", file=sys.stderr)
            continue

        target_dir = os.path.join(CONFIG['output_dir'], target_lang, relative_dir)
        os.makedirs(target_dir, exist_ok=True)
        target_file_path = os.path.join(target_dir, base_filename)

        translated_content = translate_text(main_content, CONFIG['src_language'], target_lang)

        output_content = ""
        if front_matter:
            output_content += "---\n"
            output_content += yaml.safe_dump(front_matter, allow_unicode=True, default_flow_style=False)
            output_content += "---\n"
        if CONFIG['insert_warnings'] and target_lang in CONFIG['warnings_mapping']:
            output_content += CONFIG['warnings_mapping'][target_lang] + "\n\n"

        output_content += translated_content

        with open(target_file_path, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"Übersetzt nach {target_lang}: {target_file_path}")

def main():
    # Lade Konfiguration
    config_file_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    if not os.path.exists(config_file_path):
        config_file_path = 'config.yaml'

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
        process_markdown_file(md_file)

    print("Übersetzungsprozess abgeschlossen.")

if __name__ == "__main__":
    main()
