# Wie man Monitoring-Konfigurationen mit der Checkmk Ansible Collection automatisiert

Dieses HowTo beschreibt fünf konkrete Beispiele, wie die `checkmk.general` Ansible Collection genutzt werden kann, um Monitoring-Konfigurationen in Checkmk zu automatisieren. Die Beispiele umfassen das Erstellen von Ordnern, Regeln, Benutzern, Hostgruppen und die Nutzung des Lookup-Plugins für Ordnerattribute.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit der Collection).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Server**: Zugang zu einem laufenden Checkmk-Server mit API-Zugriff.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Checkmk Automatisierungs-API.
- **Vault (empfohlen)**: Für die sichere Speicherung des `automation_secret`.
- **Ordner/Hosts**: Einige Beispiele setzen voraus, dass bestimmte Ordner oder Hosts existieren.

## Beispiel 1: Erstellen eines Ordners
Dieses Beispiel zeigt, wie man einen Ordner in Checkmk erstellt, um Hosts zu organisieren.

### Playbook
Erstelle eine YAML-Datei (z. B. `create_folder.yml`):

```yaml
- name: Erstelle einen Ordner für Produktionsserver
  hosts: localhost
  tasks:
    - name: Ordner erstellen
      checkmk.general.checkmk_folder:
        server_url: "https://monitoring.example.com"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        path: "/production_servers"
        attributes:
          criticality: "prod"
          network_segment: "dmz"
        state: present
```

### Ausführen
```bash
ansible-playbook create_folder.yml --vault-id vault.yml
```

### Ergebnis
Ein Ordner `/production_servers` wird mit den Attributen `criticality: prod` und `network_segment: dmz` erstellt.

## Beispiel 2: Erstellen einer Monitoring-Regel
Dieses Beispiel definiert eine Regel für die Speicherüberwachung von Linux-Servern.

### Playbook
Erstelle eine YAML-Datei (z. B. `create_rule.yml`):

```yaml
- name: Setze Speicherüberwachungsregel für Linux-Server
  hosts: localhost
  tasks:
    - name: Regel erstellen
      checkmk.general.checkmk_rule:
        server_url: "https://monitoring.example.com"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        ruleset: "memory"
        folder: "/linux_servers"
        conditions:
          host_tags:
            os: linux
        properties:
          levels:
            warning: 80
            critical: 90
        state: present
```

### Ausführen
```bash
ansible-playbook create_rule.yml --vault-id vault.yml
```

### Ergebnis
Eine Regel wird erstellt, die Warnungen bei 80 % und kritische Alarme bei 90 % Speicherauslastung für Linux-Server im Ordner `/linux_servers` auslöst.

## Beispiel 3: Benutzerverwaltung mit Rollenzuweisung
Dieses Beispiel erstellt einen neuen Benutzer mit Administratorrechten.

### Playbook
Erstelle eine YAML-Datei (z. B. `create_user.yml`):

```yaml
- name: Erstelle einen neuen Benutzer mit Admin-Rechten
  hosts: localhost
  tasks:
    - name: Benutzer erstellen
      checkmk.general.checkmk_user:
        server_url: "https://monitoring.example.com"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        username: "jdoe"
        fullname: "John Doe"
        password: "{{ vault_user_password }}"
        roles:
          - admin
        contactgroups:
          - "all_admins"
        state: present
```

### Ausführen
```bash
ansible-playbook create_user.yml --vault-id vault.yml
```

### Ergebnis
Ein Benutzer `jdoe` wird mit Administratorrechten und der Kontaktgruppe `all_admins` erstellt.

## Beispiel 4: Erstellen einer Hostgruppe
Dieses Beispiel zeigt, wie man eine Hostgruppe erstellt, um Hosts zu gruppieren.

### Playbook
Erstelle eine YAML-Datei (z. B. `create_hostgroup.yml`):

```yaml
- name: Erstelle eine Hostgruppe für Webserver
  hosts: localhost
  tasks:
    - name: Hostgruppe erstellen
      checkmk.general.checkmk_hostgroup:
        server_url: "https://monitoring.example.com"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        name: "web_servers"
        title: "Web Servers"
        state: present
```

### Ausführen
```bash
ansible-playbook create_hostgroup.yml --vault-id vault.yml
```

### Ergebnis
Eine Hostgruppe `web_servers` wird erstellt, die Hosts mit ähnlichen Eigenschaften (z. B. Webserver) zusammenfasst.

## Beispiel 5: Abfragen von Ordnerattributen
Dieses Beispiel zeigt, wie man alle Attribute eines Ordners mit dem Lookup-Plugin abfragt.

### Playbook
Erstelle eine YAML-Datei (z. B. `show_folder_attributes.yml`):

```yaml
- name: Zeige alle Attribute eines Ordners an
  hosts: localhost
  tasks:
    - name: Abfrage der Ordnerattribute
      ansible.builtin.debug:
        msg: "{{ lookup('checkmk.general.folder', folder_path, server_url='https://monitoring.example.com', site='mysite', automation_user='automation', automation_secret=automation_secret) }}"
      vars:
        folder_path: "/production_servers"
        automation_secret: "{{ vault_automation_secret }}"
```

### Ausführen
```bash
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
```

### Ergebnis
Die Attribute des Ordners `/production_servers` (z. B. `criticality`, `network_segment`) werden im JSON-Format ausgegeben.

## Vault für sichere Zugangsdaten (optional)
Für alle Beispiele kannst du sensible Daten wie `automation_secret` oder `vault_user_password` in einer Ansible Vault-Datei speichern:

```bash
ansible-vault create vault.yml
```

Inhalt der `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
vault_user_password: benutzer_passwort
```

Führe die Playbooks mit der Vault-Datei aus:
```bash
ansible-playbook <playbook>.yml --vault-id vault.yml
```

## Hinweise
- **Fehlerbehandlung**: Stelle sicher, dass der Checkmk-Server erreichbar ist, die Zugangsdaten korrekt sind und die angegebenen Ordner/Hosts existieren.
- **Dokumentation**: Weitere Details zu Modulen und Optionen findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **TLS**: Wenn dein Server HTTPS verwendet, überprüfe die Zertifikatsprüfung (füge ggf. `validate_certs: false` hinzu, wenn kein gültiges Zertifikat vorliegt – nur für Testumgebungen).
- **Checkmk-Version**: Stelle sicher, dass die verwendete Checkmk-Version mit der Collection kompatibel ist (siehe `SUPPORT.md`).

## Fazit
Die `checkmk.general` Collection bietet leistungsstarke Werkzeuge zur Automatisierung von Checkmk-Konfigurationen. Mit diesen Beispielen kannst du Ordner, Regeln, Benutzer, Hostgruppen und mehr effizient verwalten und anpassen.
