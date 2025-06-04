# Wie man Ordner und Hosts in Checkmk aus einer CSV-Datei mit der Ansible Collection erstellt

Dieses HowTo beschreibt, wie man das Playbook `hosts-and-folders.yml` aus dem Repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/hosts-and-folders.yml) anpasst, um Ordner und Hosts in Checkmk basierend auf einer CSV-Datei zu erstellen. Es verwendet die `checkmk.general` Ansible Collection, um Ordner (`checkmk.general.folder`) und Hosts (`checkmk.general.checkmk_host`) zu erstellen, sowie das Modul `community.general.read_csv`, um die Informationen aus einer CSV-Datei einzulesen. Zusätzlich können Hosts dynamisch basierend auf einer Abfrage erstellt werden.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit den Collections).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **community.general Collection**: Installiert via `ansible-galaxy collection install community.general` (für das `read_csv`-Modul).
- **Checkmk-Server**: Zugang zu einer Checkmk-Instanz mit aktivierter Web-API.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Automatisierungs-API.
- **Vault (empfohlen)**: Für die sichere Speicherung des `automation_secret`.
- **Netzwerkzugriff**: Der Ansible-Controller muss den Checkmk-Server über HTTP/HTTPS erreichen können.
- **CSV-Datei**: Eine CSV-Datei mit den Ordner- und Hostinformationen, die im Playbook eingelesen wird.

## CSV-Datei vorbereiten
Erstelle eine CSV-Datei (z. B. `hosts_and_folders.csv`), die die Ordner und Hosts definiert. Die Datei sollte die folgenden Spalten enthalten:
- `type`: Typ des Eintrags (`folder` oder `host`).
- `name`: Name des Ordners (z. B. `/my_folder`) oder Hosts (z. B. `myhost1.local`).
- `title`: Anzeigename des Ordners (z. B. `My Folder`) oder Alias des Hosts (z. B. `My Host 1`).
- `folder` (nur für Hosts): Ordnerpfad, in dem der Host erstellt wird (z. B. `/my_folder` oder `/` für Root).
- `ipaddress` (optional, nur für Hosts): IP-Adresse des Hosts (z. B. `192.168.1.100`).
- `tag_os` (optional, nur für Hosts): Host-Tag für das Betriebssystem (z. B. `linux`).
- `labels` (optional, nur für Hosts): JSON-Format für Labels (z. B. `{"env": "prod"}`).

**Beispiel für `hosts_and_folders.csv`**:
```csv
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,,
folder,/prod_servers,Production Servers,,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
```

Speichere die Datei im gleichen Verzeichnis wie das Playbook oder passe den Pfad im Playbook an.

## Schritte

### 1. Playbook erstellen oder anpassen
Erstelle ein neues Playbook (z. B. `create_hosts_and_folders_from_csv.yml`) oder passe das ursprüngliche `hosts-and-folders.yml` an, um die Ordner und Hosts aus der CSV-Datei einzulesen.

**Playbook: `create_hosts_and_folders_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com"
    site: "mysite"
    automation_user: "automation"
    automation_secret: "{{ vault_automation_secret }}"
    csv_file: "hosts_and_folders.csv"
  tasks:
    # CSV-Datei einlesen
    - name: Read folders and hosts from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}"
        key: name
      register: csv_data

    # Ordner erstellen
    - name: Create folders from CSV
      checkmk.general.folder:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        path: "{{ item.name }}"
        title: "{{ item.title }}"
        state: present
      loop: "{{ csv_data.list | selectattr('type', 'equalto', 'folder') | list }}"

    # Hosts erstellen
    - name: Create hosts from CSV
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item.name }}"
        folder: "{{ item.folder | default('/') }}"
        attributes:
          alias: "{{ item.title }}"
          ipaddress: "{{ item.ipaddress | default(omit) }}"
          tag_os: "{{ item.tag_os | default(omit) }}"
          labels: "{{ item.labels | default({}) | from_json }}"
        state: present
      loop: "{{ csv_data.list | selectattr('type', 'equalto', 'host') | list }}"

    # Dynamische Hosts erstellen (Beispiel)
    - name: Create dynamic hosts from query
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "ansible-{{ item }}-{{ 1000 | random }}"
        folder: "/my_folder"
        attributes:
          tag_os: linux
          labels:
            source: ansible
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}"
```

#### Erklärung
- **CSV-Einlesen**: Das Modul `community.general.read_csv` liest die Datei `hosts_and_folders.csv` und speichert die Daten in `csv_data`. Die Option `key: name` indiziert jede Zeile nach dem `name`-Feld.
- **Ordner erstellen**: Die Aufgabe filtert Einträge mit `type: folder` und erstellt Ordner mit den angegebenen `path` und `title` Werten.
- **Hosts erstellen**: Die Aufgabe filtert Einträge mit `type: host` und erstellt Hosts mit den angegebenen Attributen (`alias`, `ipaddress`, `tag_os`, `labels`). Der `folder`-Wert bestimmt den Zielordner, standardmäßig `/` (Root).
- **Dynamische Host-Erstellung**: Die letzte Aufgabe bleibt ähnlich wie im Original, erstellt aber Hosts basierend auf einer Abfrage (z. B. `os: linux`) mit einem zufälligen Suffix im Namen.
- **Vault**: Das `automation_secret` wird sicher in einer Vault-Variablen gespeichert.

### 2. Variablen anpassen
Passe die Variablen im Playbook an deine Umgebung an:
- **server_url**: Ersetze durch die URL deines Checkmk-Servers (z. B. `https://monitoring.example.com`).
- **site**: Ersetze durch den Namen deiner Checkmk-Site.
- **automation_user**: Verwende den Benutzernamen für die Automatisierungs-API (z. B. `automation`).
- **automation_secret**: Verwende die Vault-Variable (z. B. `{{ vault_automation_secret }}`).
- **csv_file**: Stelle sicher, dass der Pfad zur CSV-Datei korrekt ist (z. B. `hosts_and_folders.csv` im gleichen Verzeichnis wie das Playbook).
- **query**: Passe die Abfrage im Lookup-Plugin an, um die gewünschten Hosts zu filtern (z. B. `{"host_labels": {"env": "prod"}}`).

#### Vault-Datei erstellen
```bash
ansible-vault create vault.yml
```

Inhalt der `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

### 3. CSV-Datei bereitstellen
Erstelle die Datei `hosts_and_folders.csv` im gleichen Verzeichnis wie das Playbook oder passe den Pfad in der Variable `csv_file` an. Beispielinhalt:
```csv
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,,
folder,/prod_servers,Production Servers,,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
```

### 4. Playbook ausführen
Führe das Playbook aus, um die Ordner und Hosts zu erstellen:

```bash
ansible-playbook create_hosts_and_folders_from_csv.yml --vault-id vault.yml
```

### 5. Aufgaben des Playbooks
Das Playbook führt drei Hauptaufgaben aus:
1. **Einlesen der CSV-Datei**:
   - Liest die `hosts_and_folders.csv` Datei und speichert die Daten in `csv_data`.
2. **Erstellen von Ordnern**:
   - Erstellt Ordner (z. B. `/my_folder`, `/prod_servers`) basierend auf den CSV-Einträgen mit `type: folder`.
3. **Erstellen von Hosts**:
   - Erstellt Hosts (z. B. `myhost1.local`, `myhost2.local`) basierend auf den CSV-Einträgen mit `type: host`, mit den angegebenen Attributen und Ordnerzuweisungen.
4. **Dynamische Host-Erstellung**:
   - Erstellt Hosts basierend auf einer Abfrage (z. B. `os: linux`) mit einem zufälligen Suffix und weist sie dem Ordner `/my_folder` zu.

### 6. Änderungen aktivieren
Nach der Ausführung des Playbooks müssen die Änderungen in Checkmk aktiviert werden, da das Hinzufügen von Ordnern und Hosts die Konfiguration verändert:
1. Melde dich in der Checkmk-Weboberfläche an.
2. Gehe zu **Setup > Activate Changes** und aktiviere die ausstehenden Änderungen.
3. Alternativ, aktiviere die Änderungen über die Checkmk-API:
   ```bash
   curl -X POST "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/activation_run/actions/activate-changes/invoke" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```

### 7. Überprüfen der Ergebnisse
Nach der Ausführung des Playbooks:
1. Melde dich in der Checkmk-Weboberfläche an und navigiere zu:
   - **Setup > Hosts > Folders**, um die erstellten Ordner (z. B. `/my_folder`, `/prod_servers`) zu überprüfen.
   - **Monitor > All hosts**, um die erstellten Hosts (z. B. `myhost1.local`, `myhost2.local`) zu überprüfen.
2. Überprüfe die Host-Details:
   - Wähle einen Host aus und prüfe unter **Properties**, ob die Attribute (`alias`, `ipaddress`, `tag_os`, `labels`) korrekt gesetzt sind.
   - Überprüfe den Ordner unter **Host > Folder**.
3. Alternativ, prüfe Ordner und Hosts über die Checkmk-API:
   ```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/folder_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```
   ```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```

### 8. Fehlerbehandlung
- **CSV-Datei nicht gefunden**: Stelle sicher, dass `hosts_and_folders.csv` existiert und der Pfad in `csv_file` korrekt ist.
- **Ungültiges CSV-Format**: Überprüfe, ob die CSV-Datei die erforderlichen Spalten (`type`, `name`, `title`) enthält und korrekt formatiert ist. JSON-Daten in `labels` müssen gültig sein.
- **Ordner/Host existiert bereits**: Wenn ein Ordner oder Host bereits existiert, ignoriert das Modul die Erstellung (idempotentes Verhalten). Setze `state: absent`, um bestehende Objekte zu löschen.
- **Hosts nicht gefunden**: Wenn die Abfrage im Lookup-Plugin keine Hosts zurückgibt (z. B. weil kein Host den Tag `os: linux` hat), überspringt die Aufgabe die Erstellung. Überprüfe die Abfrage (`query`) und die Host-Tags in Checkmk.
- **Ungültige Zugangsdaten**: Stelle sicher, dass `automation_user` und `automation_secret` korrekt sind.
- **Netzwerkprobleme**: Überprüfe die Erreichbarkeit des Checkmk-Servers (`server_url`) und die korrekte Portfreigabe (HTTP/HTTPS).
- **TLS-Zertifikate**: Bei HTTPS, stelle sicher, dass das Zertifikat gültig ist, oder setze `validate_certs: false` im Playbook (nur für Testumgebungen).
- **Checkmk-Version**: Stelle sicher, dass die Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).

### 9. Anpassungen und Erweiterungen
- **Erweiterte CSV-Attribute**: Füge weitere Spalten zur CSV-Datei hinzu (z. B. weitere Tags oder benutzerdefinierte Attribute), wenn zukünftige Checkmk-Versionen diese unterstützen.
- **Dynamische Abfragen**: Passe die Abfrage im Lookup-Plugin an, um andere Kriterien zu verwenden (z. B. `{"host_labels": {"env": "prod"}}` oder `{"folder": "/production"}`).
- **Host-Löschung**: Setze `state: absent` in den Host-Aufgaben, um bestehende Hosts zu entfernen.
- **Ordner-Hierarchien**: Erstelle verschachtelte Ordner, indem du Pfade wie `/parent/child` in der CSV-Datei definierst.
- **Automatisierung**: Plane das Playbook mit einem Scheduler (z. B. Ansible Tower/AWX oder Cron), um Ordner und Hosts regelmäßig zu aktualisieren.
- **Erweiterte CSV-Struktur**: Du kannst die CSV-Datei erweitern, um zusätzliche Konfigurationen wie Gruppenzuweisungen oder Downtimes zu definieren.

## Hinweise
- **Sicherheit**: Verwende immer eine Vault-Datei für das `automation_secret`, um sensible Daten zu schützen.
- **Checkmk-Version**: Stelle sicher, dass die `checkmk.general` Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).
- **Dokumentation**: Weitere Details zu Modulen und Lookup-Plugins findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **Testumgebung**: Teste das Playbook in einer nicht-produktiven Umgebung, um unerwartete Auswirkungen zu vermeiden.
- **CSV-Format**: Stelle sicher, dass die CSV-Datei korrekt formatiert ist (z. B. keine fehlenden Spalten oder ungültigen JSON-Daten in `labels`).
- **Änderungsaktivierung**: Nach dem Hinzufügen von Ordnern und Hosts müssen Änderungen in Checkmk aktiviert werden, entweder manuell oder über die API.

## Fazit
Das angepasste Playbook `create_hosts_and_folders_from_csv.yml` ermöglicht es, Ordner und Hosts in Checkmk basierend auf einer CSV-Datei zu erstellen und Hosts dynamisch zu konfigurieren. Mit der `checkmk.general` Collection und dem `community.general.read_csv` Modul kannst du die Verwaltung von Monitoring-Hierarchien flexibel und skalierbar automatisieren, was besonders nützlich für die Organisation von Hosts in großen Umgebungen ist. Durch Anpassung der CSV-Datei und der Abfragen kannst du das Playbook an deine spezifischen Anforderungen anpassen.
