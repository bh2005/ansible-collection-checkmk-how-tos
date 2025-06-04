# HowTo: Verwendung des setup-distributed-monitoring.yml Playbooks für Checkmk

Dieses Dokument beschreibt, wie Sie das Ansible-Playbook `setup-distributed-monitoring.yml` aus der Checkmk Ansible Collection (`checkmk.general`) verwenden, um eine verteilte Überwachungsumgebung mit Checkmk einzurichten. Das Playbook automatisiert die Konfiguration eines zentralen Checkmk-Servers und eines oder mehrerer Remote-Server für verteilte Überwachung. Die Schritte umfassen die Vorbereitung, Konfiguration und Ausführung des Playbooks.

## Voraussetzungen
Bevor Sie das Playbook verwenden, stellen Sie sicher, dass die folgenden Voraussetzungen erfüllt sind:
- **Ansible**: Ansible (Version kompatibel mit der Collection, siehe SUPPORT.md) muss installiert sein.
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Server**: Ein zentraler Checkmk-Server und mindestens ein Remote-Server müssen installiert und erreichbar sein.
- **Zugangsdaten**: Sie benötigen die Zugangsdaten für den `automation_user` und `automation_secret` für den zentralen und alle Remote-Server.
- **Netzwerkkonnektivität**: Die Server müssen über die angegebenen URLs miteinander kommunizieren können.
- **Python-Bibliotheken**: Die `netaddr`-Bibliothek ist für einige Rollen erforderlich:
  ```bash
  pip install netaddr
  ```

## Überblick über das Playbook
Das Playbook `setup-distributed-monitoring.yml` (verfügbar unter: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/usecases/setup-distributed-monitoring.yml) führt die folgenden Aufgaben aus:
1. Konfiguriert den zentralen Checkmk-Server für verteilte Überwachung.
2. Registriert einen oder mehrere Remote-Server beim zentralen Server.
3. Aktiviert die Änderungen, um die verteilte Überwachung zu aktivieren.

Hier ist ein Beispiel des Playbooks (basierend auf der Struktur aus dem Repository):

```yaml
- name: Setup distributed monitoring
  hosts: localhost
  tasks:
    - name: Configure central site for distributed monitoring
      checkmk.general.site:
        server_url: "{{ central_server_url }}"
        site: "{{ central_site }}"
        automation_user: "{{ central_automation_user }}"
        automation_secret: "{{ central_automation_secret }}"
        state: present
        distributed_monitoring: true

    - name: Register remote site
      checkmk.general.site:
        server_url: "{{ central_server_url }}"
        site: "{{ central_site }}"
        automation_user: "{{ central_automation_user }}"
        automation_secret: "{{ central_automation_secret }}"
        remote_url: "{{ remote_server_url }}"
        remote_site: "{{ remote_site }}"
        remote_automation_user: "{{ remote_automation_user }}"
        remote_automation_secret: "{{ remote_automation_secret }}"
        state: present
```

## Schritt-für-Schritt-Anleitung

### Schritt 1: Vorbereitung des Inventars
Erstellen Sie eine Inventar-Datei (`inventory/hosts.ini`), um die Zielhosts zu definieren. Da das Playbook auf `localhost` ausgeführt wird, genügt eine einfache Konfiguration:

```ini
[localhost]
localhost ansible_connection=local
```

Speichern Sie diese Datei in einem Verzeichnis wie `inventory/hosts.ini`.

### Schritt 2: Definieren der Variablen
Erstellen Sie eine Variablen-Datei (`group_vars/all.yml`), um die erforderlichen Parameter zu definieren. Ein Beispiel:

```yaml
central_server_url: "http://central-server.example.com/"
central_site: "central"
central_automation_user: "automation"
central_automation_secret: "your-central-secret"
remote_server_url: "http://remote-server.example.com/"
remote_site: "remote"
remote_automation_user: "automation"
remote_automation_secret: "your-remote-secret"
```

Ersetzen Sie die Werte durch die tatsächlichen URLs und Zugangsdaten Ihrer Checkmk-Server. Für mehrere Remote-Server können Sie eine Liste von Variablen definieren, z. B.:

```yaml
remote_servers:
  - remote_url: "http://remote1.example.com/"
    remote_site: "remote1"
    remote_automation_user: "automation"
    remote_automation_secret: "your-remote1-secret"
  - remote_url: "http://remote2.example.com/"
    remote_site: "remote2"
    remote_automation_user: "automation"
    remote_automation_secret: "your-remote2-secret"
```

Passen Sie das Playbook an, um die Liste mit einer Schleife zu verarbeiten, falls erforderlich.

### Schritt 3: Klonen oder Kopieren des Playbooks
Klonen Sie das Repository der Checkmk Ansible Collection oder kopieren Sie das `setup-distributed-monitoring.yml`-Playbook in Ihr Projektverzeichnis:

```bash
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
```

Alternativ können Sie das Playbook direkt aus dem Repository kopieren: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/usecases/setup-distributed-monitoring.yml

Speichern Sie das Playbook z. B. als `setup-distributed-monitoring.yml` in Ihrem Projekt.

### Schritt 4: Installation der Abhängigkeiten
Installieren Sie die Checkmk Ansible Collection und die benötigten Python-Bibliotheken:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Schritt 5: Ausführen des Playbooks
Führen Sie das Playbook mit dem folgenden Befehl aus:

```bash
ansible-playbook -i inventory/hosts.ini setup-distributed-monitoring.yml
```

Stellen Sie sicher, dass die Variablen-Datei (`group_vars/all.yml`) im gleichen Verzeichnis oder in einem von Ansible erkannten Pfad liegt.

### Schritt 6: Überprüfen der Konfiguration
1. Melden Sie sich am zentralen Checkmk-Server an.
2. Navigieren Sie zu **Setup > Distributed monitoring** und prüfen Sie, ob der zentrale Server für verteilte Überwachung konfiguriert ist und die Remote-Server registriert wurden.
3. Verifizieren Sie, dass die Verbindung aktiv ist und Daten zwischen den Servern synchronisiert werden.

## Fehlerbehebung
- **Netzwerkfehler**: Stellen Sie sicher, dass die `central_server_url` und `remote_server_url` korrekt sind und die Server erreichbar sind.
- **Authentifizierungsfehler**: Überprüfen Sie die Zugangsdaten (`automation_user` und `automation_secret`) für alle Server.
- **Modulfehler**: Konsultieren Sie die Dokumentation des `checkmk.general.site`-Moduls: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/site.py
- **Logs**: Aktivieren Sie detailliertes Logging mit `-v` oder `-vvv` bei der Playbook-Ausführung, um Fehler zu identifizieren:
  ```bash
  ansible-playbook -i inventory/hosts.ini setup-distributed-monitoring.yml -vvv
  ```

## Best Practices
- **Sichere Speicherung von Secrets**: Speichern Sie sensible Daten wie `automation_secret` in verschlüsselten Variablen-Dateien (z. B. mit `ansible-vault`).
- **Idempotenz**: Das Playbook ist idempotent, d. h., wiederholte Ausführungen führen nicht zu unerwarteten Änderungen.
- **Versionierung**: Überprüfen Sie die Kompatibilität der Checkmk-Versionen und der Ansible Collection in der SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Skalierung**: Für mehrere Remote-Server verwenden Sie eine Schleife im Playbook, um die Registrierung zu vereinfachen:
  ```yaml
  - name: Register multiple remote sites
    checkmk.general.site:
      server_url: "{{ central_server_url }}"
      site: "{{ central_site }}"
      automation_user: "{{ central_automation_user }}"
      automation_secret: "{{ central_automation_secret }}"
      remote_url: "{{ item.remote_url }}"
      remote_site: "{{ item.remote_site }}"
      remote_automation_user: "{{ item.remote_automation_user }}"
      remote_automation_secret: "{{ item.remote_automation_secret }}"
      state: present
    loop: "{{ remote_servers }}"
  ```
- **Dokumentation**: Halten Sie Ihre Variablen und Konfigurationen gut dokumentiert, um spätere Änderungen zu erleichtern.

## Integration in CI/CD
Um das Playbook in eine CI/CD-Pipeline zu integrieren (z. B. mit GitHub Actions), erstellen Sie eine Workflow-Datei:

```yaml
name: Setup Checkmk Distributed Monitoring

on:
  push:
    branches:
      - main

jobs:
  setup-distributed-monitoring:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          pip install ansible netaddr
          ansible-galaxy collection install checkmk.general
      - name: Run Ansible Playbook
        env:
          ANSIBLE_CENTRAL_AUTOMATION_USER: ${{ secrets.CENTRAL_AUTOMATION_USER }}
          ANSIBLE_CENTRAL_AUTOMATION_SECRET: ${{ secrets.CENTRAL_AUTOMATION_SECRET }}
          ANSIBLE_REMOTE_AUTOMATION_USER: ${{ secrets.REMOTE_AUTOMATION_USER }}
          ANSIBLE_REMOTE_AUTOMATION_SECRET: ${{ secrets.REMOTE_AUTOMATION_SECRET }}
        run: |
          ansible-playbook -i inventory/hosts.ini setup-distributed-monitoring.yml
```

Speichern Sie Secrets in den Repository-Einstellungen Ihres CI/CD-Tools.

## Fazit
Das `setup-distributed-monitoring.yml`-Playbook automatisiert die Einrichtung einer verteilten Überwachungsumgebung in Checkmk. Mit den oben beschriebenen Schritten können Sie es lokal oder in einer CI/CD-Pipeline ausführen. Für weitere Details zu den Modulen und Optionen konsultieren Sie die offizielle Dokumentation: https://github.com/Checkmk/ansible-collection-checkmk.general.
