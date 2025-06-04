# Wie man Checkmk-Hostgruppen in ein Git-Repository sichert und in eine neue Instanz kopiert

Dieses HowTo beschreibt, wie man Hostgruppen aus einer Checkmk-Instanz (Instanz1) mit der `checkmk.general` Ansible Collection in ein Git-Repository sichert und anschließend in eine neue Checkmk-Instanz (Instanz2) kopiert. Es verwendet das Lookup-Plugin `checkmk.general.hostgroups`, um Hostgruppen-Daten abzurufen, speichert diese in einer YAML-Datei und verwendet das Modul `checkmk.general.checkmk_hostgroup`, um die Hostgruppen in der neuen Instanz zu erstellen. Die Daten werden mit dem Modul `ansible.builtin.git` in ein Git-Repository gesichert.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit der Collection).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Instanzen**: Zugang zu beiden Checkmk-Instanzen (Instanz1 für Backup, Instanz2 für Wiederherstellung) mit API-Zugriff.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Automatisierungs-API beider Instanzen.
- **Git**: Installiert auf dem Ansible-Controller und ein konfiguriertes Git-Repository (lokal oder remote, z. B. auf GitHub, GitLab).
- **Vault (empfohlen)**: Für die sichere Speicherung der Zugangsdaten (`automation_secret`).
- **Abhängigkeiten**: Python-Modul `netaddr` auf dem Controller (für einige Checkmk-Module erforderlich, siehe [ansible-collection-checkmk.general/roles/agent/README.md](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/roles/agent/README.md)).
- **SSH-Schlüssel**: Für den Zugriff auf ein Remote-Git-Repository (optional, siehe [Ansible-Dokumentation zu known_hosts](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/known_hosts_module.html)).

## Schritte

### 1. Git-Repository vorbereiten
Richte ein Git-Repository ein, in dem die Hostgruppen-Konfiguration gespeichert wird.

#### Lokal
Erstelle ein lokales Repository:
```bash
mkdir checkmk-hostgroups-backup
cd checkmk-hostgroups-backup
git init
```

#### Remote (optional)
Falls du ein Remote-Repository (z. B. auf GitHub) verwendest, klone es oder füge es hinzu:
```bash
git clone git@github.com:dein-benutzer/checkmk-hostgroups-backup.git
```
Stelle sicher, dass der SSH-Schlüssel des Ansible-Controllers im Repository registriert ist. Alternativ kannst du HTTPS mit Benutzername/Passwort oder einem Personal Access Token verwenden.

### 2. Hostgruppen aus Instanz1 sichern
Erstelle ein Playbook, um alle Hostgruppen aus Instanz1 abzurufen und in einer YAML-Datei zu speichern, die dann in das Git-Repository übernommen wird.

#### Playbook: `backup_hostgroups.yml`
```yaml
- name: Backup Checkmk-Hostgruppen in Git
  hosts: localhost
  tasks:
    # Hostgruppen abrufen
    - name: Abrufen aller Hostgruppen aus Instanz1
      ansible.builtin.set_fact:
        hostgroups: "{{ lookup('checkmk.general.hostgroups', server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret) }}"
      vars:
        instance1_url: "https://monitoring1.example.com"
        instance1_site: "mysite1"
        instance1_user: "automation"
        instance1_secret: "{{ vault_instance1_secret }}"

    # Hostgruppen in Datei speichern
    - name: Speichere Hostgruppen in Datei
      ansible.builtin.copy:
        content: "{{ hostgroups | to_nice_yaml }}"
        dest: "{{ backup_dir }}/hostgroups.yml"
      vars:
        backup_dir: "./checkmk-hostgroups-backup"

    # Git-Operationen
    - name: Git-Status prüfen
      ansible.builtin.git:
        repo: "{{ git_repo }}"
        dest: "{{ backup_dir }}"
        accept_hostkey: true
        version: main
      register: git_status
      vars:
        git_repo: "git@github.com:dein-benutzer/checkmk-hostgroups-backup.git"
        backup_dir: "./checkmk-hostgroups-backup"

    - name: Änderungen committen
      ansible.builtin.command:
        cmd: git commit -m "Backup der Checkmk-Hostgruppen vom {{ ansible_date_time.iso8601 }}"
        chdir: "{{ backup_dir }}"
      when: git_status.changed
      vars:
        backup_dir: "./checkmk-hostgroups-backup"

    - name: Änderungen pushen
      ansible.builtin.command:
        cmd: git push origin main
        chdir: "{{ backup_dir }}"
      when: git_status.changed
      vars:
        backup_dir: "./checkmk-hostgroups-backup"
```

#### Erklärung
- **Lookup-Plugin**: `checkmk.general.hostgroups` ruft alle Hostgruppen aus Instanz1 ab, inklusive ihrer Attribute (z. B. `name`, `title`).
- **Speichern**: Die Hostgruppen werden in einer YAML-Datei (`hostgroups.yml`) im Verzeichnis `checkmk-hostgroups-backup` gespeichert.
- **Git-Operationen**: Das Modul `ansible.builtin.git` synchronisiert das Repository, und die `ansible.builtin.command`-Tasks führen `git commit` und `git push` aus, wenn Änderungen vorliegen.
- **Vault**: Das `automation_secret` für Instanz1 wird sicher in einer Vault-Variablen (`vault_instance1_secret`) gespeichert.
- **Beispielausgabe**: Die Datei `hostgroups.yml` könnte so aussehen:
  ```yaml
  - name: web_servers
    title: Web Servers
  - name: db_servers
    title: Database Servers
  ```

#### Ausführen
```bash
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
```

#### Ergebnis
Die Hostgruppen werden in `hostgroups.yml` gespeichert und in das Git-Repository gecommittet und gepusht.

### 3. Hostgruppen in Instanz2 wiederherstellen
Erstelle ein Playbook, um die gesicherten Hostgruppen aus der YAML-Datei in Instanz2 zu importieren.

#### Playbook: `restore_hostgroups.yml`
```yaml
- name: Hostgruppen aus Git in Instanz2 wiederherstellen
  hosts: localhost
  tasks:
    # Repository klonen oder aktualisieren
    - name: Git-Repository klonen oder aktualisieren
      ansible.builtin.git:
        repo: "{{ git_repo }}"
        dest: "{{ backup_dir }}"
        accept_hostkey: true
        version: main
      vars:
        git_repo: "git@github.com:dein-benutzer/checkmk-hostgroups-backup.git"
        backup_dir: "./checkmk-hostgroups-backup"

    # Hostgruppen aus Datei laden
    - name: Lade Hostgruppen aus YAML-Datei
      ansible.builtin.set_fact:
        hostgroups: "{{ lookup('file', backup_dir + '/hostgroups.yml') | from_yaml }}"
      vars:
        backup_dir: "./checkmk-hostgroups-backup"

    # Hostgruppen in Instanz2 erstellen
    - name: Erstelle Hostgruppen in Instanz2
      checkmk.general.checkmk_hostgroup:
        server_url: "{{ instance2_url }}"
        site: "{{ instance2_site }}"
        automation_user: "{{ instance2_user }}"
        automation_secret: "{{ vault_instance2_secret }}"
        name: "{{ item.name }}"
        title: "{{ item.title }}"
        state: present
      loop: "{{ hostgroups }}"
      vars:
        instance2_url: "https://monitoring2.example.com"
        instance2_site: "mysite2"
        instance2_user: "automation"
        instance2_secret: "{{ vault_instance2_secret }}"
```

#### Erklärung
- **Git-Repository**: Das Modul `ansible.builtin.git` klont oder aktualisiert das Repository, um die `hostgroups.yml`-Datei verfügbar zu machen.
- **Datei laden**: Das Lookup-Plugin `file` liest die `hostgroups.yml`-Datei und wandelt sie mit `from_yaml` in eine Liste von Hostgruppen-Dictionaries um.
- **Hostgruppen erstellen**: Das Modul `checkmk.general.checkmk_hostgroup` erstellt jede Hostgruppe in Instanz2 mit den Attributen `name` und `title`.
- **Vault**: Das `automation_secret` für Instanz2 wird sicher in einer Vault-Variablen (`vault_instance2_secret`) gespeichert.

#### Ausführen
```bash
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
```

#### Ergebnis
Die Hostgruppen aus `hostgroups.yml` (z. B. `web_servers`, `db_servers`) werden in Instanz2 erstellt.

### 4. Vault für sichere Zugangsdaten
Speichere die Zugangsdaten für beide Instanzen sicher in einer Vault-Datei:

```bash
ansible-vault create vault.yml
```

Inhalt der `vault.yml`:
```yaml
vault_instance1_secret: dein_geheimes_passwort_instanz1
vault_instance2_secret: dein_geheimes_passwort_instanz2
```

Führe die Playbooks mit der Vault-Datei aus:
```bash
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
```

### 5. Fehlerbehandlung
- **Keine Hostgruppen**: Wenn Instanz1 keine Hostgruppen hat, ist die `hostgroups.yml`-Datei leer. Überprüfe die Konfiguration in Instanz1.
- **Ungültige Zugangsdaten**: Stelle sicher, dass `automation_user` und `automation_secret` für beide Instanzen korrekt sind.
- **Git-Zugriff**: Überprüfe SSH-Schlüssel oder HTTPS-Zugangsdaten (z. B. Personal Access Token) bei Git-Fehlern.
- **Datei nicht gefunden**: Stelle sicher, dass `hostgroups.yml` im `backup_dir` existiert, bevor du das Restore-Playbook ausführst.
- **TLS-Zertifikate**: Wenn HTTPS verwendet wird, überprüfe die Zertifikate oder setze `validate_certs: false` (nur für Testumgebungen).
- **Checkmk-Version**: Stelle sicher, dass die Collection mit den Checkmk-Versionen beider Instanzen kompatibel ist (siehe `SUPPORT.md`).

## Hinweise
- **Automatisierung**: Plane die Playbooks mit einem Scheduler (z. B. Ansible Tower/AWX oder Cron), um regelmäßige Backups durchzuführen.
- **Erweiterung**: Um weitere Konfigurationen (z. B. Ordner, Regeln) zu sichern, kannst du das Playbook mit zusätzlichen Lookup-Plugins wie `checkmk.general.folder` oder `checkmk.general.rules` erweitern.
- **Git-Repository**: Verwende ein dediziertes Repository für Backups, um Konflikte zu vermeiden. Für große Dateien (z. B. bei zusätzlichen Backups wie `omd backup`) prüfe die Nutzung von Git LFS.
- **Dokumentation**: Weitere Details zu Modulen und Lookup-Plugins findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **Hostgruppen-Attribute**: Die Collection unterstützt aktuell `name` und `title` für Hostgruppen. Für benutzerdefinierte Attribute prüfe die Checkmk-API-Dokumentation.

## Fazit
Mit der `checkmk.general` Ansible Collection kannst du Hostgruppen effizient aus einer Checkmk-Instanz sichern und in eine andere Instanz kopieren. Dieses HowTo zeigt, wie du Hostgruppen in eine YAML-Datei exportierst, in ein Git-Repository versionierst und in einer neuen Instanz wiederherstellst, was für die Migration oder Synchronisation von Monitoring-Konfigurationen nützlich ist.
