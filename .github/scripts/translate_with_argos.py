import os
import yaml
import argostranslate.package
import argostranslate.translate
from pathlib import Path
import sys

# Globale Menge für installierte Pakete
installed_packages = set()

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

def install_package(from_code: str, to_code: str) -> bool:
    """Installiert ein Argos-Paket online."""
    pkg_key = f"{from_code}->{to_code}"
    if pkg_key in installed_packages:
        print(f"Paket {pkg_key} bereits installiert, überspringe.")
        return True
    print(f"Installiere Paket: {from_code}->{to_code}")
    try:
        # Nur einmal Index aktualisieren
        if not hasattr(install_package, "index_updated"):
            argostranslate.package.update_package_index()
            install_package.index_updated = True
        for pkg in argostranslate.package.get_available_packages():
            if pkg.from_code == from_code and pkg.to_code == to_code:
                pkg.install()
                installed_packages.add(pkg_key)
                print(f"Paket {pkg_key} erfolgreich installiert.")
                return True
        print(f"Paket {pkg_key} nicht verfügbar.")
        return False
    except Exception as e:
        print(f"FEHLER bei Installation von {pkg_key}: {e}", file=sys.stderr)
        return False

def install_manual_package(from_code: str, to_code: str, model_path: str) -> bool:
    """Installiert ein Argos-Paket lokal."""
    pkg_key = f"{from_code}->{to_code}"
    if pkg_key in installed_packages:
        print(f"Manuelles Paket {pkg_key} bereits installiert, überspringe.")
        return True
    print(f"Installiere manuelles Paket: {from_code}->{to_code} von {model_path}")
    try:
        if os.path.exists(model_path):
            argostranslate.package.install_from_path(model_path)
            installed_packages.add(pkg_key)
            print(f"Manuelles Paket {pkg_key} erfolgreich installiert.")
            return True
        print(f"Manuelles Paket {model_path} nicht gefunden.")
        return False
    except Exception as e:
        print(f"FEHLER bei Installation von {pkg_key}: {e}", file=sys.stderr)
        return False

def chunk_text(text: str, max_length: int) -> list:
    """Teilt Text in Chunks von max_length Zeichen."""
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
    """Übersetzt Text, ggf. mit Chunking und Pivoting."""
    if not text.strip():
        return ""
    print(f"Übersetze von {from_code} nach {to_code}...")
    try:
        model_path = f"models/{from_code}_{to_code}_1.0.argosmodel"
        if to_code == "fr":
            model_path = f"models/{from_code}_{to_code}_1.9.argosmodel"
        if install_package(from_code, to_code) or install_manual_package(from_code, to_code, model_path):
            chunks = chunk_text(text, max_chunk_length)
            translated_chunks = [argostranslate.translate.translate(chunk, from_code, to_code) for chunk in chunks]
            print(f"Direkte Übersetzung {from_code}->{to_code} erfolgreich.")
            return "".join(translated_chunks)
        elif from_code != pivot_lang and to_code != pivot_lang:
            print(f"Kein direktes Paket für {from_code}->{to_code}, pivotere über {pivot_lang}...")
            pivot_model_path = f"models/{from_code}_{pivot_lang}_1.0.argosmodel"
            target_model_path = f"models/{pivot_lang}_{to_code}_1.9.argosmodel" if to_code == "fr" else f"models/{pivot_lang}_{to_code}_1.0.argosmodel"
            if (install_package(from_code, pivot_lang) or install_manual_package(from_code, pivot_lang, pivot_model_path)) and \
               install_manual_package(pivot_lang, to_code, target_model_path):
                chunks = chunk_text(text, max_chunk_length)
                pivot_chunks = [argostranslate.translate.translate(chunk, from_code, pivot_lang) for chunk in chunks]
                pivot_text = "".join(pivot_chunks)
                target_chunks = chunk_text(pivot_text, max_chunk_length)
                translated_chunks = [argostranslate.translate.translate(chunk, pivot_lang, to_code) for chunk in target_chunks]
                print(f"Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code} erfolgreich.")
                return "".join(translated_chunks)
        print(f"Übersetzung {from_code}->{to_code} fehlgeschlagen, Originaltext zurück.", file=sys.stderr)
        return text
    except Exception as e:
        print(f"FEHLER bei Übersetzung {from_code}->{to_code}: {e}", file=sys.stderr)
        return text

def main():
    """Hauptfunktion für Übersetzung."""
    config = load_config()
    src_dir = Path(config.get("src_dir", "DE"))
    output_dir = Path(config.get("output_dir", "DEV"))
    src_lang = config.get("src_language", "de")
    target_langs = config.get("target_langs", ["en", "fr", "es"])
    insert_warnings = config.get("insert_warnings", True)
    warnings_mapping = config.get("warnings_mapping", {})
    transparent_keys = config.get("front_matter_transparent_keys", [])
    key_value_keys = config.get("front_matter_key_value_keys", [])
    max_chunk_length = config.get("max_chunk_length", 2000)

    print(f"Quellverzeichnis: {src_dir}, Zielverzeichnis: {output_dir}, Zielsprachen: {target_langs}")

    if not src_dir.exists():
        print(f"Quellordner {src_dir} existiert nicht, beende.", file=sys.stderr)
        sys.exit(1)

    for md_file_path in src_dir.rglob("*.md"):
        relative_path = md_file_path.relative_to(src_dir)
        print(f"\nVerarbeite Datei: {md_file_path}")

        # Lese und parse Front Matter
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
            target_dir = output_dir / lang / relative_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            output_file = target_dir / md_file_path.name
            print(f"  Übersetze nach {lang} für {output_file}")

            # Übersetze Front Matter (key_value_keys)
            translated_front_matter = {}
            for key, value in front_matter.items():
                if key in transparent_keys or not isinstance(value, str):
                    translated_front_matter[key] = value
                elif key in key_value_keys:
                    translated_front_matter[key] = translate_text(value, src_lang, lang, max_chunk_length)
                else:
                    translated_front_matter[key] = value

            # Übersetze Hauptinhalt
            translated_content = translate_text(main_content, src_lang, lang, max_chunk_length)

            # Baue Ausgabe
            output_parts = []
            if translated_front_matter:
                output_parts.append("---")
                output_parts.append(yaml.safe_dump(translated_front_matter, allow_unicode=True, default_flow_style=False).strip())
                output_parts.append("---")
            if insert_warnings and lang in warnings_mapping:
                output_parts.append(warnings_mapping[lang])
                output_parts.append("")
            output_parts.append(translated_content)

            final_output = "\n".join(output_parts).strip() + "\n"

            # Schreibe Datei
            try:
                output_file.write_text(final_output, encoding="utf-8")
                print(f"  Fertig übersetzt nach {lang}: {output_file}")
            except Exception as e:
                print(f"FEHLER beim Schreiben von {output_file}: {e}", file=sys.stderr)

    print("Übersetzungsprozess abgeschlossen.")

if __name__ == "__main__":
    main()