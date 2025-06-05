import argostranslate.package
import argostranslate.translate
import yaml
import os
import glob
import sys
import platform

print(f"Python-Version: {platform.python_version()}", file=sys.stdout)

def load_config():
    """Config aus config.yaml laden."""
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Oops, Config-Fehler: {e}", file=sys.stderr)
        sys.exit(1)

def install_language_packages(src_lang, target_langs):
    """Sprachpakete für Argos runterladen."""
    print("Checke Argos-Sprachpakete...", file=sys.stdout)
    available = argostranslate.package.get_available_packages()
    installed = argostranslate.package.get_installed_packages()
    for target_lang in target_langs:
        pair = f"{src_lang}-{target_lang}"
        if not any(p.from_code == src_lang and p.to_code == target_lang for p in installed):
            package = next(
                (p for p in available if p.from_code == src_lang and p.to_code == target_lang),
                None
            )
            if package:
                print(f"Installiere Paket: {pair}", file=sys.stdout)
                package.install()
            else:
                print(f"Kein Paket für {pair}, wird übersprungen.", file=sys.stderr)

def chunk_text(text, max_chunk_length):
    """Text in Chunks splitten."""
    if len(text) <= max_chunk_length:
        return [text]
    chunks = []
    current_chunk = ""
    for line in text.split("\n"):
        if len(current_chunk) + len(line) + 1 > max_chunk_length:
            chunks.append(current_chunk.strip())
            current_chunk = line
        else:
            current_chunk += "\n" + line if current_chunk else line
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def translate_text(text, src_lang, target_lang, max_chunk_length):
    """Text mit Argos übersetzen."""
    if not text.strip():
        return ""
    chunks = chunk_text(text, max_chunk_length)
    translated_chunks = []
    for i, chunk in enumerate(chunks):
        print(f"Übersetze Chunk {i+1}/{len(chunks)} nach {target_lang}...", file=sys.stdout)
        try:
            translated = argostranslate.translate.translate(chunk, from_lang=src_lang, to_lang=target_lang)
            translated_chunks.append(translated)
        except Exception as e:
            print(f"Fehler beim Übersetzen nach {target_lang}: {e}", file=sys.stderr)
            translated_chunks.append(chunk)  # Fallback: Originaltext
    return "\n\n".join(translated_chunks)

def process_markdown_file(file_path, config):
    """Markdown-Datei übersetzen und speichern."""
    print(f"\nBearbeite: {file_path}", file=sys.stdout)
    src_lang = config["src_language"]
    target_langs = config["target_langs"]
    output_dir = config["output_dir"]
    max_chunk_length = config.get("max_chunk_length", 2000)
    front_matter_transparent = config.get("front_matter_transparent_keys", [])
    front_matter_key_value = config.get("front_matter_key_value_keys", [])

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Fehler beim Lesen von {file_path}: {e}", file=sys.stderr)
        return

    front_matter = {}
    main_content = content
    if content.startswith("---"):
        try:
            parts = content.split("---", 2)
            if len(parts) > 2:
                front_matter = yaml.safe_load(parts[1]) or {}
                main_content = parts[2].strip()
        except yaml.YAMLError as e:
            print(f"YAML-Fehler in {file_path}: {e}", file=sys.stderr)

    base_filename = os.path.basename(file_path)
    relative_dir = os.path.relpath(os.path.dirname(file_path), config["src_dir"])

    for target_lang in target_langs:
        target_dir = os.path.join(output_dir, target_lang, relative_dir)
        os.makedirs(target_dir, exist_ok=True)
        target_file_path = os.path.join(target_dir, base_filename)
        print(f"Ziel: {target_file_path}", file=sys.stdout)

        # Front Matter übersetzen
        translated_front_matter = front_matter.copy()
        for key in front_matter_key_value:
            if key in front_matter:
                translated_front_matter[key] = translate_text(
                    front_matter[key], src_lang, target_lang, max_chunk_length
                )

        # Hauptinhalt übersetzen
        translated_content = translate_text(main_content, src_lang, target_lang, max_chunk_length)

        # Ausgabe zusammenbauen
        output_content = ""
        if translated_front_matter:
            output_content += "---\n"
            output_content += yaml.dump(translated_front_matter, allow_unicode=True)
            output_content += "---\n"

        if config.get("insert_warnings") and target_lang in config.get("warnings_mapping", {}):
            output_content += config["warnings_mapping"][target_lang] + "\n\n"

        output_content += translated_content

        try:
            with open(target_file_path, "w", encoding="utf-8") as f:
                f.write(output_content)
            print(f"Fertig übersetzt nach {target_lang}: {target_file_path}", file=sys.stdout)
        except Exception as e:
            print(f"Fehler beim Schreiben von {target_file_path}: {e}", file=sys.stderr)

def main():
    """Hauptlogik: Markdowns mit Argos übersetzen."""
    config = load_config()
    src_dir = config.get("src_dir", "DE")
    src_lang = config.get("src_language", "de")
    target_langs = config.get("target_langs", ["en"])

    install_language_packages(src_lang, target_langs)

    markdown_files = glob.glob(os.path.join(src_dir, "**", "*.md"), recursive=True)
    if not markdown_files:
        print(f"Keine Markdowns in {src_dir} gefunden. Nix los!", file=sys.stderr)
        sys.exit(0)

    print(f"Gefundene Dateien: {markdown_files}", file=sys.stdout)
    for md_file in markdown_files:
        process_markdown_file(md_file, config)

    print("Übersetzung durch, alles klar!", file=sys.stdout)

if __name__ == "__main__":
    main()