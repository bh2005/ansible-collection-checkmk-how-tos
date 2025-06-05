import argostranslate.package
import argostranslate.translate
import yaml
import os
import glob
import sys
import platform

# Sichere Versionsabfrage
try:
    argos_version = argostranslate.__version__
except AttributeError:
    argos_version = "unbekannt"
print(f"Argos Translate-Version: {argos_version}, Python-Version: {platform.python_version()}", file=sys.stdout)

def load_config():
    """Config aus config.yaml laden."""
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Oops, Config-Fehler: {e}", file=sys.stderr)
        sys.exit(1)

def install_language_packages(src_lang, target_langs):
    """Sprachpakete für Argos runterladen und manuelle Pakete installieren."""
    print("Checke Argos-Sprachpakete...", file=sys.stdout)
    available = argostranslate.package.get_available_packages()
    installed = argostranslate.package.get_installed_packages()

    # Standard-Pakete installieren
    for target_lang in target_langs + ['en']:  # 'en' für Pivoting
        pair = f"{src_lang}-{target_lang}"
        if not any(p.from_code == src_lang and p.to_code == target_lang for p in installed):
            package = next(
                (p for p in available if p.from_code == src_lang and p.to_code == target_lang),
                None
            )
            if package:
                print(f"Installiere Paket: {pair}", file=sys.stdout)
                package.install()

    # Manuelle Pakete für Pivoting installieren
    manual_packages = [
        ('en', 'fr', 'models/en_fr_1.9.argosmodel'),
        ('en', 'es', 'models/en_es_1.0.argosmodel')
    ]
    for from_lang, to_lang, model_path in manual_packages:
        pair = f"{from_lang}-{to_lang}"
        if not any(p.from_code == from_lang and p.to_code == to_lang for p in installed):
            if os.path.exists(model_path):
                print(f"Installiere manuelles Paket: {pair} von {model_path}", file=sys.stdout)
                try:
                    argostranslate.package.install_from_path(model_path)
                except Exception as e:
                    print(f"Fehler bei Installation von {model_path}: {e}", file=sys.stderr)
            else:
                print(f"Manuelles Paket {model_path} nicht gefunden, überspringe {pair}.", file=sys.stderr)

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

def translate_text(text, src_lang, target_lang, max_chunk_length, pivot_lang='en'):
    """Text mit Argos übersetzen, ggf. über Pivot-Sprache."""
    if not text.strip():
        return ""

    # Direkte Übersetzung, wenn Paket verfügbar
    installed = argostranslate.package.get_installed_packages()
    if any(p.from_code == src_lang and p.to_code == target_lang for p in installed):
        chunks = chunk_text(text, max_chunk_length)
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            print(f"Übersetze Chunk {i+1}/{len(chunks)} von {src_lang} nach {target_lang}...", file=sys.stdout)
            try:
                translated = argostranslate.translate.translate(chunk, from_code=src_lang, to_code=target_lang)
                translated_chunks.append(translated)
            except Exception as e:
                print(f"Fehler beim Übersetzen von {src_lang} nach {target_lang}: {e}", file=sys.stderr)
                translated_chunks.append(chunk)  # Fallback: Originaltext
        return "\n\n".join(translated_chunks)

    # Pivoting über Englisch, wenn kein direktes Paket verfügbar
    if target_lang in ['fr', 'es'] and any(p.from_code == src_lang and p.to_code == pivot_lang for p in installed) and any(p.from_code == pivot_lang and p.to_code == target_lang for p in installed):
        print(f"Kein direktes Paket für {src_lang}->{target_lang}, pivotere über {pivot_lang}...", file=sys.stdout)
        # Schritt 1: de -> en
        en_text = translate_text(text, src_lang, pivot_lang, max_chunk_length)
        # Schritt 2: en -> fr/es
        return translate_text(en_text, pivot_lang, target_lang, max_chunk_length)

    print(f"Kein Paket für {src_lang}->{target_lang} oder Pivoting ({pivot_lang}), überspringe.", file=sys.stderr)
    return text  # Fallback: Originaltext

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