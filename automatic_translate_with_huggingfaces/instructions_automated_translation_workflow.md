# How it Works: Automated Translation Workflow with Hugging Face and spaCy in GitHub Actions

---

## 1. What does your Workflow do?

Your workflow automatically translates technical documentation or other Markdown texts from the source folder (`DE/`) into English, French, and Spanish. The results end up in the `DEV/` folder. This saves a lot of manual work and ensures that your content is consistently localized everywhere.

---

## 2. Structure

What goes where?!?
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

---

## 3. The Main Players

Your workflow has three central files that work great together:

### 3.1. `config.yaml` – Your Control Center

This file defines how your workflow operates:

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
  en: "Heads-up: This page was machine-translated, which may lead to errors or poor quality. Read with caution!"
  fr: "Attention : Page traduite par machine, ça peut être bancal ou faux. Lis avec prudence !"
  es: "¡Ojo! Esta página es una traducción automática, puede tener errores o info rara. ¡Léela con cuidado!"
translation_models:
  de-en: "Helsinki-NLP/opus-mt-de-en"
  de-fr: "Helsinki-NLP/opus-mt-de-fr"
  de-es: "Helsinki-NLP/opus-mt-de-es"
max_chunk_length: 100 # Just for safety, you can increase the size depending on the model
```

* **`src_language`**: The language of your original texts (here: German `de`).
* **`target_langs`**: Where should it go? English `en`, French `fr`, Spanish `es`.
* **`src_dir`**: Where are your German Markdowns? In the `DE` folder.
* **`output_dir`**: Where do the translations go? Into `DEV`, with subfolders like `DEV/en` or `DEV/fr`.
* **`insert_warnings`**: Should a warning note be included that it's a machine translation? (`true` = yes).
* **`warnings_mapping`**: The warning texts for each language, formulated in a casual way.
* **`translation_models`**: Which Hugging Face models are rocking the translation? Here, the Opus-MT models from Helsinki-NLP.
* **`max_chunk_length`**: How long can a text piece be that goes to the model? (100 tokens). Important because models can only handle limited chunks – feel free to experiment to see what works.

### 3.2. `translate.yml` – Your Automation Party

This is the GitHub Actions pipeline that keeps everything running:

```yaml
name: Translate Markdown with Hugging Face
on:
  push:
    branches: [main]
    paths:
      - 'DE/**'
      - 'config.yaml'
      - '.github/scripts/translate_with_huggingface.py'
      - '.github/workflows/translate.yml'
  schedule:
    - cron: '0 0 * * *' # Runs daily at midnight UTC
jobs:
  translate:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Clone Repo
        uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      - name: Install Python packages
        run: |
          pip install transformers pyyaml torch sentencepiece sacremoses spacy
      - name: Download spaCy language model
        run: |
          python -m spacy download de_core_news_sm
      - name: Cache Hugging Face and spaCy models
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache/huggingface
            ~/.spacy
          key: ${{ runner.os }}-models-${{ hashFiles('.github/scripts/translate_with_huggingface.py', 'config.yaml') }}
          restore-keys: |
            ${{ runner.os }}-models-
      - name: Create target folders
        run: |
          mkdir -p DEV/en
          mkdir -p DEV/fr
          mkdir -p DEV/es
          mkdir -p DE
      - name: Start translation script
        run: python .github/scripts/translate_with_huggingface.py
      - name: Check translations
        run: |
          if [ -z "$(find DEV -maxdepth 2 -type f -name '*.md')" ]; then
            echo "::warning::No translated Markdowns found in DEV folder."
            exit 0
          else
            echo "Translations are there, all good!"
          fi
      - name: Commit and push changes
        run: |
          git config --global user.name "GitHub Actions Bot"
          git config --global user.email "github-actions-bot@users.noreply.github.com"
          git add DEV/
          if git diff --cached --quiet; then
            echo "Nothing to commit"
          else
            echo "Changes detected, committing..."
            git commit -m "Auto-translated (Hugging Face): DE→EN/FR/ES [skip ci]"
            git push
```

#### What's happening (`on`):
* **`push`**: Whenever something changes in the `main` branch within `DE/`, `config.yaml`, `translate_with_huggingface.py`, or `translate.yml`, the workflow kicks off.
* **`schedule`**: The workflow runs automatically every day at midnight UTC, ensuring translations stay fresh, even if nothing has changed (e.g., if the target folders were empty).

#### The Job (`translate`):
* **`runs-on: ubuntu-latest`**: Runs on a Linux server in the GitHub Actions cloud.
* **`permissions: contents: write`**: Allows the job to push the translated files to the repo.

#### The Steps:
1.  **Clone Repo**: Gets your repo into the runner's environment.
2.  **Set up Python**: Prepares Python 3.10.
3.  **Install Python packages**: Grabs `transformers`, `pyyaml`, `torch`, `sentencepiece`, `spacy`, and `sacremoses`.
4.  **Load spaCy language model**: Downloads `de_core_news_sm` for sentence splitting.
5.  **Cache models**: Caches Hugging Face and spaCy models to speed up future runs.
6.  **Create target folders**: Ensures `DEV/en`, `DEV/fr`, `DEV/es` exist.
7.  **Start translation script**: Kicks off the Python script that does the translation.
8.  **Check translations**: Sees if Markdowns ended up in `DEV/`, otherwise issues a warning.
9.  **Commit and push changes**: If there are new translations, they're pushed to the repo. The `[skip ci]` tag prevents the workflow from looping.

---

### 3.3. `translate_with_huggingface.py` – The Engine

This script is the boss that handles all the translation work. Here are the highlights:

```python
import os
import sys
import yaml
import glob
import re
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import spacy

# spaCy Setup
nltk_data_path = os.environ.get('NLTK_DATA', os.path.expanduser('~/.nltk_data'))
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

# ... (CONFIG comes from config.yaml) ...

SPACY_NLP_MODEL = None  # Placeholder for the spaCy model

def initialize_translators(config: dict):
    # ... (Loads Hugging Face translators) ...
    # Load spaCy model for German
    try:
        global SPACY_NLP_MODEL
        spacy_model_name = f"{src_lang}_core_news_sm"
        SPACY_NLP_MODEL = spacy.load(spacy_model_name)
    except Exception as e:
        print(f"Oops, spaCy model failed: {e}. Fallback to Regex.", file=sys.stderr)
        SPACY_NLP_MODEL = None

def chunk_text(text: str, max_chunk_length_config: int, tokenizer) -> list:
    # Splits text into sentences with spaCy.
    # If spaCy fails, Regex or character splitting as Plan B.
    # Adjusts max_chunk_length to tokenizer.model_max_length.
    # Keeps chunks within model limits.
    # ... (Chunking logic) ...
    return chunks

def translate_text(text: str, src_lang: str, target_lang: str) -> str:
    # Translates text in chunks with Hugging Face.
    # ... (Translation and reassembly logic) ...
    return "\n\n".join(translated_chunks)

def process_markdown_file(file_path: str):
    # Reads Markdown, separates metadata and content.
    # Translates with translate_text and saves.
    # ... (Logic for file handling) ...

def main():
    # Load config from config.yaml.
    # Start translators and spaCy.
    # Find all Markdowns in the source folder.
    # Process each file.
    # ... (Main control flow) ...
```

#### What's going on here:
* **spaCy**: The script uses spaCy (`spacy.load('de_core_news_sm')`) for sentence splitting – more precise and reliable, which improves translation. I couldn't get it to work with NLTK.
* **Chunking**: `chunk_text` breaks down the text into small pieces so the models aren't overwhelmed. `max_chunk_length` (from `config.yaml`) and the model limit (`tokenizer.model_max_length`) are checked. Sentences too long? They are handled individually and possibly shortened.
* **Hugging Face Power**: The `transformers.pipeline` loads the translation models and does the work.
* **Plan B**: If spaCy or models act up, there's a regex fallback for sentence splitting.

---

## 4. How it Runs in Detail

The workflow starts when you change something in the `main` branch or when midnight UTC strikes:

1.  **Setup**: Repo is cloned, Python and libraries like Hugging Face and spaCy are installed.
2.  **Get & Cache Models**: The German spaCy model (`de_core_news_sm`) is loaded. Hugging Face and spaCy models are cached to speed things up.
3.  **Translate**:
    * The `translate_with_huggingface.py` script kicks off.
    * Reads `config.yaml` for languages, folders, and `max_chunk_length`.
    * For each Markdown in `DE/`:
        * Text is read, metadata (YAML front matter) is extracted.
        * Content is segmented into sentences with spaCy.
        * Sentences are packed into chunks that adhere to `max_chunk_length` and model limits.
        * Chunks are translated with Hugging Face models (e.g., `Helsinki-NLP/opus-mt-de-en`).
        * Everything is glued back together.
        * Warning note (if desired) is added at the top.
        * Translated file lands in `DEV/` (e.g., `DEV/en/your_file.md`).
4.  **Check & Commit**: The workflow checks if anything ended up in `DEV/`. If yes, the files are pushed to the repo. `[skip ci]` ensures the workflow doesn't get into a loop.

---

## 5. What the Logs Tell You

In the GitHub Actions logs, you'll often see:

* **`Device set to use cpu`**: Hugging Face tells you that the models are running on the CPU (no GPU available). All good, no problem.
* **`WARNUNG: Einzelner Satz ist länger als max_chunk_length (...)`** or **`Your input_length: X is bigger than 0.9 * max_length: 512...`**: Means a chunk is almost too long for the model (usually 512 tokens for Opus-MT). The script keeps this in check with `max_chunk_length`. If it doesn't crash or truncate text, it's just a warning, but it indicates you're close to the limit.

---

## 6. Conclusion

The translation workflow is a really powerful tool for quickly localizing Markdowns. With Hugging Face for translation, spaCy for clean sentences, and GitHub Actions for automation, you've got a robust process going.

In my case, the result isn't what I want, so I'm trying the next tool... to be continued.
