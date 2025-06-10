# Automatisierte Markdown-Übersetzung mit GitHub Actions

Dieses Repository enthält einen GitHub Actions Workflow, der die Übersetzung von Markdown-Dateien aus einem Quellordner (`DE/`) in mehrere Zielsprachen (Englisch und Spanisch) automatisiert. Dabei wird das Open-Source-Tool [Free Markdown Translator](https://github.com/CrazyMayfly/Free-Markdown-Translator) verwendet. Die übersetzten Dateien werden in sprachspezifischen Unterordnern im `DEV/`-Verzeichnis abgelegt.

## ✨ Funktionsweise

Der Workflow wird automatisch ausgelöst, wenn Sie Änderungen an Markdown-Dateien im `DE/`-Ordner oder an der Workflow-Datei selbst auf dem `main`-Branch Ihres Repositorys vornehmen.

Hier ist eine Schritt-für-Schritt-Erklärung, was der Workflow tut:

1. **Repository klonen:** Der Workflow klont Ihr aktuelles Repository und auch das `Free-Markdown-Translator`-Tool von GitHub.

2. **Abhängigkeiten installieren:** Die für den Translator erforderlichen Python-Abhängigkeiten werden installiert.

3. **Temporäres Verzeichnis vorbereiten:** Eine temporäre Kopie Ihrer deutschen Markdown-Dateien aus `DE/` (einschließlich aller Unterordner) wird in einem speziellen Ordner erstellt. Dies stellt sicher, dass Ihre Originaldateien in `DE/` unberührt bleiben.

4. **Dateinamen generieren:** Der Workflow liest alle Basis-Dateinamen (ohne `.md`-Erweiterung) aus dem temporären Verzeichnis und bereitet sie als Liste für die Konfiguration des Translators vor.

5. **Konfigurationsdatei erstellen:** Eine `config.yaml`-Datei wird dynamisch erstellt und im `src/`-Ordner des geklonten `Free-Markdown-Translator`-Tools platziert. Diese Datei enthält alle notwendigen Einstellungen für die Übersetzung, wie z.B. die Zielsprachen (Englisch und Spanisch), den verwendeten Übersetzungsdienst (Google) und die Liste der zu übersetzenden Dateinamen.

6. **Dateien übersetzen:** Der `Free-Markdown-Translator` wird auf dem temporären Verzeichnis ausgeführt. Er übersetzt die Markdown-Dateien und legt die übersetzten Versionen (z.B. `README.en.md`, `README.es.md`) direkt neben den Originaldateien im temporären Verzeichnis ab.

7. **Zielordner erstellen & Dateien verschieben:** Der Workflow stellt sicher, dass die Zielordner `DEV/en/` und `DEV/es/` in Ihrem Repository existieren. Anschließend werden die übersetzten Dateien rekursiv aus dem temporären Verzeichnis in die entsprechenden `DEV/en/` und `DEV/es/` Ordner verschoben, wobei die ursprüngliche Ordnerstruktur beibehalten wird. Das temporäre Verzeichnis wird danach gelöscht.

8. **Übersetzungen committen:** Die neu übersetzten oder aktualisierten Dateien im `DEV/`-Ordner werden automatisch zu Ihrem Repository hinzugefügt und committet.

## 📂 Projektstruktur

Ihr Repository sollte folgendermaßen aufgebaut sein:

```text
Ihr-Repository/
├── .github/
│   └── workflows/
│       └── translate-markdown.yml  # <-- Diese Workflow-Datei
├── DE/                            # <-- Hier liegen Ihre deutschen .md-Dateien (Originale)
│   └── document.md
│   └── subfolder/
│       └── another_document.md
├── DEV/                           # <-- Zielordner für Übersetzungen
│   ├── en/                        # Übersetzte englische Dateien
│   │   └── document.en.md
│   │   └── subfolder/
│   │       └── another_document.en.md
│   └── es/                        # Übersetzte spanische Dateien
│       └── document.es.md
│       └── subfolder/
│           └── another_document.es.md
└── ... (Ihre anderen Dateien und Ordner)
```


## 🚀 Nutzung

1. **Erstellen/Bearbeiten:** Erstellen oder bearbeiten Sie eine Markdown-Datei (z.B. `your-document.md`) im Ordner `DE/` oder in einem seiner Unterordner.

2. **Committen & Pushen:** Committen und pushen Sie Ihre Änderungen auf den `main`-Branch Ihres GitHub-Repositorys.

3. **Workflow ausführen:** Der GitHub Actions Workflow wird automatisch ausgelöst. Sie können den Fortschritt in der "Actions"-Sektion Ihres GitHub-Repositorys verfolgen.

4. **Ergebnisse prüfen:** Sobald der Workflow abgeschlossen ist, finden Sie die übersetzten Versionen Ihrer Dateien in den entsprechenden sprachspezifischen Unterordnern unter `DEV/` (z.B. `DEV/en/your-document.en.md`, `DEV/es/your-document.es.md`).

## ⚙️ Konfiguration des Translators (im Workflow)

Die Konfiguration für den `Free-Markdown-Translator` wird direkt innerhalb des Workflows dynamisch generiert und sieht im Wesentlichen so aus:

AUTOMATISCHE KONFIGURATION FÜR GITHUB ACTIONS
insert_warnings: true
src_language: de
warnings_mapping:
zh: "警告：本文由机器翻译生成,可能导致质量不佳或信息有误,请谨慎阅读！"
en: "This document was translated by machine and may contain errors. Please read with caution!"
es: "Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente."
translator: google
target_langs:

en
es src_filenames: # Diese Liste wird dynamisch mit Ihren Dateinamen gefüllt
"README"
"index"
... und so weiter für alle .md-Dateien in Ihrem DE/ Ordner
compact_langs: []
threads: 4
proxy:
enable: false
host: ""
port: 0
user: ""
password: ""
front_matter_transparent_keys: []
front_matter_key_value_keys: []
front_matter_key_value_array_keys: []


Diese `config.yaml` wird vom Workflow erstellt und im `translator-repo/src/`-Ordner abgelegt, damit das `MarkdownTranslator.py`-Skript sie verwenden kann.

Viel Spaß beim Automatisieren Ihrer Übersetzung!