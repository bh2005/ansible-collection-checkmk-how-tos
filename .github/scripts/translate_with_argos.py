import os
import yaml
import argostranslate.package
import argostranslate.translate
from pathlib import Path

# Globale Menge für installierte Pakete
installed_packages = set()

def load_config():
    print("Lade config.yaml...")
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def install_package(from_code, to_code):
    pkg_key = f"{from_code}->{to_code}"
    if pkg_key in installed_packages:
        print(f"Paket {pkg_key} bereits installiert, überspringe.")
        return True
    print(f"Installiere Paket: {from_code}->{to_code}")
    try:
        for pkg in argostranslate.package.get_available_packages():
            if pkg.from_code == from_code and pkg.to_code == to_code:
                pkg.install()
                installed_packages.add(pkg_key)
                print(f"Paket {pkg_key} erfolgreich installiert.")
                return True
        print(f"Paket {pkg_key} nicht verfügbar.")
        return False
    except Exception as e:
        print(f"Fehler bei Installation von {pkg_key}: {e}")
        return False

def install_manual_package(from_code, to_code, model_path):
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
        print(f"Fehler bei Installation von {pkg_key}: {e}")
        return False

def translate_text(text, from_code, to_code, pivot_lang="en"):
    print(f"Übersetze von {from_code} nach {to_code}...")
    try:
        if install_package(from_code, to_code):
            translated = argostranslate.translate.translate(text, from_code, to_code)
            print(f"Direkte Übersetzung {from_code}->{to_code} erfolgreich.")
            return translated
        elif from_code != pivot_lang and to_code != pivot_lang:
            print(f"Kein direktes Paket für {from_code}->{to_code}, pivotere über {pivot_lang}...")
            model_path = f"models/{pivot_lang}_{to_code}_1.9.argosmodel" if to_code == "fr" else f"models/{pivot_lang}_{to_code}_1.0.argosmodel"
            if install_package(from_code, pivot_lang) and install_manual_package(pivot_lang, to_code, model_path):
                pivot_text = argostranslate.translate.translate(text, from_code, pivot_lang)
                translated = argostranslate.translate.translate(pivot_text, pivot_lang, to_code)
                print(f"Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code} erfolgreich.")
                return translated
        print(f"Übersetzung {from_code}->{to_code} fehlgeschlagen, gebe Originaltext zurück.")
        return text  # Fallback
    except Exception as e:
        print(f"Fehler bei Übersetzung {from_code}->{to_code}: {e}")
        return text

def main():
    try:
        config = load_config()
        source_dir = Path("DE")
        target_langs = config.get("target_langs", ["en", "fr", "es"])
        print(f"Zielsprachen: {target_langs}")

        if not source_dir.exists():
            print("Quellordner DE existiert nicht, beende.")
            return

        for lang in target_langs:
            target_dir = Path(f"DEV/{lang}")
            target_dir.mkdir(parents=True, exist_ok=True)
            print(f"Verarbeite Sprache: {lang}, Zielordner: {target_dir}")

            for md_file in source_dir.glob("*.md"):
                print(f"Übersetze Datei: {md_file}")
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                translated = translate_text(content, "de", lang)
                output_file = target_dir / md_file.name
                with open(output_file, "w", encoding="utf-8") as f:
                    f.write(f"<!-- Auto-übersetzt nach {lang} -->\n\n{translated}")
                print(f"Fertig übersetzt nach {lang}: {output_file}")
    except Exception as e:
        print(f"Fehler in main: {e}")

if __name__ == "__main__":
    main()