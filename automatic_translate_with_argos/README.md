# Automatisierte Markdown-Übersetzung mit Argos Translate

Dieses Projekt automatisiert die Übersetzung von Markdown-Dateien von einer Quellsprache (standardmäßig Deutsch) in mehrere Zielsprachen mithilfe von Argos Translate und GitHub Actions. Der Workflow ist so konzipiert, dass er bei Änderungen im Quellverzeichnis automatisch ausgelöst wird und die übersetzten Dateien in einem separaten Verzeichnis ablegt.

✨ Features
* **Vollautomatisch**: Übersetzungen werden automatisch bei einem git push auf den main-Branch ausgelöst.
* **Multi-Language-Support**: Einfache Konfiguration zur Übersetzung in mehrere Zielsprachen (z. B. Englisch, Französisch, Spanisch).
* **Intelligente Front-Matter-Behandlung**: YAML-Front-Matter in Markdown-Dateien wird erkannt. Bestimmte Schlüssel (wie title oder description) werden übersetzt, während andere (wie date oder slug) unangetastet bleiben.
* **Robustes Modell-Management**: Die benötigten Argos-Translate-Modelle werden dynamisch heruntergeladen, auf ihre Gültigkeit überprüft und für schnellere nachfolgende Durchläufe direkt im Repository gespeichert.
* **Pivot-Übersetzung**: Falls keine direkte Übersetzung verfügbar ist (z. B. de -> fr), kann der Workflow über eine Pivot-Sprache (standardmäßig en) übersetzen (de -> en -> fr).
* **Konfigurierbar**: Alle wichtigen Parameter werden zentral in einer config.yaml-Datei verwaltet.
* **Effizient**: Das Skript lädt alle benötigten Übersetzungsmodelle nur einmal zu Beginn, um wiederholte Ladevorgänge und Warnungen zu vermeiden.

📂 Projektstruktur.
```text
├── .github/
│   ├── workflows/
│   │   └── translate.yml         # Haupt-Workflow-Datei
│   └── scripts/
│       └── translate_with_argos.py # Python-Übersetzungsskript
│
├── DE/
│   └── ...                       # Hier liegen Ihre deutschen .md-Dateien
│
├── DEV/
│   ├── en/                       # Übersetzte englische Dateien
│   ├── fr/                       # Übersetzte französische Dateien
│   └── es/                       # Übersetzte spanische Dateien
│
├── models/
│   └── *.argosmodel              # Zwischengespeicherte Übersetzungsmodelle
│
├── config.yaml                   # Zentrale Konfigurationsdatei
└── README.md                     # Diese Datei
```


## ⚙️ FunktionsweiseTrigger: 

Der GitHub Actions Workflow (.github/workflows/translate.yml) wird ausgelöst, wenn Änderungen an den Dateien im DE/-Verzeichnis oder an den Konfigurations- und Skriptdateien vorgenommen werden.Einrichtung: Der Runner richtet eine Python-Umgebung ein und installiert die notwendigen Abhängigkeiten (argostranslate, pyyaml).Modell-Management:Der Workflow lädt die aktuellsten URLs für die benötigten Sprachmodelle aus dem offiziellen ArgosPM-Index.Er lädt die .argosmodel-Dateien herunter und prüft ihre Integrität.Die Modelle werden in der Runner-Umgebung installiert, damit das Python-Skript sie verwenden kann.Neue oder aktualisierte Modelle werden in das models/-Verzeichnis committet, um zukünftige Workflow-Läufe zu beschleunigen.Skript-Ausführung: Das Python-Skript translate_with_argos.py wird ausgeführt.Es liest die config.yaml, um Quell- und Zielsprachen, Verzeichnisse und andere Einstellungen zu laden.Alle benötigten Übersetzungsmodelle werden einmalig vorab geladen.Das Skript durchsucht rekursiv das DE/-Verzeichnis nach *.md-Dateien.Für jede Datei wird der Inhalt und das Front-Matter analysiert und gemäß der Konfiguration in alle Zielsprachen übersetzt.Commit der Übersetzungen: Nach Abschluss des Skripts prüft der Workflow, ob neue oder geänderte Übersetzungen im DEV/-Verzeichnis vorliegen. Falls ja, werden diese Änderungen automatisch in das Repository committet und gepusht.

## 🔧 Konfiguration
Die gesamte Steuerung des Übersetzungsprozesses erfolgt über die config.yaml-Datei.
```yaml
# config.yaml

# Die Sprache Ihrer Quelldateien (im ISO 639-1 Format)
src_language: de

# Eine Liste der Zielsprachen (im ISO 639-1 Format)
target_langs:
  - en
  - fr
  - es

# Das Verzeichnis, das die zu übersetzenden Markdown-Dateien enthält
src_dir: DE

# Das Basisverzeichnis, in dem die übersetzten Dateien abgelegt werden
output_dir: DEV

# Ob ein Warnhinweis zur maschinellen Übersetzung eingefügt werden soll
insert_warnings: true

# Der Text des Warnhinweises für jede Zielsprache
warnings_mapping:
  en: "Yo, this is a machine translation! It might not be perfect, so read with care."
  fr: "Hé, c'est une traduction automatique ! Elle n'est peut-être pas parfaite, alors lisez attentivement."
  es: "¡Ojo, esta es una traducción automática! Puede que no sea perfecta, así que léela con cuidado."

# Front-Matter-Schlüssel, deren Werte NICHT übersetzt werden sollen
front_matter_transparent_keys:
  - date
  - slug

# Front-Matter-Schlüssel, deren (String-)Werte übersetzt werden sollen
# HINWEIS: Alle nicht als "transparent" markierten String-Werte werden standardmäßig übersetzt.
# Diese Liste dient vor allem der Übersichtlichkeit.
front_matter_key_value_keys:
  - title
  - description

# Die maximale Zeichenlänge für Text-Chunks vor der Übersetzung.
# Hilft bei der Verarbeitung sehr großer Dateien.
max_chunk_length: 2000
```

## 🚀 Nutzung
Schreiben oder bearbeiten Sie eine Markdown-Datei im Verzeichnis DE/.Committen und pushen Sie Ihre Änderungen auf den main-Branch.Warten Sie, bis der GitHub-Action-Lauf abgeschlossen ist.Die übersetzten Versionen Ihrer Datei finden Sie anschließend in den entsprechenden Unterordnern in DEV/ (z. B. DEV/en/, DEV/fr/, etc.).