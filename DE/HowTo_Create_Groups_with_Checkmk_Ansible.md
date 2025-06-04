# Wie man Host- und Servicegruppen in Checkmk mit der Ansible Collection erstellt

Dieses HowTo beschreibt, wie man das Playbook `groups.yml` aus dem Repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/groups.yml) verwendet, um Host- und Servicegruppen in Checkmk zu erstellen und Hosts dynamisch einer Hostgruppe zuzuweisen. Das Playbook nutzt die `checkmk.general` Ansible Collection, um eine Hostgruppe (`my_hostgroup`) und eine Servicegruppe (`my_servicegroup`) zu erstellen sowie Hosts basierend auf Tags (z. B. `os: linux`) einer Hostgruppe zuzuweisen.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit der Collection).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Server**: Zugang zu einer Checkmk-Instanz mit aktivierter Web-API.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Automatisierungs-API.
- **Vault (empfohlen)**: Für die sichere Speicherung des `automation_secret`.
- **Netzwerkzugriff**: Der Ansible-Controller muss den Checkmk-Server über HTTP/HTTPS erreichen können.
- **Hosts**: Die im Playbook angesprochenen Hosts (z. B. mit dem Tag `os: linux`) müssen in der Checkmk-Instanz existieren.

## Schritte

### 1. Playbook herunterladen
Klone das Repository oder kopiere das Playbook `groups.yml` auf deinen Ansible-Controller:

```bash
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
cd ansible-collection-checkmk.general/playbooks/demo
```

Das Playbook sieht wie folgt aus (Auszug zur Übersicht):
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "http://localhost"
    site: "mysite"
    automation_user: "automation"
    automation_secret: "mysecret"
  tasks:
    - name: Create a host group
      checkmk.general.checkmk_hostgroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "my_hostgroup"
        title: "My Hostgroup"
        state: present
    - name: Create a service group
      checkmk.general.checkmk_servicegroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "my_servicegroup"
        title: "My Servicegroup"
        state: present
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
              - "my_hostgroup"
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}"
```

### 2. Variablen anpassen
Passe die Variablen im Playbook an deine Umgebung an:
- **server_url**: Ersetze `http://localhost` durch die URL deines Checkmk-Servers (z. B. `https://monitoring.example.com`).
- **site**: Ersetze `mysite` durch den Namen deiner Checkmk-Site.
- **automation_user**: Verwende den Benutzernamen für die Automatisierungs-API (z. B. `automation`).
- **automation_secret**: Ersetze `mysecret` durch das API-Passwort oder -Token.
- **name/title**: Passe die Namen (`my_hostgroup`, `my_servicegroup`) und Titel (`My Hostgroup`, `My Servicegroup`) an deine gewünschten Gruppennamen an.
- **query**: Passe die Abfrage im Lookup-Plugin an, um die gewünschten Hosts zu filtern (z. B. `{"host_tags": {"os": "linux"}}` für Linux-Hosts oder `{"host_labels": {"env": "prod"}}` für Produktionsumgebungen).

**Empfehlung**: Speichere das `automation_secret` in einer Ansible Vault-Datei, um die Sicherheit zu erhöhen.

#### Vault-Datei erstellen
```bash
ansible-vault create vault.yml
```

Inhalt der `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

Bearbeite das Playbook, um die Vault-Variable zu verwenden:
```yaml
automation_secret: "{{ vault_automation_secret }}"
```

### 3. Playbook ausführen
Führe das Playbook aus, um die Host- und Servicegruppen zu erstellen und Hosts zuzuweisen:

```bash
ansible-playbook groups.yml --vault-id vault.yml
```

### 4. Aufgaben des Playbooks
Das Playbook führt drei Aufgaben aus:
1. **Erstellen einer Hostgruppe**:
   - Erstellt eine Hostgruppe mit dem Namen `my_hostgroup` und dem Titel `My Hostgroup`.
2. **Erstellen einer Servicegruppe**:
   - Erstellt eine Servicegruppe mit dem Namen `my_servicegroup` und dem Titel `My Servicegroup`.
3. **Dynamische Zuweisung von Hosts zu einer Hostgruppe**:
   - Ruft alle Hosts mit dem Tag `os: linux` über das Lookup-Plugin `checkmk.general.host` ab.
   - Aktualisiert die Host-Attribute, um die Hosts der Hostgruppe `my_hostgroup` zuzuweisen.

### 5. Änderungen aktivieren
Nach der Ausführung des Playbooks müssen die Änderungen in Checkmk aktiviert werden, da die Zuweisung von Hosts zu einer Hostgruppe die Konfiguration verändert:
1. Melde dich in der Checkmk-Weboberfläche an.
2. Gehe zu **Setup > Activate Changes** und aktiviere die ausstehenden Änderungen.
3. Alternativ, aktiviere die Änderungen über die Checkmk-API:
   ```bash
   curl -X POST "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/activation_run/actions/activate-changes/invoke" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```

### 6. Überprüfen der Ergebnisse
Nach der Ausführung des Playbooks:
1. Melde dich in der Checkmk-Weboberfläche an und navigiere zu:
   - **Setup > Hosts > Host groups**, um die Hostgruppe `my_hostgroup` zu überprüfen.
   - **Setup > Services > Service groups**, um die Servicegruppe `my_servicegroup` zu überprüfen.
2. Überprüfe die Hostzuweisung:
   - Gehe zu **Monitor > All hosts**, wähle einen Host aus der Liste (z. B. mit dem Tag `os: linux`) und prüfe unter **Properties > Host groups**, ob `my_hostgroup` zugewiesen ist.
3. Alternativ, prüfe die Gruppen über die Checkmk-API:
   ```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_group_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```

### 7. Fehlerbehandlung
- **Hostgruppe/Servicegruppe existiert bereits**: Wenn `my_hostgroup` oder `my_servicegroup` bereits existieren, ignoriert das Modul die Erstellung (idempotentes Verhalten). Setze `state: absent`, um bestehende Gruppen zu löschen.
- **Hosts nicht gefunden**: Wenn die Abfrage im Lookup-Plugin keine Hosts zurückgibt (z. B. weil kein Host den Tag `os: linux` hat), überspringt die Aufgabe die Zuweisung. Überprüfe die Abfrage (`query`) und die Host-Tags in Checkmk.
- **Ungültige Zugangsdaten**: Stelle sicher, dass `automation_user` und `automation_secret` korrekt sind.
- **Netzwerkprobleme**: Überprüfe die Erreichbarkeit des Checkmk-Servers (`server_url`) und die korrekte Portfreigabe (HTTP/HTTPS).
- **TLS-Zertifikate**: Bei HTTPS, stelle sicher, dass das Zertifikat gültig ist, oder setze `validate_certs: false` im Playbook (nur für Testumgebungen).
- **Checkmk-Version**: Stelle sicher, dass die Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).

### 8. Anpassungen und Erweiterungen
- **Andere Gruppennamen**: Ändere `name` und `title` für Host- und Servicegruppen, um sie an deine Anforderungen anzupassen (z. B. `web_servers`, `database_services`).
- **Dynamische Abfragen**: Passe die Abfrage im Lookup-Plugin an, um andere Kriterien zu verwenden (z. B. `{"host_labels": {"env": "prod"}}` oder `{"folder": "/production"}`).
- **Servicegruppen-Zuweisung**: Um Services einer Servicegruppe zuzuweisen, kannst du das Modul `checkmk.general.checkmk_service` verwenden (nicht im Demo-Playbook enthalten, aber in der Collection verfügbar).
- **Entfernen von Gruppen**: Setze `state: absent` in den Aufgaben, um bestehende Host- oder Servicegruppen zu löschen.
- **Automatisierung**: Plane das Playbook mit einem Scheduler (z. B. Ansible Tower/AWX oder Cron), um Gruppen regelmäßig zu aktualisieren.

## Hinweise
- **Sicherheit**: Verwende immer eine Vault-Datei für das `automation_secret`, um sensible Daten zu schützen.
- **Checkmk-Version**: Stelle sicher, dass die `checkmk.general` Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).
- **Dokumentation**: Weitere Details zu Modulen und Lookup-Plugins findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **Testumgebung**: Teste das Playbook in einer nicht-produktiven Umgebung, um unerwartete Auswirkungen zu vermeiden.
- **Beispielwerte**: Das Playbook verwendet Platzhalter (`http://localhost`, `my_hostgroup`). Passe diese an deine tatsächliche Umgebung an.
- **Änderungsaktivierung**: Nach der Zuweisung von Hosts zu einer Hostgruppe müssen Änderungen in Checkmk aktiviert werden, entweder manuell oder über die API.

## Fazit
Das Playbook `groups.yml` bietet eine einfache Möglichkeit, Host- und Servicegruppen in Checkmk zu erstellen und Hosts dynamisch einer Hostgruppe zuzuweisen. Mit der `checkmk.general` Collection kannst du die Gruppenverwaltung effizient automatisieren, was besonders nützlich für die Organisation von Monitoring-Objekten in großen Umgebungen ist. Durch Anpassung der Variablen und Abfragen kannst du das Playbook an deine spezifischen Anforderungen anpassen.
