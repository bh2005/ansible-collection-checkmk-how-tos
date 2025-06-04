# Wie man Host- und Servicegruppen in Checkmk aus einer CSV-Datei mit der Ansible Collection erstellt

Dieses HowTo beschreibt, wie man das Playbook `groups.yml` aus dem Repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/groups.yml) anpasst, um Host- und Servicegruppen in Checkmk basierend auf einer CSV-Datei zu erstellen. Es verwendet die `checkmk.general` Ansible Collection, um Hostgruppen (`checkmk.general.checkmk_hostgroup`) und Servicegruppen (`checkmk.general.checkmk_servicegroup`) zu erstellen, sowie das Modul `community.general.read_csv`, um die Gruppeninformationen aus einer CSV-Datei einzulesen. Zusätzlich können Hosts dynamisch einer Hostgruppe zugewiesen werden, basierend auf Tags oder anderen Kriterien.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit den Collections).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **community.general Collection**: Installiert via `ansible-galaxy collection install community.general` (für das `read_csv`-Modul).
- **Checkmk-Server**: Zugang zu einer Checkmk-Instanz mit aktivierter Web-API.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Automatisierungs-API.
- **Vault (empfohlen)**: Für die sichere Speicherung des `automation_secret`.
- **Netzwerkzugriff**: Der Ansible-Controller muss den Checkmk-Server über HTTP/HTTPS erreichen können.
- **Hosts**: Die im Playbook angesprochenen Hosts (z. B. mit dem Tag `os: linux`) müssen in der Checkmk-Instanz existieren.
- **CSV-Datei**: Eine CSV-Datei mit den Gruppeninformationen, die im Playbook eingelesen wird.

## CSV-Datei vorbereiten
Erstelle eine CSV-Datei (z. B. `groups.csv`), die die Host- und Servicegruppen definiert. Die Datei sollte mindestens die folgenden Spalten enthalten:
- `type`: Typ der Gruppe (`hostgroup` oder `servicegroup`).
- `name`: Name der Gruppe (z. B. `web_servers`).
- `title`: Anzeigename der Gruppe (z. B. `Web Servers`).

**Beispiel für `groups.csv`**:
```csv
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
```

Speichere die Datei im gleichen Verzeichnis wie das Playbook oder passe den Pfad im Playbook an.

## Schritte

### 1. Playbook erstellen oder anpassen
Erstelle ein neues Playbook (z. B. `create_groups_from_csv.yml`) oder passe das ursprüngliche `groups.yml` an, um die Gruppen aus der CSV-Datei einzulesen.

**Playbook: `create_groups_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com"
    site: "mysite"
    automation_user: "automation"
    automation_secret: "{{ vault_automation_secret }}"
    csv_file: "groups.csv"
  tasks:
    # CSV-Datei einlesen
    - name: Read groups from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}"
        key: name
      register: groups_data

    # Hostgruppen erstellen
    - name: Create host groups from CSV
      checkmk.general.checkmk_hostgroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item.name }}"
        title: "{{ item.title }}"
        state: present
      loop: "{{ groups_data.list | selectattr('type', 'equalto', 'hostgroup') | list }}"

    # Servicegruppen erstellen
    - name: Create service groups from CSV
      checkmk.general.checkmk_servicegroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item.name }}"
        title: "{{ item.title }}"
        state: present
      loop: "{{ groups_data.list | selectattr('type', 'equalto', 'servicegroup') | list }}"

    # Hosts einer Hostgruppe zuweisen (z. B. web_servers für Linux-Hosts)
    - name: Add hosts to a host group
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item }}"
        attributes:
          groups:
            host:
              - "web_servers"
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}"
```

#### Erklärung
- **CSV-Einlesen**: Das Modul `community.general.read_csv` liest die Datei `groups.csv` und speichert die Daten in `groups_data`. Die Option `key: name` stellt sicher, dass jede Zeile nach dem `name`-Feld indiziert wird.
- **Hostgruppen erstellen**: Die Aufgabe filtert Einträge mit `type: hostgroup` und erstellt Hostgruppen mit den angegebenen `name` und `title` Werten.
- **Servicegruppen erstellen**: Die Aufgabe filtert Einträge mit `type: servicegroup` und erstellt Servicegruppen.
- **Hostzuweisung**: Hosts mit dem Tag `os: linux` werden der Hostgruppe `web_servers` zugewiesen. Passe den Gruppennamen (`web_servers`) oder die Abfrage (`{'host_tags': {'os': 'linux'}}`) an deine Bedürfnisse an.
- **Vault**: Das `automation_secret` wird sicher in einer Vault-Variablen gespeichert.

### 2. Variablen anpassen
Passe die Variablen im Playbook an deine Umgebung an:
- **server_url**: Ersetze durch die URL deines Checkmk-Servers (z. B. `https://monitoring.example.com`).
- **site**: Ersetze durch den Namen deiner Checkmk-Site.
- **automation_user**: Verwende den Benutzernamen für die Automatisierungs-API (z. B. `automation`).
- **automation_secret**: Verwende die Vault-Variable (z. B. `{{ vault_automation_secret }}`).
- **csv_file**: Stelle sicher, dass der Pfad zur CSV-Datei korrekt ist (z. B. `groups.csv` im gleichen Verzeichnis wie das Playbook).
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
Erstelle die Datei `groups.csv` im gleichen Verzeichnis wie das Playbook oder passe den Pfad in der Variable `csv_file` an. Beispielinhalt:
```csv
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
```

### 4. Playbook ausführen
Führe das Playbook aus, um die Gruppen zu erstellen und Hosts zuzuweisen:

```bash
ansible-playbook create_groups_from_csv.yml --vault-id vault.yml
```

### 5. Aufgaben des Playbooks
Das Playbook führt drei Hauptaufgaben aus:
1. **Einlesen der CSV-Datei**:
   - Liest die `groups.csv` Datei und speichert die Daten in `groups_data`.
2. **Erstellen von Hostgruppen**:
   - Erstellt Hostgruppen (z. B. `web_servers`, `db_servers`) basierend auf den CSV-Einträgen mit `type: hostgroup`.
3. **Erstellen von Servicegruppen**:
   - Erstellt Servicegruppen (z. B. `http_services`, `database_services`) basierend auf den CSV-Einträgen mit `type: servicegroup`.
4. **Dynamische Zuweisung von Hosts zu einer Hostgruppe**:
   - Weist Hosts mit dem Tag `os: linux` der Hostgruppe `web_servers` zu (anpassbar).

### 6. Änderungen aktivieren
Nach der Ausführung des Playbooks müssen die Änderungen in Checkmk aktiviert werden, da die Zuweisung von Hosts zu einer Hostgruppe die Konfiguration verändert:
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
   - **Setup > Hosts > Host groups**, um die erstellten Hostgruppen (z. B. `web_servers`, `db_servers`) zu überprüfen.
   - **Setup > Services > Service groups**, um die erstellten Servicegruppen (z. B. `http_services`, `database_services`) zu überprüfen.
2. Überprüfe die Hostzuweisung:
   - Gehe zu **Monitor > All hosts**, wähle einen Host aus der Liste (z. B. mit dem Tag `os: linux`) und prüfe unter **Properties > Host groups**, ob `web_servers` zugewiesen ist.
3. Alternativ, prüfe die Gruppen über die Checkmk-API:
   ```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_group_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```

### 8. Fehlerbehandlung
- **CSV-Datei nicht gefunden**: Stelle sicher, dass `groups.csv` existiert und der Pfad in `csv_file` korrekt ist.
- **Ungültiges CSV-Format**: Überprüfe, ob die CSV-Datei die erforderlichen Spalten (`type`, `name`, `title`) enthält und korrekt formatiert ist.
- **Hostgruppe/Servicegruppe existiert bereits**: Wenn eine Gruppe bereits existiert, ignoriert das Modul die Erstellung (idempotentes Verhalten). Setze `state: absent`, um bestehende Gruppen zu löschen.
- **Hosts nicht gefunden**: Wenn die Abfrage im Lookup-Plugin keine Hosts zurückgibt (z. B. weil kein Host den Tag `os: linux` hat), überspringt die Aufgabe die Zuweisung. Überprüfe die Abfrage (`query`) und die Host-Tags in Checkmk.
- **Ungültige Zugangsdaten**: Stelle sicher, dass `automation_user` und `automation_secret` korrekt sind.
- **Netzwerkprobleme**: Überprüfe die Erreichbarkeit des Checkmk-Servers (`server_url`) und die korrekte Portfreigabe (HTTP/HTTPS).
- **TLS-Zertifikate**: Bei HTTPS, stelle sicher, dass das Zertifikat gültig ist, oder setze `validate_certs: false` im Playbook (nur für Testumgebungen).
- **Checkmk-Version**: Stelle sicher, dass die Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).

### 9. Anpassungen und Erweiterungen
- **Erweiterte CSV-Attribute**: Füge weitere Spalten zur CSV-Datei hinzu (z. B. `description` oder benutzerdefinierte Attribute), wenn zukünftige Checkmk-Versionen diese unterstützen.
- **Dynamische Abfragen**: Passe die Abfrage im Lookup-Plugin an, um andere Kriterien zu verwenden (z. B. `{"host_labels": {"env": "prod"}}` oder `{"folder": "/production"}`).
- **Servicegruppen-Zuweisung**: Um Services einer Servicegruppe zuzuweisen, kannst du das Modul `checkmk.general.checkmk_service` verwenden (nicht im Demo-Playbook enthalten, aber in der Collection verfügbar).
- **Entfernen von Gruppen**: Setze `state: absent` in den Aufgaben, um bestehende Host- oder Servicegruppen zu löschen.
- **Automatisierung**: Plane das Playbook mit einem Scheduler (z. B. Ansible Tower/AWX oder Cron), um Gruppen regelmäßig zu aktualisieren.
- **Erweiterte CSV-Struktur**: Du kannst die CSV-Datei erweitern, um auch Zuweisungsregeln zu definieren (z. B. eine Spalte `host_tags` für die dynamische Zuweisung von Hosts).

## Hinweise
- **Sicherheit**: Verwende immer eine Vault-Datei für das `automation_secret`, um sensible Daten zu schützen.
- **Checkmk-Version**: Stelle sicher, dass die `checkmk.general` Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).
- **Dokumentation**: Weitere Details zu Modulen und Lookup-Plugins findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **Testumgebung**: Teste das Playbook in einer nicht-produktiven Umgebung, um unerwartete Auswirkungen zu vermeiden.
- **CSV-Format**: Stelle sicher, dass die CSV-Datei korrekt formatiert ist (z. B. keine fehlenden Spalten oder ungültigen Zeichen).
- **Änderungsaktivierung**: Nach der Zuweisung von Hosts zu einer Hostgruppe müssen Änderungen in Checkmk aktiviert werden, entweder manuell oder über die API.

## Fazit
Das angepasste Playbook `create_groups_from_csv.yml` ermöglicht es, Host- und Servicegruppen in Checkmk basierend auf einer CSV-Datei zu erstellen und Hosts dynamisch einer Hostgruppe zuzuweisen. Mit der `checkmk.general` Collection und dem `community.general.read_csv` Modul kannst du die Gruppenverwaltung flexibel und skalierbar automatisieren, was besonders nützlich für die Verwaltung von Monitoring-Objekten in großen Umgebungen ist. Durch Anpassung der CSV-Datei und der Abfragen kannst du das Playbook an deine spezifischen Anforderungen anpassen.
