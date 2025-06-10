# 🌐 Automatisierte Markdown-Übersetzung mit GitHub Actions

Dieses Repository enthält einen **GitHub Actions Workflow**, der die automatische Übersetzung von Markdown-Dateien aus dem Quellordner (`DE/`) in mehrere Zielsprachen (Englisch und Spanisch) ermöglicht. Dabei wird das Open-Source-Tool [Free Markdown Translator](https://github.com/CrazyMayfly/Free-Markdown-Translator) verwendet. Die übersetzten Dateien werden in sprachspezifischen Unterordnern im `DEV/`-Verzeichnis abgelegt.

---

## ✨ Funktionsweise

Der Workflow wird automatisch ausgelöst, sobald Änderungen an Markdown-Dateien im `DE/`-Ordner oder an der Workflow-Datei selbst auf dem `main`-Branch deines Repositorys vorgenommen werden. Hier ist eine Schritt-für-Schritt-Erklärung des Ablaufs:

1. **Repository klonen**  
   Der Workflow klont dein aktuelles Repository sowie das [Free-Markdown-Translator-Tool](https://github.com/CrazyMayfly/Free-Markdown-Translator) von GitHub.

2. **Abhängigkeiten installieren**  
   Alle für den Translator benötigten Python-Abhängigkeiten werden installiert.

3. **Temporäres Verzeichnis vorbereiten**  
   Eine temporäre Kopie deiner deutschen Markdown-Dateien aus `DE/` (inklusive aller Unterordner) wird erstellt, um die Originaldateien unberührt zu lassen.

4. **Dateinamen generieren**  
   Der Workflow liest alle Basis-Dateinamen (ohne `.md`-Erweiterung) aus dem temporären Verzeichnis und erstellt eine Liste für die Translator-Konfiguration.

5. **Konfigurationsdatei erstellen**  
   Eine `config.yaml`-Datei wird dynamisch generiert und im `src/`-Ordner des geklonten Translators abgelegt. Sie enthält Einstellungen wie Zielsprachen (Englisch, Spanisch), Übersetzungsdienst (Google) und die Liste der zu übersetzenden Dateien.

6. **Dateien übersetzen**  
   Der `Free-Markdown-Translator` wird ausgeführt und übersetzt die Markdown-Dateien. Die übersetzten Versionen (z. B. `README.en.md`, `README.es.md`) werden im temporären Verzeichnis gespeichert.

7. **Zielordner erstellen & Dateien verschieben**  
   Die Zielordner `DEV/en/` und `DEV/es/` werden erstellt, falls sie nicht existieren. Die übersetzten Dateien werden rekursiv in diese Ordner verschoben, wobei die ursprüngliche Ordnerstruktur erhalten bleibt. Das temporäre Verzeichnis wird anschließend gelöscht.

8. **Übersetzungen committen**  
   Die neuen oder aktualisierten Dateien im `DEV/`-Ordner werden automatisch deinem Repository hinzugefügt und committet.

---

## 📂 Projektstruktur

Dein Repository sollte folgende Struktur aufweisen:

```
Ihr-Repository/
├── .github/
│   └── workflows/
│       └── translate-markdown.yml  # Workflow-Datei
├── DE/                            # Deutsche Original-Markdown-Dateien
│   ├── document.md
│   └── subfolder/
│       └── another_document.md
├── DEV/                           # Zielordner für Übersetzungen
│   ├── en/                        # Englische Übersetzungen
│   │   ├── document.en.md
│   │   └── subfolder/
│   │       └── another_document.en.md
│   └── es/                        # Spanische Übersetzungen
│       ├── document.es.md
│       └── subfolder/
│           └── another_document.es.md
└── ... (Weitere Dateien und Ordner)
```

---

## 🚀 Nutzung

1. **Erstellen oder Bearbeiten**  
   Erstelle oder bearbeite eine Markdown-Datei (z. B. `your-document.md`) im Ordner `DE/` oder einem seiner Unterordner.

2. **Committen & Pushen**  
   Committe und pushe deine Änderungen auf den `main`-Branch deines GitHub-Repositorys.

3. **Workflow ausführen**  
   Der Workflow wird automatisch gestartet. Verfolge den Fortschritt in der **Actions**-Sektion deines Repositorys.

4. **Ergebnisse prüfen**  
   Nach Abschluss des Workflows findest du die übersetzten Dateien in den sprachspezifischen Unterordnern unter `DEV/` (z. B. `DEV/en/your-document.en.md`, `DEV/es/your-document.es.md`).

---

## ⚙️ Konfiguration des Translators

Die Konfiguration für den `Free-Markdown-Translator` wird dynamisch im Workflow generiert. Die `config.yaml` sieht wie folgt aus:

```yaml
# AUTOMATISCHE KONFIGURATION FÜR GITHUB ACTIONS
insert_warnings: true
src_language: de
warnings_mapping:
  zh: "警告：本文由机器翻译生成，可能导致质量不佳或信息有误，请谨慎阅读！"
  en: "This document was translated by machine and may contain errors. Please read with caution!"
  es: "Este documento fue traducido por máquina y puede contener errores. Por favor, revíselo cuidadosamente."
translator: google
target_langs:
  - en
  - es
src_filenames: # Dynamisch generierte Liste der Dateinamen
  - "README"
  - "index"
  # ... weitere .md-Dateien aus DE/
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
```

Diese `config.yaml` wird vom Workflow erstellt und im `translator-repo/src/`-Ordner abgelegt, damit das `MarkdownTranslator.py`-Skript sie verwenden kann.

---

## 🎉 Fazit

Mit diesem Workflow kannst du deine Markdown-Übersetzungen effizient automatisieren. Viel Spaß beim Übersetzen!