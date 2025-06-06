# So läuft’s: Automatisierter Übersetzungs-Workflow mit Hugging Face und spaCy in GitHub Actions

Hier kriegst du einen lockeren Überblick, wie dein automatisierter Übersetzungs-Workflow Markdown-Dateien mit Hugging Face-Modellen und spaCy in einer GitHub Actions-Pipeline übersetzt.

## 1. Was macht dein Workflow?

Dein Workflow nimmt technische Doku oder andere Markdown-Texte aus dem Ordner (`DE/`) und übersetzt sie automatisch ins Englische, Französische und Spanische. Die Ergebnisse landen im `DEV/`-Ordner. Das spart eine Menge Handarbeit und sorgt dafür, dass deine Inhalte überall gleich gut lokalisiert sind.

## 2. Struktur

Was gehört wohin ?!?
```text
.
├── config.yaml
├── DE/
│   ├── HowTo_Backup_and_Restore_Hostgroups_Checkmk.md
│   ├── HowTo_Create_Groups_from_CSV_with_Checkmk_Ansible.md
│   └── ...
├── .github/
│   ├── scripts/
│   │   └── translate_with_huggingface.py
│   └── workflows/
│       └── translate.yml
```

## 3. Die Hauptplayer

Dein Workflow hat drei zentrale Dateien, die super zusammenarbeiten:

### 3.1. `config.yaml` – Deine Steuerzentrale

Die Datei legt fest, wie dein Workflow tickt:

```yaml
src_language: de
target_langs:
  - en
  - fr
  - es
src_dir: DE
output_dir: DEV
insert_warnings: true
warnings_mapping:
  en: "Heads-up: Diese Seite wurde maschinell übersetzt, das kann zu Fehlern oder schlechter Qualität führen. Mit Vorsicht lesen!"
  fr: "Attention : Page traduite par machine, ça peut être bancal ou faux. Lis avec prudence !"
  es: "¡Ojo! Esta página es una traducción automática, puede tener errores o info rara. ¡Léela con cuidado!"
translation_models:
  de-en: "Helsinki-NLP/opus-mt-de-en"
  de-fr: "Helsinki-NLP/opus-mt-de-fr"
  de-es: "Helsinki-NLP/opus-mt-de-es"
max_chunk_length: 100 # nur zur Sicherheit die Größe könnt Ihr erhöhen je nach Model
```

- **`src_language`**: Die Sprache deiner Originaltexte (hier: Deutsch `de`).
- **`target_langs`**: Wohin soll’s gehen? Englisch `en`, Französisch `fr`, Spanisch `es`.
- **`src_dir`**: Wo liegen deine deutschen Markdowns? Im Ordner `DE`.
- **`output_dir`**: Wohin mit den Übersetzungen? In `DEV`, mit Unterordnern wie `DEV/en` oder `DEV/fr`.
- **`insert_warnings`**: Soll ’n Warnhinweis rein, dass es ’ne Maschinenübersetzung ist? (`true` = ja).
- **`warnings_mapping`**: Die Warntexte für jede Sprache, schön locker formuliert.
- **`translation_models`**: Welche Hugging Face-Modelle rocken die Übersetzung? Hier die Opus-MT-Modelle von Helsinki-NLP.
- **`max_chunk_length`**: Wie lang darf ’n Textstück sein, das ans Modell geht? (100 Tokens). Wichtig, weil die Modelle nur begrenzte Chunks schlucken können einfach mal rumspielen was geht

### 3.2. `translate.yml` – Deine Automatisierungsparty

Das ist die GitHub Actions-Pipeline, die alles am Laufen hält:

```yaml
name: Markdown mit Hugging Face übersetzen
on:
  push:
    branches: [main]
    paths:
      - 'DE/**'
      - 'config.yaml'
      - '.github/scripts/translate_with_huggingface.py'
      - '.github/workflows/translate.yml'
  schedule:
    - cron: '0 0 * * *' # Läuft jeden Tag um Mitternacht UTC
jobs:
  translate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Repo klonen
        uses: actions/checkout@v4
      - name: Python einrichten
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Python-Pakete installieren
        run: |
          pip install transformers pyyaml torch sentencepiece sacremoses spacy
      - name: spaCy-Sprachmodell laden
        run: |
          python -m spacy download de_core_news_sm
      - name: Hugging Face- und spaCy-Modelle cachen
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/huggingface
            ~/.spacy
          key: ${{ runner.os }}-models-${{ hashFiles('.github/scripts/translate_with_huggingface.py', 'config.yaml') }}
          restore-keys: |
            ${{ runner.os }}-models-
      - name: Zielordner anlegen
        run: |
          mkdir -p DEV/en
          mkdir -p DEV/fr
          mkdir -p DEV/es
          mkdir -p DE
      - name: Übersetzungsskript starten
        run: python .github/scripts/translate_with_huggingface.py
      - name: Übersetzungen checken
        run: |
          if [ -z "$(find DEV -maxdepth 2 -type f -name '*.md')" ]; then
            echo "::warning::Keine übersetzten Markdowns im DEV-Ordner gefunden."
            exit 0
          else
            echo "Übersetzungen da, alles klar!"
          fi
      - name: Änderungen committen und pushen
        run: |
          git config --global user.name "GitHub Actions Bot"
          git config --global user.email "github-actions-bot@users.noreply.github.com"
          git add DEV/
          if git diff --cached --quiet; then
            echo "Nix zu committen"
          else
            echo "Änderungen da, wird committet..."
            git commit -m "Auto-übersetzt (Hugging Face): DE→EN/FR/ES [skip ci]"
            git push
```

#### Was geht ab (`on`):
- **`push`**: Immer wenn was im `main`-Branch in `DE/`, `config.yaml`, `translate_with_huggingface.py` oder `translate.yml` geändert wird, legt der Workflow los.
- **`schedule`**: Jeden Tag um Mitternacht UTC läuft der Workflow automatisch, damit die Übersetzungen frisch bleiben, auch wenn nix geändert wurde (z. B. wenn die Zielordner leer waren).

#### Der Job (`translate`):
- **`runs-on: ubuntu-latest`**: Läuft auf einem Linux-Server in der GitHub Actions Cloud.
- **`permissions: contents: write`**: Erlaubt dem Job, die übersetzten Dateien ins Repo zu pushen.

#### Die Schritte:
1. **Repo klonen**: Holt dein Repo in die Runner-Umgebung.
2. **Python einrichten**: Stellt Python 3.10 parat.
3. **Python-Pakete installieren**: Schnappt sich `transformers`, `pyyaml`, `torch`, `sentencepiece`, `spacy`, und `sacremoses`.
4. **spaCy-Sprachmodell laden**: Lädt `de_core_news_sm` für die Satztrennung.
5. **Modelle cachen**: Speichert Hugging Face- und spaCy-Modelle, damit’s beim nächsten Mal schneller geht.
6. **Zielordner anlegen**: Macht sicher, dass `DEV/en`, `DEV/fr`, `DEV/es` da sind.
7. **Übersetzungsskript starten**: Kickt das Python-Skript an, das die Übersetzung macht.
8. **Übersetzungen checken**: Guckt, ob Markdowns in `DEV/` gelandet sind, sonst gibt’s ’ne Warnung.
9. **Änderungen committen und pushen**: Wenn’s neue Übersetzungen gibt, werden die ins Repo gepusht. Der `[skip ci]`-Tag verhindert, dass der Workflow durch den Commit wieder losgeht.

---

### 3.3. `translate_with_huggingface.py` – Der Motor

Das Skript ist der Boss, der die ganze Übersetzungsarbeit erledigt. Hier die Highlights:

```python
import os
import sys
import yaml
import glob
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import spacy

# spaCy-Setup
nltk_data_path = os.environ.get('NLTK_DATA', os.path.expanduser('~/.nltk_data'))
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

# ... (CONFIG kommt aus config.yaml) ...

SPACY_NLP_MODEL = None  # Platz fürs spaCy-Modell

def initialize_translators(config: dict):
    # ... (Lädt Hugging Face-Übersetzer) ...
    # spaCy-Modell für Deutsch laden
    try:
        global SPACY_NLP_MODEL
        spacy_model_name = f"{src_lang}_core_news_sm"
        SPACY_NLP_MODEL = spacy.load(spacy_model_name)
    except Exception as e:
        print(f"Oops, spaCy-Modell ging nicht: {e}. Fallback auf Regex.", file=sys.stderr)
        SPACY_NLP_MODEL = None

def chunk_text(text: str, max_chunk_length_config: int, tokenizer) -> list:
    # Teilt Text mit spaCy in Sätze.
    # Wenn spaCy streikt, Regex oder Zeichen-Splitting als Plan B.
    # Passt max_chunk_length an tokenizer.model_max_length an.
    # Hält Chunks in Modellgrenzen.
    # ... (Chunk-Logik) ...
    return chunks

def translate_text(text: str, src_lang: str, target_lang: str) -> str:
    # Übersetzt Text in Chunks mit Hugging Face.
    # ... (Übersetzungs- und Zusammenfügungslogik) ...
    return "\n\n".join(translated_chunks)

def process_markdown_file(file_path: str):
    # Liest Markdown, trennt Metadaten und Inhalt.
    # Übersetzt mit translate_text und speichert.
    # ... (Logik für Datei-Handling) ...

def main():
    # Config aus config.yaml laden.
    # Übersetzer und spaCy starten.
    # Alle Markdowns im Quellordner finden.
    # Jede Datei abarbeiten.
    # ... (Hauptsteuerung) ...
```

#### Was geht hier ab:
- **spaCy**: Das Skript nutzt spaCy (`spacy.load('de_core_news_sm')`) für die Satztrennung – präziser und zuverlässiger, was die Übersetzung besser macht. mit NLTK habe ich es nicht zum laufen gebracht
- **Chunking**: `chunk_text` zerlegt den Text in kleine Häppchen, damit die Modelle nicht überfordert sind. `max_chunk_length` (aus `config.yaml`) und die Modellgrenze (`tokenizer.model_max_length`) werden gecheckt. Zu lange Sätze? Werden einzeln behandelt und ggf. gekürzt.
- **Hugging Face Power**: Die `transformers.pipeline` lädt die Übersetzungsmodelle und macht die Arbeit.
- **Plan B**: Wenn spaCy oder Modelle zicken, gibt’s Regex als Fallback für die Satztrennung.

---

## 4. Wie läuft’s im Detail?

Der Workflow startet, wenn du was im `main`-Branch änderst oder Mitternacht UTC schlägt:

1. **Setup**: Repo wird geklont, Python und Bibliotheken wie Hugging Face und spaCy werden installiert.
2. **Modelle holen & cachen**: Das deutsche spaCy-Modell (`de_core_news_sm`) wird geladen. Hugging Face- und spaCy-Modelle werden gecacht, damit’s schneller geht.
3. **Übersetzen**:
   - Das Skript `translate_with_huggingface.py` legt los.
   - Liest `config.yaml` für Sprachen, Ordner und `max_chunk_length`.
   - Für jede Markdown in `DE/`:
     - Text wird eingelesen, Metadaten (YAML-Front Matter) rausgeholt.
     - Inhalt wird mit spaCy in Sätze zerlegt.
     - Sätze werden zu Chunks gepackt, die `max_chunk_length` und Modelllimits einhalten.
     - Chunks werden mit Hugging Face-Modellen (z. B. `Helsinki-NLP/opus-mt-de-en`) übersetzt.
     - Alles wird wieder zusammengeklebt.
     - Warnhinweis (falls gewollt) oben dran.
     - Übersetzte Datei landet in `DEV/` (z. B. `DEV/en/deine_datei.md`).
4. **Check & Commit**: Der Workflow guckt, ob was in `DEV/` liegt. Wenn ja, werden die Dateien ins Repo gepusht. `[skip ci]` sorgt dafür, dass der Workflow nicht in ’ne Schleife gerät.

---

## 5. Was die Logs dir sagen

In den GitHub Actions-Logs siehst du oft:

- **`Device set to use cpu`**: Hugging Face sagt dir, dass die Modelle auf der CPU laufen (keine GPU da). Alles gut, kein Ding.
- **`WARNUNG: Einzelner Satz ist länger als max_chunk_length (...)`** oder **`Your input_length: X is bigger than 0.9 * max_length: 512...`**: Heißt, ein Chunk ist fast zu lang fürs Modell (meist 512 Tokens bei Opus-MT). Das Skript hält das mit `max_chunk_length` im Griff. Wenn’s nicht crasht oder Text abschneidet, ist es nur ’ne Warnung, aber zeigt, dass du nah an der Grenze bist.

---

## 6. Fazit

Der Übersetzungs-Workflow ist eine richtig starke Nummer, um Markdowns schnell zu lokalisieren. Mit Hugging Face für die Übersetzung, spaCy für saubere Sätze und GitHub Actions für die Automatisierung hast du einen robusten Prozess am Start.

In meinem Fall ist das Ergbniss nicht so wie ich es haben möchte von daher probiere ich das nächste Tool aus .... to be continue

