# README: Automatisierter Übersetzungs-Workflow

---

## 1. Überblick

Dieses Repository enthält einen automatisierten Workflow zur Übersetzung von Markdown-Dateien. Mithilfe von **Hugging Face** Modellen und **spaCy** in einer **GitHub Actions** Pipeline werden Inhalte aus dem Quellordner (`DE/`) automatisch ins Englische, Französische und Spanische übersetzt. Die Ergebnisse landen im `DEV/`-Ordner, was den manuellen Aufwand reduziert und Konsistenz sichert.

---

## 2. Projektstruktur

Die grundlegende Struktur sieht so aus:

```text
.
├── config.yaml
├── DE/
│   ├── HowTo_Backup_and_Restore_Hostgroups_Checkmk.md
│   ├── HowTo_Create_Groups_from_CSV_with_Checkmk_Ansible.md
│   └── ... (weitere deutsche Markdown-Dateien)
├── .github/
│   ├── scripts/
│   │   └── translate_with_huggingface.py
│   └── workflows/
│       └── translate.yml
```

