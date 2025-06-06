import os
import yaml
import argostranslate.translate
from pathlib import Path
import sys

# WICHTIG: Die Funktionen zur Installation von Argos Translate Paketen (install_package, install_manual_package)
# wurden aus diesem Skript entfernt. Die Installation der Modelle erfolgt nun VOR der Ausführung dieses Skripts
# im GitHub Actions Workflow (translate.yml). Dieses Skript geht davon aus, dass die benötigten Modelle bereits
# erfolgreich in der Argos Translate Umgebung des Runners installiert wurden.

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
    """
    Teilt Text in Chunks von max_length Zeichen, basierend auf Zeilenumbrüchen.
    Dies hilft, sehr lange Texte in handhabbare Stücke für die Übersetzung zu zerlegen.
    """
    if not text.strip():
        return [""] # Gib einen leeren Chunk zurück, wenn der Text leer ist

    if len(text) <= max_length:
        return [text]

    chunks = []
    current_chunk = ""
    # Teile den Text zeilenweise auf, um Absätze nicht unnötig zu trennen
    for line in text.splitlines(keepends=True):
        # Wenn die aktuelle Zeile den Chunk nicht über das Limit bringt, füge sie hinzu
        if len(current_chunk) + len(line) <= max_length:
            current_chunk += line
        else:
            # Wenn der aktuelle Chunk nicht leer ist, füge ihn zu den fertigen Chunks hinzu
            if current_chunk:
                chunks.append(current_chunk)
            # Starte einen neuen Chunk mit der aktuellen Zeile
            current_chunk = line
    
    # Füge den letzten verbleibenden Chunk hinzu
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

def translate_text(text: str, from_code: str, to_code: str, max_chunk_length: int, pivot_lang: str = "en") -> str:
    """
    Übersetzt Text mithilfe von Argos Translate.
    Diese Funktion geht davon aus, dass die benötigten Sprachpakete
    (z.B. de->en, en->fr, en->es) bereits im Runner installiert sind.
    """
    if not text.strip():
        return ""

    print(f"Übersetze von {from_code} nach {to_code}...")
    translated_chunks = []

    # Zuerst versuchen, eine direkte Übersetzung zu erhalten
    try:
        # Versuche, die direkte Übersetzung zu erhalten.
        # get_translation_from_codes wird die Pakete finden, da sie bereits im Workflow installiert wurden.
        direct_translation_model = argostranslate.translate.get_translation_from_codes(from_code, to_code)
        
        # Chunks für direkte Übersetzung erstellen
        chunks = chunk_text(text, max_chunk_length)
        
        # Übersetze jeden Chunk direkt
        for i, chunk in enumerate(chunks):
            if not chunk.strip(): # Leere Chunks überspringen, aber beibehalten
                translated_chunks.append("")
                continue
            translated_chunk = direct_translation_model.translate(chunk)
            translated_chunks.append(translated_chunk)
        
        print(f"Direkte Übersetzung {from_code}->{to_code} erfolgreich.")
        return "".join(translated_chunks)
    except Exception as e:
        # Fange Fehler ab, wenn das direkte Modell nicht gefunden wird oder die Übersetzung fehlschlägt.
        print(f"WARNUNG: Direkte Übersetzung {from_code}->{to_code} nicht verfügbar oder fehlgeschlagen ({e}). Versuche Pivot-Übersetzung.", file=sys.stderr)

    # Pivot-Übersetzung versuchen, wenn direkte Übersetzung fehlschlägt
    # (Dies gilt nur, wenn from_code und to_code nicht die Pivot-Sprache selbst sind)
    if from_code != pivot_lang and to_code != pivot_lang:
        print(f"Kein direktes Paket für {from_code}->{to_code}, pivotere über {pivot_lang}...")
        try:
            # Hole das erste Pivot-Übersetzungsmodell (z.B. DE -> EN). Modell muss installiert sein.
            pivot_to_intermediate_model = argostranslate.translate.get_translation_from_codes(from_code, pivot_lang)
            
            # Hole das zweite Pivot-Übersetzungsmodell (z.B. EN -> FR/ES). Modell muss installiert sein.
            intermediate_to_target_model = argostranslate.translate.get_translation_from_codes(pivot_lang, to_code)
            
            # Chunks des Originaltextes für den ersten Pivot-Schritt
            chunks = chunk_text(text, max_chunk_length)
            
            pivot_text_chunks = []
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    pivot_text_chunks.append("")
                    continue
                # Übersetze ersten Schritt (z.B. DE -> EN)
                pivot_text_chunks.append(pivot_to_intermediate_model.translate(chunk))
            
            # Füge die Pivot-Chunks wieder zusammen für den zweiten Übersetzungsschritt
            combined_pivot_text = "".join(pivot_text_chunks)
            
            # Chunks des Pivot-Textes für den zweiten Schritt
            target_chunks = chunk_text(combined_pivot_text, max_chunk_length)
            
            final_translated_chunks = []
            for i, chunk in enumerate(target_chunks):
                if not chunk.strip():
                    final_translated_chunks.append("")
                    continue
                # Übersetze zweiten Schritt (z.B. EN -> FR/ES)
                final_translated_chunks.append(intermediate_to_target_model.translate(chunk))
            
            print(f"Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code} erfolgreich.")
            return "".join(final_translated_chunks)
        except Exception as e:
            print(f"FEHLER bei Pivot-Übersetzung {from_code}->{pivot_lang}->{to_code}: {e}", file=sys.stderr)
    else:
        # Dieser Zweig wird erreicht, wenn from_code oder to_code die Pivot-Sprache selbst ist
        # und die direkte Übersetzung bereits oben fehlgeschlagen ist.
        # Es gibt keine weitere Pivot-Möglichkeit.
        print(f"WARNUNG: Pivot-Strategie nicht anwendbar oder Pivot-Modelle fehlen für {from_code}->{to_code}.", file=sys.stderr)

    print(f"Übersetzung {from_code}->{to_code} fehlgeschlagen oder nicht möglich, gebe Originaltext zurück.", file=sys.stderr)
    return text # Fallback: Originaltext zurückgeben, wenn Übersetzung fehlschlägt

def main():
    """Hauptfunktion des Übersetzungsskripts."""
    config = load_config()
    src_dir = Path(config.get("src_dir", "DE")) # Verwendet 'DE' als Standard
    output_base_dir = Path(config.get("output_dir", "DEV")) # Verwendet 'DEV' als Standard
    src_lang = config.get("src_language", "de")
    target_langs = config.get("target_langs", ["en", "fr", "es"])
    
    insert_warnings = config.get("insert_warnings", True)
    warnings_mapping = config.get("warnings_mapping", {})
    transparent_keys = config.get("front_matter_transparent_keys", [])
    key_value_keys = config.get("front_matter_key_value_keys", [])
    max_chunk_length = config.get("max_chunk_length", 2000) # Maximal mögliche Chunk-Länge

    print(f"Quellverzeichnis: {src_dir}, Zielverzeichnis: {output_base_dir}, Zielsprachen: {target_langs}")

    if not src_dir.exists():
        print(f"Quellordner {src_dir} existiert nicht, beende.", file=sys.stderr)
        sys.exit(1) # Beende mit Fehlercode, da die Quelle nicht existiert

    # Iteriere über alle Markdown-Dateien im Quellverzeichnis (und Unterverzeichnissen)
    for md_file_path in src_dir.rglob("*.md"): # rglob für rekursive Suche in Unterordnern
        relative_path = md_file_path.relative_to(src_dir)
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
                print(f"WARNUNG: YAML-Fehler in {md_file_path}: {e}. Ignoriere Front Matter.", file=sys.stderr)
        
        for lang in target_langs:
            target_dir = output_base_dir / lang / relative_path.parent
            target_dir.mkdir(parents=True, exist_ok=True)
            output_file_path = target_dir / md_file_path.name
            
            print(f"  Übersetze nach {lang} für {output_file_path}")

            # Übersetze Front Matter (basierend auf transparent_keys und key_value_keys)
            translated_front_matter = {}
            for key, value in front_matter.items():
                if key in transparent_keys or not isinstance(value, str):
                    # Schlüssel, die nicht übersetzt oder keine Strings sind, bleiben unverändert
                    translated_front_matter[key] = value
                elif key in key_value_keys:
                    # Schlüssel, deren Werte übersetzt werden sollen
                    translated_front_matter[key] = translate_text(value, src_lang, lang, max_chunk_length)
                else:
                    # Alle anderen String-Werte im Front Matter werden ebenfalls übersetzt
                    translated_front_matter[key] = translate_text(value, src_lang, lang, max_chunk_length)

            # Übersetze den Hauptinhalt
            translated_main_content = translate_text(main_content, src_lang, lang, max_chunk_length)

            # Baue den neuen Inhalt zusammen
            output_content_parts = []

            # Füge übersetztes Front Matter hinzu
            if translated_front_matter:
                output_content_parts.append("---")
                output_content_parts.append(yaml.safe_dump(translated_front_matter, allow_unicode=True, default_flow_style=False).strip())
                output_content_parts.append("---")
            
            # Füge Warnhinweis hinzu
            if insert_warnings and lang in warnings_mapping:
                output_content_parts.append(warnings_mapping[lang])
                output_content_parts.append("") # Leere Zeile nach Warnung für bessere Lesbarkeit

            # Füge übersetzten Hauptinhalt hinzu
            output_content_parts.append(translated_main_content)

            # Sicherstellen, dass die Datei mit einem Newline endet
            final_output = "\n".join(output_content_parts).strip() + "\n"

            # Schreibe die übersetzte Datei
            try:
                output_file_path.write_text(final_output, encoding="utf-8")
                print(f"  Fertig übersetzt nach {lang}: {output_file_path}")
            except Exception as e:
                print(f"FEHLER beim Schreiben der Datei {output_file_path}: {e}", file=sys.stderr)

    print("Übersetzungsprozess abgeschlossen.")

if __name__ == "__main__":
    main()
