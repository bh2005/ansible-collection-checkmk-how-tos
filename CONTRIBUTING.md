# Mitwirkungsrichtlinien / Contributing Guidelines

## Deutsch

### Willkommen

Vielen Dank für dein Interesse, am Projekt [ansible-collection-checkmk-how-tos](https://github.com/bh2005/ansible-collection-checkmk-how-tos) mitzuwirken! Dieses Repository bietet Anleitungen zur Nutzung der Checkmk Ansible Collection, um die Automatisierung von Checkmk-Konfigurationen zu erleichtern. Wir freuen uns über alle Arten von Beiträgen, sei es durch neue Anleitungen, Verbesserungen bestehender Dokumentation, Fehlerberichte oder Vorschläge.

Diese Richtlinie beschreibt, wie du beitragen kannst, und stellt sicher, dass der Prozess für alle Beteiligten klar und einheitlich ist. Bitte lies auch unseren [Verhaltenskodex](CODE_OF_CONDUCT.md), um eine respektvolle und inklusive Zusammenarbeit zu gewährleisten.

### Arten von Beiträgen

Du kannst auf verschiedene Weisen beitragen:

- **Dokumentation**:
  - Neue How-To-Anleitungen in Deutsch oder Englisch erstellen.
  - Bestehende Anleitungen korrigieren, aktualisieren oder übersetzen.
  - Markdown-Formatierungsfehler oder Tippfehler beheben.
- **Fehlerberichte**:
  - Unklare, falsche oder veraltete Inhalte in Issues melden.
- **Vorschläge**:
  - Neue Themen oder Verbesserungen für Anleitungen vorschlagen.
- **Technische Beiträge**:
  - Beispieldateien (z. B. Playbooks, Skripte) hinzufügen oder verbessern.
  - CI/CD-Workflows oder andere Automatisierungen vorschlagen.

### Wie du beitragen kannst

#### 1. Repository forken
- Forke das Repository auf GitHub, um eine eigene Kopie zu erstellen.
- Klone dein geforktes Repository lokal:
  ```bash
  git clone https://github.com/<dein-benutzername>/ansible-collection-checkmk-how-tos.git
  ```

#### 2. Änderungen vornehmen
- Erstelle einen neuen Branch für deine Änderungen:
  ```bash
  git checkout -b mein-beitrag
  ```
- Bearbeite oder erstelle Markdown-Dateien im entsprechenden Verzeichnis (`DE/` für Deutsch, `EN/` für Englisch).
- Halte dich an die bestehende Struktur der Anleitungen:
  - Verwende klare Überschriften (`#`, `##`, etc.).
  - Nutze Code-Blöcke (```yaml, ```bash) für Beispiele.
  - Stelle sicher, dass die Sprache präzise und für Anfänger verständlich ist.
- Für technische Beiträge (z. B. Playbooks):
  - Teste deine Änderungen lokal, um sicherzustellen, dass sie funktionieren.
  - Dokumentiere die Voraussetzungen und Schritte klar.

#### 3. Änderungen einreichen
- Committe deine Änderungen mit einer klaren Nachricht:
  ```bash
  git add .
  git commit -m "Neue Anleitung für XYZ hinzugefügt"
  ```
- Pushe deinen Branch zu deinem geforkten Repository:
  ```bash
  git push origin mein-beitrag
  ```
- Erstelle einen Pull Request (PR) im ursprünglichen Repository:
  - Gehe zu deinem geforkten Repository auf GitHub.
  - Klicke auf „Contribute“ und „Open Pull Request“.
  - Beschreibe deine Änderungen im PR, z. B. was du hinzugefügt oder geändert hast und warum.

#### 4. Überprüfung und Feedback
- Die Maintainer überprüfen deinen Pull Request und geben gegebenenfalls Feedback.
- Sei bereit, Anpassungen vorzunehmen, falls Änderungen angefordert werden.
- Nach Genehmigung wird dein Beitrag in das Haupt-Repository übernommen.

### Richtlinien für Beiträge

- **Sprache**:
  - Deutsche Anleitungen gehören in `DE/`, englische in `EN/`.
  - Achte auf klare, präzise und professionelle Sprache.
  - Vermeide Jargon, es sei denn, er ist für die Zielgruppe (Checkmk- und Ansible-Nutzer) relevant.
- **Formatierung**:
  - Halte dich an die Markdown-Syntax und die Struktur bestehender Dateien.
  - Verwende Absätze, Listen und Code-Blöcke, um die Lesbarkeit zu erhöhen.
- **Qualität**:
  - Stelle sicher, dass neue Anleitungen korrekt, vollständig und getestet sind.
  - Füge bei technischen Beiträgen Beispiele oder Screenshots hinzu, wenn möglich.
- **Lizenz**:
  - Alle Beiträge fallen unter die Lizenz des Projekts (siehe [LICENSE](LICENSE) im Repository, falls vorhanden).
  - Stelle sicher, dass du die Rechte an deinem Beitrag hast.

### Fragen oder Unterstützung

Falls du Fragen hast oder Unterstützung benötigst, öffne ein Issue im Repository oder kontaktiere die Maintainer per E-Mail unter [bernd.holzhauer@k-plus-s.com](mailto:bernd.holzhauer@k-plus-s.com). Wir helfen dir gerne weiter!

### Danksagung

Vielen Dank für deine Unterstützung dieses Projekts! Deine Beiträge helfen, die Checkmk Ansible Collection für alle Nutzer zugänglicher und nützlicher zu machen.

---

## English

### Welcome

Thank you for your interest in contributing to the [ansible-collection-checkmk-how-tos](https://github.com/bh2005/ansible-collection-checkmk-how-tos) project! This repository provides guides for using the Checkmk Ansible Collection to simplify Checkmk configuration automation. We welcome all types of contributions, whether through new guides, improvements to existing documentation, bug reports, or suggestions.

This guideline outlines how you can contribute and ensures a clear and consistent process for everyone involved. Please also read our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure respectful and inclusive collaboration.

### Types of Contributions

You can contribute in various ways:

- **Documentation**:
  - Create new how-to guides in German or English.
  - Fix, update, or translate existing guides.
  - Correct Markdown formatting errors or typos.
- **Bug Reports**:
  - Report unclear, incorrect, or outdated content via issues.
- **Suggestions**:
  - Propose new topics or improvements for guides.
- **Technical Contributions**:
  - Add or improve example files (e.g., playbooks, scripts).
  - Suggest CI/CD workflows or other automation enhancements.

### How to Contribute

#### 1. Fork the Repository
- Fork the repository on GitHub to create your own copy.
- Clone your forked repository locally:
  ```bash
  git clone https://github.com/<your-username>/ansible-collection-checkmk-how-tos.git
  ```

#### 2. Make Changes
- Create a new branch for your changes:
  ```bash
  git checkout -b my-contribution
  ```
- Edit or create Markdown files in the appropriate directory (`DE/` for German, `EN/` for English).
- Follow the structure of existing guides:
  - Use clear headings (`#`, `##`, etc.).
  - Use code blocks (```yaml, ```bash) for examples.
  - Ensure the language is precise and understandable for beginners.
- For technical contributions (e.g., playbooks):
  - Test your changes locally to ensure they work.
  - Document prerequisites and steps clearly.

#### 3. Submit Changes
- Commit your changes with a clear message:
  ```bash
  git add .
  git commit -m "Added new guide for XYZ"
  ```
- Push your branch to your forked repository:
  ```bash
  git push origin my-contribution
  ```
- Create a Pull Request (PR) in the original repository:
  - Go to your forked repository on GitHub.
  - Click “Contribute” and “Open Pull Request.”
  - Describe your changes in the PR, e.g., what you added or modified and why.

#### 4. Review and Feedback
- The maintainers will review your Pull Request and provide feedback if needed.
- Be prepared to make adjustments if changes are requested.
- Once approved, your contribution will be merged into the main repository.

### Contribution Guidelines

- **Language**:
  - German guides belong in `DE/`, English guides in `EN/`.
  - Use clear, precise, and professional language.
  - Avoid jargon unless relevant to the audience (Checkmk and Ansible users).
- **Formatting**:
  - Adhere to Markdown syntax and the structure of existing files.
  - Use paragraphs, lists, and code blocks to enhance readability.
- **Quality**:
  - Ensure new guides are accurate, complete, and tested.
  - Include examples or screenshots for technical contributions when possible.
- **License**:
  - All contributions fall under the project’s license (see [LICENSE](LICENSE) in the repository, if available).
  - Ensure you have the rights to your contribution.

### Questions or Support

If you have questions or need assistance, open an issue in the repository or contact the maintainers via email at [bernd.holzhauer@k-plus-s.com](mailto:bernd.holzhauer@k-plus-s.com). We’re happy to help!

### Acknowledgment

Thank you for supporting this project! Your contributions help make the Checkmk Ansible Collection more accessible and useful for all users.
