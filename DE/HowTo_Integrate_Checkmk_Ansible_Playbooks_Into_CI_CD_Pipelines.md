# HowTo zur Integration der Checkmk Ansible-Playbooks in CI/CD-Pipelines

Diese Anleitung beschreibt, wie Sie die Ansible-Playbooks aus der Checkmk Ansible Collection (https://github.com/Checkmk/ansible-collection-checkmk.general) in eine CI/CD-Pipeline integrieren können. Die Integration ermöglicht die Automatisierung von Checkmk-Konfigurationen, wie das Einrichten von Servern, das Verwalten von Sites oder das Hinzufügen von Hosts, in einem kontinuierlichen Integrations- und Bereitstellungsprozess. Wir verwenden GitHub Actions als Beispiel, die Schritte sind jedoch auf andere CI/CD-Systeme wie GitLab CI/CD oder Jenkins übertragbar.

## Voraussetzungen
Bevor Sie beginnen, stellen Sie sicher, dass die folgenden Voraussetzungen erfüllt sind:
- **Ansible installiert**: Ansible muss auf dem Runner oder in der CI/CD-Umgebung verfügbar sein.
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Server**: Zugang zu einem laufenden Checkmk-Server mit API-Zugriff.
- **Git-Repository**: Ein Repository mit Ihren Playbooks, das die Checkmk Ansible Collection verwendet.
- **CI/CD-Tool**: In dieser Anleitung verwenden wir GitHub Actions. Für andere Tools müssen Sie die Syntax anpassen.
- **Python und Abhängigkeiten**: Die Checkmk Ansible Collection benötigt Python und gegebenenfalls die Python-Bibliothek `netaddr` für bestimmte Rollen (z. B. `agent`).

## Schritt 1: Installation der Checkmk Ansible Collection
Die Checkmk Ansible Collection kann über Ansible Galaxy installiert werden. Dies kann in Ihrer CI/CD-Pipeline automatisiert werden.

1. **Installationsbefehl**:
   ```bash
   ansible-galaxy collection install checkmk.general
   ```
   Alternativ können Sie die Collection direkt aus dem GitHub-Repository klonen:
   ```bash
   git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
   ```

2. **Abhängigkeiten**:
   Stellen Sie sicher, dass die benötigten Python-Bibliotheken installiert sind. Für die `agent`-Rolle wird `netaddr` benötigt:
   ```bash
   pip install netaddr
   ```

## Schritt 2: Erstellen eines Ansible-Playbooks
Erstellen Sie ein Playbook, das die Module der Checkmk Ansible Collection verwendet. Hier ist ein Beispiel, das einen Ordner in Checkmk erstellt:

```yaml
- name: Create a folder in Checkmk
  hosts: localhost
  tasks:
    - name: Create a single folder
      checkmk.general.folder:
        server_url: "http://myserver/"
        site: "mysite"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        path: "/my_folder"
        name: "My Folder"
        state: "present"
```

Speichern Sie dieses Playbook als `create_folder.yml` in Ihrem Repository.

## Schritt 3: Konfigurieren der CI/CD-Pipeline
Im Folgenden wird eine Beispielkonfiguration für GitHub Actions erstellt, die das Playbook ausführt.

1. **Erstellen der Workflow-Datei**:
   Erstellen Sie eine Datei `.github/workflows/checkmk.yml` in Ihrem Repository:

```yaml
name: Checkmk Ansible Integration

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  ansible:
    runs-on: ubuntu-latest

    steps:
      # Checkout des Repositories
      - name: Checkout repository
        uses: actions/checkout@v3

      # Einrichten von Python
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      # Installieren von Ansible und Abhängigkeiten
      - name: Install Ansible and dependencies
        run: |
          pip install ansible
          pip install netaddr
          ansible-galaxy collection install checkmk.general

      # Ausführen des Ansible-Playbooks
      - name: Run Ansible Playbook
        env:
          ANSIBLE_AUTOMATION_USER: ${{ secrets.AUTOMATION_USER }}
          ANSIBLE_AUTOMATION_SECRET: ${{ secrets.AUTOMATION_SECRET }}
        run: |
          ansible-playbook create_folder.yml -i inventory/hosts.ini
```

2. **Erklärung der Schritte**:
   - **Checkout repository**: Klont das Repository, das Ihre Playbooks enthält.
   - **Set up Python**: Richtet eine Python-Umgebung ein, die für Ansible erforderlich ist.
   - **Install Ansible and dependencies**: Installiert Ansible, die `netaddr`-Bibliothek und die Checkmk Ansible Collection.
   - **Run Ansible Playbook**: Führt das Playbook aus und übergibt die Zugangsdaten als Umgebungsvariablen.

3. **Sichere Speicherung der Zugangsdaten**:
   Speichern Sie sensible Daten wie `automation_user` und `automation_secret` als Secrets in Ihrem CI/CD-Tool:
   - In GitHub Actions: Gehen Sie zu `Settings > Secrets and variables > Actions > New repository secret` und fügen Sie `AUTOMATION_USER` und `AUTOMATION_SECRET` hinzu.
   - Diese Secrets werden im Workflow als Umgebungsvariablen verwendet.

## Schritt 4: Inventar und Variablen
1. **Inventar-Datei**:
   Erstellen Sie eine Inventar-Datei (`inventory/hosts.ini`) im Repository, um die Zielhosts zu definieren. Für lokale Ausführung kann es so aussehen:
   ```ini
   [localhost]
   localhost ansible_connection=local
   ```

2. **Variablen**:
   Definieren Sie Variablen wie `server_url` und `site` entweder direkt im Playbook oder in einer separaten Variablen-Datei (`group_vars/all.yml`):
   ```yaml
   server_url: "http://myserver/"
   site: "mysite"
   ```

## Schritt 5: Testen der Pipeline
1. **Commit und Push**:
   Committen Sie die Workflow-Datei, das Playbook und die Inventar-Datei in Ihr Repository und pushen Sie diese Änderungen.
2. **Pipeline-Ausführung**:
   Die Pipeline wird automatisch bei einem Push oder Pull Request auf den `main`-Branch ausgelöst. Überprüfen Sie die Ausführung in der GitHub Actions-Oberfläche.
3. **Fehlerbehebung**:
   - Stellen Sie sicher, dass die Checkmk-Server-URL erreichbar ist.
   - Überprüfen Sie, ob die Zugangsdaten korrekt sind.
   - Konsultieren Sie die Checkmk-Dokumentation oder die `README.md` der Collection für spezifische Modulparameter: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/README.md[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/README.md)

## Schritt 6: Erweiterte Konfigurationen
- **Mehrere Playbooks**: Organisieren Sie mehrere Playbooks in einem Verzeichnis und führen Sie diese nacheinander in der Pipeline aus.
- **Tagging**: Nutzen Sie Ansible-Tags, um spezifische Aufgaben auszuführen, z. B.:
  ```yaml
  ansible-playbook create_folder.yml -i inventory/hosts.ini --tags "create_folder"
  ```
- **Distribuierte Überwachung**: Verwenden Sie Module wie `checkmk.general.site` oder `checkmk.general.sites` für verteilte Checkmk-Setups.[](https://github.com/Checkmk/ansible-collection-checkmk.general/releases)
- **Dynamisches Inventar**: Nutzen Sie das `checkmk.general.checkmk` Inventar-Plugin, um Hosts direkt aus Checkmk zu beziehen:
  ```yaml
  plugin: checkmk.general.checkmk
  server_url: "http://myserver/"
  site: "mysite"
  automation_user: "{{ automation_user }}"
  automation_secret: "{{ automation_secret }}"
  groupsources: ["hosttags", "sites"]
  ```
  Speichern Sie dies als `checkmk.yml` und verwenden Sie es mit `ansible-inventory -i checkmk.yml --graph`.[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/inventory/checkmk.py)

## Schritt 7: Best Practices
- **Idempotenz**: Stellen Sie sicher, dass Ihre Playbooks idempotent sind, um unerwartete Änderungen zu vermeiden.
- **Logging**: Aktivieren Sie das Logging nur für Debugging-Zwecke, da sensible Informationen wie Passwörter in Logs erscheinen können.[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/roles/server/README.md)
- **Versionierung**: Beachten Sie die Kompatibilität zwischen Ansible, Checkmk und der Collection. Überprüfen Sie die SUPPORT.md für getestete Versionen: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md.[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md)
- **Fehlerbehandlung**: Implementieren Sie Fehlerbehandlung im Playbook, z. B. durch `ignore_errors` oder `failed_when`, um Pipeline-Abbrüche zu vermeiden.

## Fazit
Durch die Integration der Checkmk Ansible Collection in Ihre CI/CD-Pipeline können Sie Checkmk-Konfigurationen automatisieren und konsistent halten. Diese Anleitung bietet eine Grundlage, die an spezifische Anforderungen angepasst werden kann. Für weitere Details zu Modulen und Rollen konsultieren Sie die Dokumentation der Collection: https://github.com/Checkmk/ansible-collection-checkmk.general.
