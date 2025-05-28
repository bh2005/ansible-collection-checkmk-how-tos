# Anleitung: Automatische Übersetzung von deutschen Markdown-Dateien ins Englische mit GitHub Actions

Diese Anleitung beschreibt Schritt für Schritt, wie du eine GitHub Actions CI/CD-Pipeline einrichtest, die deutsche Markdown-Dateien (*.md*) automatisch ins Englische übersetzt. Die Pipeline wird ausgelöst, wenn eine Markdown-Datei im Verzeichnis `DE/` hinzugefügt oder geändert wird, verwendet die DeepL-API für die Übersetzung und speichert die übersetzten Dateien im Verzeichnis `EN/`. Die übersetzten Dateien werden anschließend in das Repository eingecheckt.

## Voraussetzungen
Stelle vor Beginn sicher, dass folgende Anforderungen erfüllt sind:
- **GitHub-Repository**: Ein Repository, das deine deutschen Markdown-Dateien im Verzeichnis `DE/` enthält.
- **DeepL-API-Schlüssel**: Melde dich bei DeepL an (https://www.deepl.com/pro-api), um einen API-Schlüssel zu erhalten (kostenloses Kontingent verfügbar, kostenpflichtig für höhere Nutzung).
- **Python-Kenntnisse**: Grundlegendes Verständnis von Python für das Übersetzungsskript (optional, da das bereitgestellte Skript einsatzbereit ist).
- **GitHub Actions**: Grundkenntnisse der GitHub Actions-Workflows (die grundlegende Einrichtung wird unten erläutert).

## Überblick
Die Pipeline führt folgende Aufgaben aus:
1. Erkennt Änderungen an Markdown-Dateien im Verzeichnis `DE/`.
2. Verwendet ein Python-Skript, um jede deutsche Markdown-Datei zu lesen und mit der DeepL-API zu übersetzen.
3. Speichert die übersetzte Datei mit demselben Dateinamen im Verzeichnis `EN/`.
4. Checkt die übersetzten Dateien ins Repository ein und pusht sie.
5. (Optional) Erstellt einen Pull Request zur Überprüfung anstelle eines direkten Pushes.

## Schritt-für-Schritt-Anleitung

### Schritt 1: DeepL-API-Schlüssel einrichten
1. **API-Schlüssel erhalten**:
   - Registriere dich bei https://www.deepl.com/pro-api und erstelle einen API-Schlüssel.
   - Notiere den Schlüssel für die Verwendung in GitHub Secrets.
2. **API-Schlüssel in GitHub Secrets speichern**:
   - Gehe zu deinem GitHub-Repository.
   - Navigiere zu `Einstellungen > Secrets und Variablen > Actions > Neues Repository-Secret`.
   - Füge ein Secret namens `DEEPL_API_KEY` mit deinem DeepL-API-Schlüssel als Wert hinzu.

### Schritt 2: Repository-Struktur erstellen
Organisiere dein Repository wie folgt:
```plaintext
├── .github/
│   ├── scripts/
│   │   └── translate_md.py  # Python-Skript für die Übersetzung
│   └── workflows/
│       └── translate_md.yml  # GitHub Actions Workflow
├── DE/
│   └── beispiel.md  # Deutsche Markdown-Dateien
├── EN/
│   └── beispiel.md  # Übersetzte englische Markdown-Dateien (automatisch generiert)
```
- Erstelle ein Verzeichnis `DE/` für deutsche Markdown-Dateien.
- Das Verzeichnis `EN/` wird automatisch von der Pipeline erstellt, falls es nicht existiert.

### Schritt 3: Übersetzungsskript erstellen
Erstelle ein Python-Skript, das die Übersetzung der Markdown-Dateien mit der DeepL-API übernimmt. Speichere es als `.github/scripts/translate_md.py`:

```python
import os
import requests
import glob

# DeepL-API-Konfiguration
DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')
DEEPL_API_URL = 'https://api-free.deepl.com/v2/translate'

def translate_text(text, source_lang='DE', target_lang='EN'):
    """Text mit der DeepL-API übersetzen."""
    headers = {
        'Authorization': f'DeepL-Auth-Key {DEEPL_API_KEY}'
    }
    data = {
        'text': text,
        'source_lang': source_lang,
        'target_lang': target_lang,
        'preserve_formatting': 1  # Markdown-Formatierung beibehalten
    }
    response = requests.post(DEEPL_API_URL, headers=headers, data=data)
    response.raise_for_status()
    return response.json()['translations'][0]['text']

def translate_markdown_file(input_file, output_file):
    """Markdown-Datei übersetzen und Struktur beibehalten."""
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Inhalt in Chunks aufteilen, um API-Limits zu umgehen (z. B. 128 KB pro Anfrage)
    max_chunk_size = 5000  # An API-Limits anpassen
    chunks = [content[i:i + max_chunk_size] for i in range(0, len(content), max_chunk_size)]
    translated_chunks = [translate_text(chunk) for chunk in chunks]

    # Übersetzte Chunks kombinieren
    translated_content = ''.join(translated_chunks)

    # In Ausgabedatei schreiben
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_content)

def main():
    """Alle Markdown-Dateien in DE/ verarbeiten und Übersetzungen in EN/ speichern."""
    for input_file in glob.glob('DE/*.md'):
        # Ausgabedateipfad generieren (z. B. DE/Anleitung.md -> EN/Anleitung.md)
        output_file = input_file.replace('DE/', 'EN/')
        print(f"Übersetze {input_file} nach {output_file}")
        translate_markdown_file(input_file, output_file)

if __name__ == '__main__':
    main()
```

Dieses Skript:
- Liest alle *.md*-Dateien im Verzeichnis `DE/`.
- Übersetzt den Inhalt mit der DeepL-API und behält die Markdown-Formatierung bei.
- Speichert die übersetzten Dateien im Verzeichnis `EN/`.

### Schritt 4: GitHub Actions Workflow erstellen
Erstelle eine Workflow-Datei, um den Übersetzungsprozess zu automatisieren. Speichere sie als `.github/workflows/translate_md.yml`:

```yaml
name: Markdown von Deutsch nach Englisch übersetzen

on:
  push:
    branches:
      - main
    paths:
      - 'DE/**.md'  # Nur für Änderungen in DE/*.md auslösen
  pull_request:
    branches:
      - main
    paths:
      - 'DE/**.md'

jobs:
  translate:
    runs-on: ubuntu-latest
    steps:
      - name: Repository auschecken
        uses: actions/checkout@v3

      - name: Python einrichten
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Abhängigkeiten installieren
        run: |
          pip install requests

      - name: EN-Verzeichnis erstellen, falls nicht vorhanden
        run: mkdir -p EN

      - name: Markdown-Dateien übersetzen
        env:
          DEEPL_API_KEY: ${{ secrets.DEEPL_API_KEY }}
        run: |
          python .github/scripts/translate_md.py

      - name: Übersetzte Dateien einchecken
        run: |
          git config --global user.name 'GitHub Action'
          git config --global user.email 'action@example.com'
          git add EN/*.md
          git diff --staged --quiet || git commit -m "Übersetzte Markdown-Dateien hinzufügen"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Dieser Workflow:
- Ausgelöst bei Pushes oder Pull Requests, die Dateien in `DE/*.md` betreffen.
- Richtet eine Python-Umgebung ein und installiert die `requests`-Bibliothek.
- Führt das Übersetzungsskript aus.
- Checkt die übersetzten Dateien in das Repository ein und pusht sie.

### Schritt 5: (Optional) Pull Requests statt direkter Push verwenden
Um einen Pull Request für die übersetzten Dateien zu erstellen, anstelle eines direkten Pushes, ersetze den Schritt „Übersetzte Dateien einchecken“ durch:

```yaml
      - name: Pull Request erstellen
        uses: peter-evans/create-pull-request@v5
        with:
          commit-message: "Übersetzte Markdown-Dateien hinzufügen"
          branch: "translated-files"
          title: "Übersetzte Markdown-Dateien hinzufügen"
          body: "Automatisierte Übersetzung von Markdown-Dateien von DE nach EN."
          token: ${{ secrets.GITHUB_TOKEN }}
```

Dies erstellt einen neuen Branch (`translated-files`) und öffnet einen Pull Request zur Überprüfung.

### Schritt 6: Pipeline testen
1. **Deutsche Markdown-Datei hinzufügen**:
   - Erstelle eine Datei wie `DE/beispiel-test.md` mit deutschem Inhalt, z. B.:
     ```markdown
     # Beispielüberschrift
     Dies ist ein Testdokument auf Deutsch.
     ```
   - Committe und pushe die Datei in den `main`-Branch.
2. **Pipeline überwachen**:
   - Gehe zum Tab `Actions` in deinem GitHub-Repository, um die Workflow-Ausführung zu überprüfen.
   - Stelle sicher, dass eine entsprechende Datei `EN/beispiel-test.md` mit dem übersetzten Inhalt erstellt wird.
3. **Übersetzung überprüfen**:
   - Vergewissere dich, dass die übersetzte Datei in `EN/` korrekt formatiert und genau übersetzt ist.

### Fehlerbehebung
- **Probleme mit dem API-Schlüssel**: Überprüfe, ob der `DEEPL_API_KEY` korrekt in GitHub Secrets gesetzt und im Workflow zugänglich ist.
- **Fehler bei der Markdown-Formatierung**: Wenn die Formatierung (z. B. Tabellen, Code-Blöcke) beschädigt ist, passe die Chunk-Größe in `translate_md.py` an oder preprocess die Markdown-Datei, um bestimmte Elemente separat zu behandeln.
- **API-Limits**: Das kostenlose DeepL-Kontingent hat ein Limit von 500.000 Zeichen pro Monat. Überwache den Verbrauch und erwäge ein Upgrade auf einen kostenpflichtigen Plan bei höherem Bedarf.
- **Pipeline-Fehler**: Überprüfe die Workflow-Protokolle in GitHub Actions auf Fehler (z. B. Netzwerkprobleme, ungültige API-Antworten).
- **Debugging**: Füge `print`-Anweisungen in `translate_md.py` hinzu oder verwende ausführliches Logging im Workflow, um Probleme zu diagnostizieren.

### Best Practices
- **Markdown-Struktur beibehalten**:
  - Die `preserve_formatting`-Option von DeepL hilft, aber teste komplexe Markdown-Dateien (z. B. mit Tabellen oder Code-Blöcken), um die Genauigkeit sicherzustellen.
  - Erwäge die Verwendung eines Markdown-Parsers (z. B. `markdown-it` oder `mistune`), um Inhalte in übersetzbare und nicht übersetzbare Teile zu zerlegen.
- **API-Limits handhaben**:
  - Teile große Dateien in kleinere Chunks (wie im Skript gezeigt), um die Anfragegrößenbeschränkungen von DeepL (z. B. 128 KB) einzuhalten.
  - Überwache den API-Verbrauch, um das kostenlose Kontingent nicht zu überschreiten.
- **Versionskontrolle**:
  - Stelle sicher, dass die übersetzten Dateien in `EN/` mit ihren `DE/`-Gegenstücken synchron bleiben.
  - Verwende konsistente Dateinamen, um Konflikte zu vermeiden (z. B. `DE/Anleitung.md` → `EN/Anleitung.md`).
- **Qualitätssicherung**:
  - Überprüfe die ersten Übersetzungen manuell, um die Qualität zu validieren, insbesondere bei technischem oder domänenspezifischem Inhalt.
  - Erwäge einen menschlichen Überprüfungsschritt durch Pull Requests.
- **Fehlerbehandlung**:
  - Füge robuste Fehlerbehandlung in `translate_md.py` hinzu, um API-Ausfälle oder ungültige Eingaben zu managen.
  - Protokolliere Fehler im Workflow für einfacheres Debugging.

### Alternative Übersetzungstools
Falls DeepL nicht geeignet ist, kannst du folgende Alternativen nutzen:
- **Google Cloud Translate**:
  - Verwende die Python-Bibliothek `google-cloud-translate`.
  - Ersetze die `translate_text`-Funktion in `translate_md.py` durch Aufrufe der Google Translate API.
  - Erfordert ein Google Cloud-Projekt und einen API-Schlüssel.
- **Open-Source-Bibliotheken**:
  - Nutze `googletrans` für nicht-kommerzielle Projekte (weniger zuverlässig, inoffizielle API).
  - Beispiel: `pip install googletrans==4.0.0-rc1`.
- **Eigene Modelle**:
  - Verwende Open-Source-Übersetzungsmodelle (z. B. `transformers` von Hugging Face) für Offline- oder benutzerdefinierte Übersetzungen, was jedoch mehr Einrichtungsaufwand erfordert.

### Beispielausgabe
Für eine Eingabedatei `DE/beispiel-test.md`:
```markdown
# Beispielüberschrift
Dies ist ein Testdokument auf Deutsch.
```
Erstellt die Pipeline `EN/beispiel-test.md`:
```markdown
# Example Heading
This is a test document in English.
```

## Fazit
Diese GitHub Actions Pipeline automatisiert die Übersetzung von deutschen Markdown-Dateien ins Englische mit der DeepL-API. Das Setup ist flexibel und kann für andere Sprachen oder Übersetzungstools angepasst werden. Indem du dieser Anleitung folgst, kannst du den Übersetzungsprozess optimieren und gleichzeitig die Markdown-Formatierung beibehalten. Stelle sicher, dass du API-Schlüssel sicher speicherst, Übersetzungen validierst und den API-Verbrauch überwachst, um den Prozess zu optimieren. Weitere Details zur DeepL-API findest du unter https://www.deepl.com/docs-api.