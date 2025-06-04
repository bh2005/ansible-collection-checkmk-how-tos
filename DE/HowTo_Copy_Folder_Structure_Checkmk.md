# Wie man die Ordnerstruktur von einer Checkmk-Instanz in eine andere kopiert

Dieses HowTo beschreibt, wie man die Ordnerstruktur aus einer Checkmk-Instanz (Instanz1) in eine andere Checkmk-Instanz (Instanz2) kopiert, indem man die `checkmk.general` Ansible Collection verwendet. Es wird das Lookup-Plugin `checkmk.general.folder` genutzt, um die Ordner und deren Attribute aus Instanz1 abzurufen, und das Modul `checkmk.general.checkmk_folder`, um diese Ordner in Instanz2 zu erstellen.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit der Collection).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Instanzen**: Zugang zu beiden Checkmk-Instanzen (Instanz1 und Instanz2) mit API-Zugriff.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Automatisierungs-API beider Instanzen.
- **Vault (empfohlen)**: Für die sichere Speicherung der Zugangsdaten (`automation_secret`).
- **Netzwerkzugriff**: Beide Checkmk-Server müssen erreichbar sein.

## Schritte

### 1. Ordnerstruktur aus Instanz1 abrufen
Erstelle ein Playbook, um die Ordnerstruktur von Instanz1 abzufragen. Dieses Playbook verwendet das Lookup-Plugin `checkmk.general.folder`, um die Attribute aller Ordner zu sammeln.

#### Playbook: `get_folder_structure.yml`
```yaml
- name: Abrufen der Ordnerstruktur von Instanz1
  hosts: localhost
  tasks:
    - name: Sammle alle Ordner von Instanz1
      ansible.builtin.set_fact:
        folders: "{{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret)] }}"
      loop: "{{ instance1_folders }}"
      vars:
        instance1_url: "https://monitoring1.example.com"
        instance1_site: "mysite1"
        instance1_user: "automation"
        instance1_secret: "{{ vault_instance1_secret }}"
        instance1_folders:
          - "/"
          - "/production_servers"
          - "/test_servers"
          - "/development"

    - name: Zeige gesammelte Ordner an
      ansible.builtin.debug:
        msg: "{{ folders }}"
```

#### Erklärung
- **Loop**: Die Liste `instance1_folders` enthält die Pfade der Ordner, die abgerufen werden sollen (z. B. Root-Ordner `/` und Unterordner wie `/production_servers`).
- **Lookup-Plugin**: `checkmk.general.folder` ruft die Attribute jedes Ordners (z. B. `criticality`, `network_segment`) ab.
- **set_fact**: Die Ergebnisse werden in der Variable `folders` gespeichert.
- **Vault**: Das `automation_secret` für Instanz1 wird sicher in einer Vault-Variablen (`vault_instance1_secret`) gespeichert.

#### Ausführen
```bash
ansible-playbook get_folder_structure.yml --vault-id vault.yml
```

#### Ergebnis
Die Variable `folders` enthält eine Liste von Dictionaries mit den Attributen aller abgerufenen Ordner, z. B.:
```json
[
  {"path": "/", "attributes": {"criticality": "prod"}},
  {"path": "/production_servers", "attributes": {"criticality": "prod", "network_segment": "dmz"}},
  ...
]
```

### 2. Ordnerstruktur in Instanz2 erstellen
Erstelle ein zweites Playbook, um die abgerufene Ordnerstruktur in Instanz2 zu replizieren. Das Modul `checkmk.general.checkmk_folder` wird verwendet, um die Ordner mit denselben Attributen zu erstellen.

#### Playbook: `create_folder_structure.yml`
```yaml
- name: Erstellen der Ordnerstruktur in Instanz2
  hosts: localhost
  tasks:
    - name: Erstelle Ordner in Instanz2
      checkmk.general.checkmk_folder:
        server_url: "{{ instance2_url }}"
        site: "{{ instance2_site }}"
        automation_user: "{{ instance2_user }}"
        automation_secret: "{{ vault_instance2_secret }}"
        path: "{{ item.path }}"
        attributes: "{{ item.attributes }}"
        state: present
      loop: "{{ folders }}"
  vars:
    instance2_url: "https://monitoring2.example.com"
    instance2_site: "mysite2"
    instance2_user: "automation"
    instance2_secret: "{{ vault_instance2_secret }}"
    folders: "{{ hostvars['localhost']['folders'] | default([]) }}"
```

#### Erklärung
- **Loop**: Iteriert über die Liste `folders`, die aus dem ersten Playbook stammt.
- **checkmk_folder**: Erstellt jeden Ordner mit dem Pfad (`path`) und den Attributen (`attributes`) aus Instanz1.
- **Vault**: Das `automation_secret` für Instanz2 wird sicher in einer Vault-Variablen (`vault_instance2_secret`) gespeichert.
- **folders**: Die Variable `folders` muss aus dem ersten Playbook verfügbar sein (z. B. durch Speichern in einer Datei oder Übergabe zwischen Playbooks).

#### Ausführen
```bash
ansible-playbook create_folder_structure.yml --vault-id vault.yml
```

#### Ergebnis
Die Ordnerstruktur von Instanz1 (z. B. `/`, `/production_servers`, `/test_servers`, `/development`) wird in Instanz2 mit denselben Attributen erstellt.

### 3. Vault für sichere Zugangsdaten
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
ansible-playbook get_folder_structure.yml --vault-id vault.yml
ansible-playbook create_folder_structure.yml --vault-id vault.yml
```

### 4. Kombinieren der Playbooks (optional)
Um den Prozess zu vereinfachen, kannst du beide Schritte in einem Playbook kombinieren:

#### Kombiniertes Playbook: `copy_folder_structure.yml`
```yaml
- name: Kopieren der Ordnerstruktur von Instanz1 nach Instanz2
  hosts: localhost
  tasks:
    - name: Abrufen der Ordnerstruktur von Instanz1
      ansible.builtin.set_fact:
        folders: "{{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret)] }}"
      loop: "{{ instance1_folders }}"
      vars:
        instance1_url: "https://monitoring1.example.com"
        instance1_site: "mysite1"
        instance1_user: "automation"
        instance1_secret: "{{ vault_instance1_secret }}"
        instance1_folders:
          - "/"
          - "/production_servers"
          - "/test_servers"
          - "/development"

    - name: Erstellen der Ordner in Instanz2
      checkmk.general.checkmk_folder:
        server_url: "{{ instance2_url }}"
        site: "{{ instance2_site }}"
        automation_user: "{{ instance2_user }}"
        automation_secret: "{{ vault_instance2_secret }}"
        path: "{{ item.path }}"
        attributes: "{{ item.attributes }}"
        state: present
      loop: "{{ folders }}"
  vars:
    instance2_url: "https://monitoring2.example.com"
    instance2_site: "mysite2"
    instance2_user: "automation"
    instance2_secret: "{{ vault_instance2_secret }}"
```

#### Ausführen
```bash
ansible-playbook copy_folder_structure.yml --vault-id vault.yml
```

### 5. Fehlerbehandlung
- **Ordner existiert nicht**: Das Lookup-Plugin gibt eine Fehlermeldung, wenn ein Ordner in Instanz1 nicht existiert. Überprüfe die Liste `instance1_folders`.
- **Ungültige Zugangsdaten**: Stelle sicher, dass `automation_user` und `automation_secret` für beide Instanzen korrekt sind.
- **Netzwerkprobleme**: Überprüfe, ob beide Server erreichbar sind und die `server_url` korrekt ist.
- **TLS-Zertifikate**: Wenn HTTPS verwendet wird, stelle sicher, dass die Zertifikate gültig sind oder setze `validate_certs: false` (nur für Testumgebungen).

## Hinweise
- **Ordnerliste**: Die Liste `instance1_folders` muss die Pfade aller Ordner enthalten, die kopiert werden sollen. Du kannst die Liste dynamisch erweitern, indem du die Checkmk-API direkt abfragst, um alle Ordner zu finden.
- **Attribute**: Nicht alle Attribute (z. B. benutzerdefinierte Tags) sind in jeder Checkmk-Version verfügbar. Überprüfe die API-Dokumentation deiner Checkmk-Version.
- **Dokumentation**: Weitere Details zu Modulen und Plugins findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **Skalierung**: Für große Ordnerstrukturen kann das Playbook angepasst werden, um Unterordner rekursiv abzufragen (erfordert zusätzliche API-Abfragen).

## Fazit
Mit der `checkmk.general` Ansible Collection kannst du die Ordnerstruktur effizient von einer Checkmk-Instanz in eine andere kopieren. Dieses HowTo zeigt, wie du Ordner und deren Attribute mit minimalem Aufwand replizieren kannst, was besonders nützlich für die Synchronisation von Monitoring-Umgebungen ist.
