import os
import yaml
import argostranslate.translate
from pathlib import Path
import sys

def load_config():
    """Lädt config.yaml."""
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
    """Teilt Text in Chunks von max_length Zeichen, basierend auf Zeilenumbrüchen."""
    if not text.strip():
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

def translate_text(text: str, from_code: str, to_code: str, max_chunk_length: int, pivot_lang: str = "en") -> str:
    """Übersetzt Text mit Argos Translate, erwartet installierte Modelle."""
    if not text.strip():
        return ""
    print(f"Übersetze von {from_code} nach {to_code}...")
    translated_chunks = []
    # Direkte Übersetzung
    try:
        direct_model = argostranslate.translate.get_translation_from_codes(from_code, to_code)
        chunks = chunk_text(text, max_chunk_length)
        for chunk in chunks:
            if not chunk.strip():
                translated_chunks.append("")
                continue
            translated_chunks.append(direct_model.translate(chunk))
        print(f"Direkte Übersetzung {from_code}->{to_code} erfolgreich.")
        return "".join(translated_chunks)
    except Exception as e:
        print(f"WARNUNG: Direkte Übersetzung {from_code}->{to_code} fehlgeschlagen ({e}).", file=sys.stderr)
    # Pivot-Übersetzung
    if from_code != pivot_lang and to_code != pivot_lang:
        print(f"Kein direktes Paket für {from_code}->{to_code}, pivotere über {pivot_lang}...")
        try:
            pivot_model = argostranslate.translate.get_translation_from_codes(from_code, pivot_lang)
            target_model = argostranslate.translate.get_translation_from_codes(pivot_lang, to_code)
            chunks = chunk_text(text, max_chunk_length)
            pivot_chunks = []
            for chunk in chunks:
                if not chunk.strip():
                    pivot_chunks.append("")
                    continue
                pivot_chunks.append(pivot_model.translate(chunk))
            final_chunks = []
            for chunk in pivot_chunks:
                if not chunk.strip():
                    final_chunks.append("")
                    continue
                final_chunks.append(target_model.translate(chunk))
            print(f"Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code} erfolgreich.")
            return "".join(final_chunks)
        except Exception as e:
            print(f"FEHLER: Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code} fehlgeschlagen: {e}. Prüfe translate.yml für Modellinstallation.", file=sys.stderr)
    print(f"FEHLER: Übersetzung {from_code}->{to_code} nicht möglich, Originaltext zurück.", file=sys.stderr)
    return text

def main():
    """Hauptfunktion des Übersetzungsskripts."""
    config = load_config()
    src_dir = Path(config.get("src_dir", "DE"))
    output_base_dir = Path(config.get("output_dir", "DEV"))
    src_lang = config.get("src_language", "de")
    target_langs = config.get("target_langs", ["en", "fr", "es"])
    insert_warnings = config.get("insert_warnings", True)
    warnings_mapping = config.get("warnings_mapping", {})
    transparent_keys = config.get("front_matter_transparent_keys", [])
    key_value_keys = config.get("front_matter_key_value_keys", [])
    max_chunk_length = config.get("max_chunk_length", 2000)

    print(f"Quellverzeichnis: {src_dir}, Zielverzeichnis: {output_base_dir}, Zielsprachen: {target_langs}")

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
                print(f"WARNUNG: YAML-Fehler in {md_file_path}: {e}. Ignoriere Front Matter.", file=sys.stderr)
        for lang in target_langs:
            target_dir = output_base_dir / lang / relative_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = target_dir / md_file_path.name
            print(f"  Übersetze nach {lang} für {output_file_path}")
            translated_front_matter = {}
            for key, value in front_matter.items():
                if key in transparent_keys or not isinstance(value, str):
                    translated_front_matter[key] = value
                else:
                    translated_front_matter[key] = translate_text(value, src_lang, lang, max_chunk_length)
            translated_main_content = translate_text(main_content, src_lang, lang, max_chunk_length)
            output_content_parts = []
            if translated_front_matter:
                output_content_parts.append("---")
                output_content_parts.append(yaml.safe_dump(translated_front_matter, allow_unicode=True, default_flow_style=False).strip())
                output_content_parts.append("---")
            if insert_warnings:
                warning = warnings_mapping.get(lang, "Warnung: Maschinenübersetzung, kann Fehler enthalten!")
                output_content_parts.append(warning)
                output_content_parts.append("")
            output_content_parts.append(translated_main_content)
            final_output = "\n".join(output_content_parts).strip() + "\n"
            try:
                output_file_path.write_text(final_output, encoding="utf-8")
                print(f"  Fertig übersetzt nach {lang}: {output_file_path}")
            except Exception as e:
                print(f"FEHLER beim Schreiben der Datei {output_file_path}: {e}", file=sys.stderr)
    print("Übersetzungsprozess abgeschlossen.")

if __name__ == "__main__":
    main()