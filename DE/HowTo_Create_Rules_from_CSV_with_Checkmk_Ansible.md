# Wie man Regeln in Checkmk aus einer CSV-Datei mit der Ansible Collection erstellt

Dieses HowTo beschreibt, wie man das Playbook `rules.yml` aus dem Repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/rules.yml) anpasst, um Regeln in Checkmk basierend auf einer CSV-Datei zu erstellen. Es verwendet die `checkmk.general` Ansible Collection, um Regeln (`checkmk.general.rules`) für verschiedene Rulesets zu erstellen, sowie das Modul `community.general.read_csv`, um die Regelinformationen aus einer CSV-Datei einzulesen. Zusätzlich können bestehende Regeln dynamisch abgefragt und gespeichert werden.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit den Collections).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **community.general Collection**: Installiert via `ansible-galaxy collection install community.general` (für das `read_csv`-Modul).
- **Checkmk-Server**: Zugang zu einer Checkmk-Instanz mit aktivierter Web-API.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Automatisierungs-API.
- **Vault (empfohlen)**: Für die sichere Speicherung des `automation_secret`.
- **Netzwerkzugriff**: Der Ansible-Controller muss den Checkmk-Server über HTTP/HTTPS erreichen können.
- **CSV-Datei**: Eine CSV-Datei mit den Regelinformationen, die im Playbook eingelesen wird.

## CSV-Datei vorbereiten
Erstelle eine CSV-Datei (z. B. `rules.csv`), die die Regeln definiert. Die Datei sollte die folgenden Spalten enthalten:
- `ruleset`: Name des Rulesets (z. B. `notification_parameters`, `host_tags`, `checkgroup_parameters:filesystem`).
- `folder`: Zielordner für die Regel (z. B. `/` für Root oder `/my_folder`).
- `conditions`: JSON-Format für Regelbedingungen (z. B. `{"host_name": ["web.*"]}`).
- `value`: JSON-Format für Regelwerte (z. B. `{"method": "email", "contact_all": true}`).
- `description`: Beschreibung der Regel (z. B. `Email notifications for web servers`).

**Beispiel für `rules.csv`**:
```csv
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"}},{"levels": [85, 95]},Filesystem thresholds for critical services
```

Speichere die Datei im gleichen Verzeichnis wie das Playbook oder passe den Pfad im Playbook an.

## Schritte

### 1. Playbook erstellen oder anpassen
Erstelle ein neues Playbook (z. B. `create_rules_from_csv.yml`) oder passe das ursprüngliche `rules.yml` an, um die Regeln aus der CSV-Datei einzulesen.

**Playbook: `create_rules_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com"
    site: "mysite"
    automation_user: "automation"
    automation_secret: "{{ vault_automation_secret }}"
    csv_file: "rules.csv"
  tasks:
    # CSV-Datei einlesen
    - name: Read rules from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}"
        key: description
      register: rules_data

    # Regeln erstellen
    - name: Create rules from CSV
      checkmk.general.rules:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        ruleset: "{{ item.ruleset }}"
        folder: "{{ item.folder }}"
        conditions: "{{ item.conditions | from_json }}"
        value: "{{ item.value | from_json }}"
        description: "{{ item.description }}"
        state: present
      loop: "{{ rules_data.list }}"

    # Bestehende Regeln abrufen und speichern
    - name: Get all notification rules
      ansible.builtin.copy:
        content: "{{ query('checkmk.general.rules', 'notification_parameters', server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) | to_nice_yaml }}"
        dest: "notification_rules.yml"
```

#### Erklärung
- **CSV-Einlesen**: Das Modul `community.general.read_csv` liest die Datei `rules.csv` und speichert die Daten in `rules_data`. Die Option `key: description` indiziert jede Zeile nach dem `description`-Feld.
- **Regeln erstellen**: Die Aufgabe erstellt Regeln für die angegebenen Rulesets (`ruleset`), mit Bedingungen (`conditions`), Werten (`value`), und Beschreibungen (`description`) aus der CSV-Datei. Die Felder `conditions` und `value` werden aus JSON geparst.
- **Regeln abrufen**: Die letzte Aufgabe bleibt ähnlich wie im Original und speichert alle Regeln des Rulesets `notification_parameters` in einer YAML-Datei (`notification_rules.yml`).
- **Vault**: Das `automation_secret` wird sicher in einer Vault-Variablen gespeichert.

### 2. Variablen anpassen
Passe die Variablen im Playbook an deine Umgebung an:
- **server_url**: Ersetze durch die URL deines Checkmk-Servers (z. B. `https://monitoring.example.com`).
- **site**: Ersetze durch den Namen deiner Checkmk-Site.
- **automation_user**: Verwende den Benutzernamen für die Automatisierungs-API (z. B. `automation`).
- **automation_secret**: Verwende die Vault-Variable (z. B. `{{ vault_automation_secret }}`).
- **csv_file**: Stelle sicher, dass der Pfad zur CSV-Datei korrekt ist (z. B. `rules.csv` im gleichen Verzeichnis wie das Playbook).

#### Vault-Datei erstellen
```bash
ansible-vault create vault.yml
```

Inhalt der `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

### 3. CSV-Datei bereitstellen
Erstelle die Datei `rules.csv` im gleichen Verzeichnis wie das Playbook oder passe den Pfad in der Variable `csv_file` an. Beispielinhalt:
```csv
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"}},{"levels": [85, 95]},Filesystem thresholds for critical services
```

### 4. Playbook ausführen
Führe das Playbook aus, um die Regeln zu erstellen:

```bash
ansible-playbook create_rules_from_csv.yml --vault-id vault.yml
```

### 5. Aufgaben des Playbooks
Das Playbook führt zwei Hauptaufgaben aus:
1. **Einlesen der CSV-Datei**:
   - Liest die `rules.csv` Datei und speichert die Daten in `rules_data`.
2. **Erstellen von Regeln**:
   - Erstellt Regeln für die angegebenen Rulesets (z. B. `notification_parameters`, `host_tags`, `checkgroup_parameters:filesystem`) basierend auf den CSV-Einträgen, mit den angegebenen Bedingungen, Werten und Beschreibungen.
3. **Abrufen von Regeln**:
   - Ruft alle Regeln für das Ruleset `notification_parameters` ab und speichert sie in `notification_rules.yml`.

### 6. Änderungen aktivieren
Nach der Ausführung des Playbooks müssen die Änderungen in Checkmk aktiviert werden, da das Hinzufügen von Regeln die Konfiguration verändert:
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
   - **Setup > General > Rule-based notifications**, um die Benachrichtigungsregel zu überprüfen.
   - **Setup > Hosts > Host tags**, um die Host-Tag-Regel zu überprüfen.
   - **Setup > Services > Service monitoring rules**, um die Service-Parameter-Regel zu überprüfen.
2. Überprüfe die Regeln:
   - Wähle das entsprechende Ruleset aus und prüfe, ob die Regel mit der Beschreibung (z. B. `Email notifications for web servers`) und den Bedingungen/Werten korrekt erstellt wurde.
3. Überprüfe die gespeicherten Regeln:
   - Öffne die Datei `notification_rules.yml`, um die abgefragten Regeln zu sehen.
4. Alternativ, prüfe die Regeln über die Checkmk-API:
   ```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/rule/collections/all?ruleset_name=notification_parameters" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```

### 8. Fehlerbehandlung
- **CSV-Datei nicht gefunden**: Stelle sicher, dass `rules.csv` existiert und der Pfad in `csv_file` korrekt ist.
- **Ungültiges CSV-Format**: Überprüfe, ob die CSV-Datei die erforderlichen Spalten (`ruleset`, `folder`, `conditions`, `value`, `description`) enthält und korrekt formatiert ist. JSON-Daten in `conditions` und `value` müssen gültig sein.
- **Regel existiert bereits**: Wenn eine Regel mit denselben Eigenschaften bereits existiert, ignoriert das Modul die Erstellung (idempotentes Verhalten). Setze `state: absent`, um bestehende Regeln zu löschen.
- **Ungültiges Ruleset**: Stelle sicher, dass das `ruleset` in der CSV-Datei ein gültiges Checkmk-Ruleset ist (z. B. `notification_parameters`). Konsultiere die [Checkmk-Dokumentation](https://docs.checkmk.com/latest/en/rest_api.html) für gültige Rulesets.
- **Ungültige Zugangsdaten**: Stelle sicher, dass `automation_user` und `automation_secret` korrekt sind.
- **Netzwerkprobleme**: Überprüfe die Erreichbarkeit des Checkmk-Servers (`server_url`) und die korrekte Portfreigabe (HTTP/HTTPS).
- **TLS-Zertifikate**: Bei HTTPS, stelle sicher, dass das Zertifikat gültig ist, oder setze `validate_certs: false` im Playbook (nur für Testumgebungen).
- **Checkmk-Version**: Stelle sicher, dass die Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).

### 9. Anpassungen und Erweiterungen
- **Erweiterte CSV-Attribute**: Füge weitere Spalten zur CSV-Datei hinzu (z. B. `properties` für Regel-Eigenschaften wie `disabled`), wenn zukünftige Checkmk-Versionen diese unterstützen.
- **Komplexe Bedingungen**: Erweitere die `conditions`-Spalte, um komplexere Bedingungen wie mehrere Host- oder Service-Muster zu definieren.
- **Regel-Löschung**: Setze `state: absent` in der Regel-Aufgabe, um bestehende Regeln zu entfernen.
- **Andere Rulesets**: Passe die CSV-Datei an, um Regeln für andere Rulesets (z. B. `active_checks:http`, `inventory_df_rules`) zu erstellen.
- **Automatisierung**: Plane das Playbook mit einem Scheduler (z. B. Ansible Tower/AWX oder Cron), um Regeln regelmäßig zu aktualisieren.
- **Regel-Backup**: Erweitere die letzte Aufgabe, um Regeln für andere Rulesets abzufragen und zu speichern.

## Hinweise
- **Sicherheit**: Verwende immer eine Vault-Datei für das `automation_secret`, um sensible Daten zu schützen.
- **Checkmk-Version**: Stelle sicher, dass die `checkmk.general` Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).
- **Dokumentation**: Weitere Details zu Modulen und Lookup-Plugins findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **Testumgebung**: Teste das Playbook in einer nicht-produktiven Umgebung, um unerwartete Auswirkungen zu vermeiden.
- **CSV-Format**: Stelle sicher, dass die CSV-Datei korrekt formatiert ist (z. B. keine fehlenden Spalten oder ungültigen JSON-Daten in `conditions` oder `value`).
- **Änderungsaktivierung**: Nach dem Hinzufügen von Regeln müssen Änderungen in Checkmk aktiviert werden, entweder manuell oder über die API.

## Fazit
Das angepasste Playbook `create_rules_from_csv.yml` ermöglicht es, Regeln in Checkmk basierend auf einer CSV-Datei zu erstellen und bestehende Regeln dynamisch abzufragen. Mit der `checkmk.general` Collection und dem `community.general.read_csv` Modul kannst du die Regelverwaltung flexibel und skalierbar automatisieren, was besonders nützlich für die Konfiguration von Benachrichtigungen, Tags und Service-Parametern in großen Umgebungen ist. Durch Anpassung der CSV-Datei kannst du das Playbook an deine spezifischen Anforderungen anpassen.
