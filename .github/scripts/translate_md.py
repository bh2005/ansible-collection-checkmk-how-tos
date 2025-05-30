import os
import glob
from transformers import pipeline
import re

# Übersetzungspipeline initialisieren
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-de-en")

# Verzeichnisse
input_dir = "DE"
output_dir = "EN"

# Sicherstellen, dass der Ausgabeordner existiert
os.makedirs(output_dir, exist_ok=True)

# Funktion zum Übersetzen von Text, wobei Markdown-Struktur erhalten bleibt
def translate_markdown(content):
    lines = content.split("\n")
    translated_lines = []
    
    for line in lines:
        if not line.strip() or line.startswith("#"):
            translated_lines.append(line)
            continue
        if line.startswith("```"):
            translated_lines.append(line)
            continue
        if line.startswith("- ") or line.startswith("* ") or line.startswith("1. "):
            match = re.match(r"([-*] |[0-9]+\. )(.+)", line)
            if match:
                prefix, text = match.groups()
                translated_text = translator(text, max_length=512)[0]["translation_text"]
                translated_lines.append(f"{prefix}{translated_text}")
            else:
                translated_lines.append(line)
            continue
        if line.strip():
            translated_text = translator(line, max_length=512)[0]["translation_text"]
            translated_lines.append(translated_text)
        else:
            translated_lines.append(line)
    
    return "\n".join(translated_lines)

# Alle Markdown-Dateien im DE-Ordner verarbeiten
markdown_files = glob.glob(f"{input_dir}/*.md")

for md_file in markdown_files:
    with open(md_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    translated_content = translate_markdown(content)
    
    output_file = os.path.join(output_dir, os.path.basename(md_file))
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(translated_content)