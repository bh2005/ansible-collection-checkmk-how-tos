import os
import sys
import yaml
import argostranslate.translate
from pathlib import Path

# Dieses Skript geht davon aus, dass die benötigten Argos-Modelle
# bereits im GitHub Actions Workflow installiert wurden.

def load_config():
    """Lädt die Konfiguration aus der config.yaml-Datei."""
    print("Lade config.yaml...")
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("FEHLER: config.yaml nicht gefunden!", file=sys.stderr)
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"FEHLER: Fehler beim Parsen von config.yaml: {e}", file=sys.stderr)
        sys.exit(1)

def chunk_text(text: str, max_length: int) -> list:
    """Teilt Text in handhabbare Chunks basierend auf Zeilenumbrüchen."""
    if not text or not text.strip():
        return [""]
    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""
    for line in text.splitlines(keepends=True):
        if len(current_chunk) + len(line) <= max_length:
            current_chunk += line
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = line
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def load_translation_models(src_lang, target_langs, pivot_lang="en"):
    """
    Lädt alle benötigten Übersetzungsmodelle einmalig vorab.
    Gibt ein Dictionary zurück, das für jede Zielsprache entweder ein
    direktes Modell oder ein Tupel aus zwei Pivot-Modellen enthält.
    """
    print("Lade Übersetzungsmodelle vorab...")
    loaded_models = {}
    
    # Lade das Pivot-Modell von der Quelle zur Pivot-Sprache, falls nötig
    src_to_pivot_model = None
    try:
        src_to_pivot_model = argostranslate.translate.get_translation_from_codes(src_lang, pivot_lang)
    except Exception as e:
        print(f"WARNUNG: Konnte das Quell-zu-Pivot-Modell ({src_lang}->{pivot_lang}) nicht laden: {e}", file=sys.stderr)

    for lang in target_langs:
        # 1. Versuche direkte Übersetzung
        try:
            model = argostranslate.translate.get_translation_from_codes(src_lang, lang)
            loaded_models[lang] = model
            print(f"  -> Modell für direkte Übersetzung geladen: {src_lang}->{lang}")
            continue
        except Exception:
            pass # Weiter zur Pivot-Logik

        # 2. Versuche Pivot-Übersetzung
        if lang != pivot_lang and src_to_pivot_model:
            try:
                pivot_to_target_model = argostranslate.translate.get_translation_from_codes(pivot_lang, lang)
                loaded_models[lang] = (src_to_pivot_model, pivot_to_target_model)
                print(f"  -> Modelle für Pivot-Übersetzung geladen: {src_lang}->{pivot_lang}->{lang}")
            except Exception as e:
                print(f"FEHLER: Pivot-Modell {pivot_lang}->{lang} nicht gefunden: {e}", file=sys.stderr)
                loaded_models[lang] = None
        else:
            print(f"WARNUNG: Kein direktes oder Pivot-Modell für {src_lang}->{lang} verfügbar.", file=sys.stderr)
            loaded_models[lang] = None
            
    return loaded_models

def translate_content(text: str, model, max_chunk_length: int) -> str:
    """Übersetzt Text mit einem oder zwei (Pivot) vorab geladenen Modellen."""
    if not text or not text.strip() or not model:
        return text or ""

    # Pivot-Übersetzung
    if isinstance(model, tuple):
        model1, model2 = model
        # Erster Schritt der Pivot-Übersetzung
        chunks1 = chunk_text(text, max_chunk_length)
        translated_chunks1 = [model1.translate(chunk) for chunk in chunks1]
        intermediate_text = "".join(translated_chunks1)
        
        # Zweiter Schritt der Pivot-Übersetzung
        chunks2 = chunk_text(intermediate_text, max_chunk_length)
        translated_chunks2 = [model2.translate(chunk) for chunk in chunks2]
        return "".join(translated_chunks2)
    
    # Direkte Übersetzung
    else:
        chunks = chunk_text(text, max_chunk_length)
        translated_chunks = [model.translate(chunk) for chunk in chunks]
        return "".join(translated_chunks)

def main():
    """Hauptfunktion des Übersetzungsskripts."""
    config = load_config()
    src_dir = Path(config.get("src_dir", "DE"))
    output_base_dir = Path(config.get("output_dir", "DEV"))
    src_lang = config.get("src_language", "de")
    target_langs = config.get("target_langs", [])
    max_chunk_length = config.get("max_chunk_length", 2000)

    # Lade alle Modelle, die für die konfigurierten Sprachen benötigt werden
    translation_models = load_translation_models(src_lang, target_langs)

    if not src_dir.exists():
        print(f"Quellordner {src_dir} existiert nicht, beende.", file=sys.stderr)
        sys.exit(1)

    for md_file_path in src_dir.rglob("*.md"):
        relative_path = md_file_path.relative_to(src_dir)
        print(f"\nVerarbeite Datei: {md_file_path}")

        content = md_file_path.read_text(encoding="utf-8")
        front_matter = {}
        main_content = content

        if content.startswith('---'):
            try:
                parts = content.split('---', 2)
                if len(parts) > 2:
                    front_matter = yaml.safe_load(parts[1]) or {}
                    main_content = parts[2].strip()
            except yaml.YAMLError as e:
                print(f"WARNUNG: YAML-Fehler in {md_file_path}: {e}", file=sys.stderr)
        
        for lang in target_langs:
            model = translation_models.get(lang)
            if not model:
                print(f"  -> Überspringe Sprache {lang} für {md_file_path.name}, da kein Modell geladen werden konnte.")
                continue

            target_dir = output_base_dir / lang / relative_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = target_dir / md_file_path.name
            
            print(f"  -> Übersetze nach {lang} für {output_file_path}")

            # Übersetze Front Matter
            translated_front_matter = {}
            transparent_keys = config.get("front_matter_transparent_keys", [])
            key_value_keys = config.get("front_matter_key_value_keys", [])
            for key, value in front_matter.items():
                if key in transparent_keys or not isinstance(value, str) or not value.strip():
                    translated_front_matter[key] = value
                else:
                    # Alle anderen Keys werden übersetzt, nicht nur die in key_value_keys
                    translated_front_matter[key] = translate_content(value, model, max_chunk_length)

            # Übersetze den Hauptinhalt
            translated_main_content = translate_content(main_content, model, max_chunk_length)

            # Baue den neuen Inhalt zusammen
            output_content_parts = []
            if translated_front_matter:
                output_content_parts.append("---")
                # allow_unicode=True ist wichtig für Umlaute etc.
                output_content_parts.append(yaml.safe_dump(translated_front_matter, allow_unicode=True, sort_keys=False).strip())
                output_content_parts.append("---")
            
            if config.get("insert_warnings", True):
                warnings_mapping = config.get("warnings_mapping", {})
                if lang in warnings_mapping:
                    output_content_parts.append("\n" + warnings_mapping[lang])

            output_content_parts.append("\n" + translated_main_content)
            
            final_output = "\n".join(output_content_parts).strip() + "\n"

            try:
                output_file_path.write_text(final_output, encoding="utf-8")
            except Exception as e:
                print(f"FEHLER beim Schreiben der Datei {output_file_path}: {e}", file=sys.stderr)

    print("\nÜbersetzungsprozess abgeschlossen.")

if __name__ == "__main__":
    main()
