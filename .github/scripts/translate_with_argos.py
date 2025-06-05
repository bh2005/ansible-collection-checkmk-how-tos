import os
import yaml
import argostranslate.package
import argostranslate.translate
from pathlib import Path
import sys

# Globale Menge für installierte Pakete
# Dies hilft, redundante Installationsversuche zu vermeiden.
installed_packages = set()

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

def install_package(from_code: str, to_code: str) -> bool:
    """
    Versucht, ein Argos Translate Sprachpaket aus den verfügbaren Online-Paketen zu installieren.
    Gibt True bei Erfolg, False bei Misserfolg zurück.
    """
    pkg_key = f"{from_code}->{to_code}"
    if pkg_key in installed_packages:
        print(f"Paket {pkg_key} bereits installiert, überspringe.")
        return True
    
    print(f"Versuche, Paket {from_code}->{to_code} herunterzuladen und zu installieren...")
    try:
        # Aktualisiere den Paketindex, um die neuesten verfügbaren Pakete zu sehen
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()

        for pkg in available_packages:
            if pkg.from_code == from_code and pkg.to_code == to_code:
                pkg.install()
                installed_packages.add(pkg_key)
                print(f"Paket {pkg_key} erfolgreich installiert.")
                return True
        print(f"Paket {pkg_key} online nicht gefunden.")
        return False
    except Exception as e:
        print(f"FEHLER bei der Installation von {pkg_key} aus dem Online-Index: {e}", file=sys.stderr)
        return False

def install_manual_package(from_code: str, to_code: str, model_path: str) -> bool:
    """
    Versucht, ein Argos Translate Sprachpaket aus einer lokalen .argosmodel-Datei zu installieren.
    Gibt True bei Erfolg, False bei Misserfolg zurück.
    """
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
        print(f"FEHLER bei der manuellen Installation von {pkg_key} von {model_path}: {e}", file=sys.stderr)
        return False

def translate_text(text: str, from_code: str, to_code: str, pivot_lang: str = "en") -> str:
    """
    Übersetzt Text mithilfe von Argos Translate. Versucht eine direkte Übersetzung,
    andernfalls wird über eine Pivot-Sprache (standardmäßig Englisch) übersetzt.
    """
    if not text.strip():
        return ""

    print(f"Übersetze von {from_code} nach {to_code}...")

    # Zuerst versuchen, direkt zu übersetzen
    try:
        if install_package(from_code, to_code):
            translated_text = argostranslate.translate.translate(text, from_code, to_code)
            print(f"Direkte Übersetzung {from_code}->{to_code} erfolgreich.")
            return translated_text
    except Exception as e:
        print(f"WARNUNG: Direkte Übersetzung {from_code}->{to_code} fehlgeschlagen: {e}", file=sys.stderr)

    # Wenn direkte Übersetzung fehlschlägt und es keine Pivot-Übersetzung ist, versuche zu pivotieren
    if from_code != pivot_lang and to_code != pivot_lang:
        print(f"Kein direktes Paket für {from_code}->{to_code} gefunden oder fehlgeschlagen, pivotere über {pivot_lang}...")
        
        # Modelle für die Pivot-Übersetzung heruntergeladen und im 'models/' Ordner abgelegt
        # Stelle sicher, dass die Dateinamen hier mit denen im translate.yml-Workflow übereinstimmen
        pivot_to_target_model_path = None
        if to_code == "fr":
            pivot_to_target_model_path = f"models/translate-{pivot_lang}_{to_code}-1_9.argosmodel"
        elif to_code == "es":
            pivot_to_target_model_path = f"models/translate-{pivot_lang}_{to_code}-1_0.argosmodel"
        
        if pivot_to_target_model_path and \
           install_package(from_code, pivot_lang) and \
           install_manual_package(pivot_lang, to_code, pivot_to_target_model_path):
            try:
                pivot_text = argostranslate.translate.translate(text, from_code, pivot_lang)
                translated_text = argostranslate.translate.translate(pivot_text, pivot_lang, to_code)
                print(f"Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code} erfolgreich.")
                return translated_text
            except Exception as e:
                print(f"FEHLER bei Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code}: {e}", file=sys.stderr)
        else:
            print(f"WARNUNG: Pivot-Modelle für {from_code}->{pivot_lang} oder {pivot_lang}->{to_code} konnten nicht installiert werden. Überprüfen Sie den 'models/' Ordner und die Namen.", file=sys.stderr)

    print(f"Übersetzung {from_code}->{to_code} fehlgeschlagen oder nicht möglich, gebe Originaltext zurück.", file=sys.stderr)
    return text # Fallback: Originaltext zurückgeben, wenn Übersetzung fehlschlägt

def main():
    """Hauptfunktion des Übersetzungsskripts."""
    config = load_config()
    source_dir = Path(config.get("src_dir", "DE")) # Verwendet 'DE' als Standard
    output_base_dir = Path(config.get("output_dir", "DEV")) # Verwendet 'DEV' als Standard
    target_langs = config.get("target_langs", ["en", "fr", "es"])
    
    # Neu aus config.yaml
    front_matter_transparent_keys = config.get("front_matter_transparent_keys", [])
    front_matter_key_value_keys = config.get("front_matter_key_value_keys", [])
    insert_warnings = config.get("insert_warnings", True)
    warnings_mapping = config.get("warnings_mapping", {})

    print(f"Zielsprachen: {target_langs}")
    print(f"Quellverzeichnis: {source_dir}")
    print(f"Zielverzeichnis: {output_base_dir}")

    if not source_dir.exists():
        print(f"Quellordner {source_dir} existiert nicht, beende.")
        sys.exit(1) # Beende mit Fehlercode, da die Quelle nicht existiert

    # Iteriere über alle Markdown-Dateien im Quellverzeichnis (und Unterverzeichnissen)
    for md_file_path in source_dir.rglob("*.md"): # rglob für rekursive Suche
        relative_path = md_file_path.relative_to(source_dir)
        print(f"\nVerarbeite Datei: {md_file_path}")

        # Lese Inhalt und trenne Front Matter
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
                print(f"WARNUNG: YAML Fehler in {md_file_path}: {e}. Ignoriere Front Matter.", file=sys.stderr)

        for lang in target_langs:
            target_dir = output_base_dir / lang / relative_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = target_dir / md_file_path.name
            
            print(f"  Übersetze nach {lang} für {output_file_path}")
            
            # Übersetzung des Hauptinhalts
            translated_main_content = translate_text(main_content, config['src_language'], lang)

            # Baue den neuen Inhalt zusammen
            output_content_parts = []

            # Füge Front Matter hinzu (unverändert)
            if front_matter:
                output_content_parts.append("---")
                # Hier können Sie Logik für transparent_keys und key_value_keys implementieren,
                # falls diese im Front Matter übersetzt werden sollen.
                # Aktuell wird das Front Matter unverändert übernommen.
                output_content_parts.append(yaml.safe_dump(front_matter, allow_unicode=True, default_flow_style=False).strip())
                output_content_parts.append("---")
            
            # Füge Warnhinweis hinzu
            if insert_warnings and lang in warnings_mapping:
                output_content_parts.append(warnings_mapping[lang])
                output_content_parts.append("") # Leere Zeile nach Warnung

            # Füge übersetzten Hauptinhalt hinzu
            output_content_parts.append(translated_main_content)

            final_output = "\n".join(output_content_parts).strip() + "\n" # Sicherstellen, dass die Datei mit einem Newline endet

            # Schreibe die übersetzte Datei
            try:
                output_file_path.write_text(final_output, encoding="utf-8")
                print(f"  Fertig übersetzt nach {lang}: {output_file_path}")
            except Exception as e:
                print(f"FEHLER beim Schreiben der Datei {output_file_path}: {e}", file=sys.stderr)

    print("Übersetzungsprozess abgeschlossen.")

if __name__ == "__main__":
    main()

