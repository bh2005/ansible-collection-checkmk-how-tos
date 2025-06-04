# Wie man Downtimes in Checkmk mit der Ansible Collection setzt

Dieses HowTo beschreibt, wie man das Playbook `downtimes.yml` aus dem Repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/downtimes.yml) verwendet, um Ausfallzeiten (Downtimes) für Hosts und Services in Checkmk zu planen. Das Playbook nutzt die `checkmk.general` Ansible Collection, um Ausfallzeiten für einzelne oder mehrere Hosts sowie spezifische Services zu setzen.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (kompatibel mit der Collection).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Server**: Zugang zu einer Checkmk-Instanz mit aktivierter Web-API.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Automatisierungs-API.
- **Vault (empfohlen)**: Für die sichere Speicherung des `automation_secret`.
- **Netzwerkzugriff**: Der Ansible-Controller muss den Checkmk-Server über HTTP/HTTPS erreichen können.
- **Hosts/Services**: Die im Playbook angegebenen Hosts (z. B. `example.com`) und Services (z. B. `Filesystem /`, `Ping`) müssen in der Checkmk-Instanz existieren.

## Schritte

### 1. Playbook herunterladen
Klone das Repository oder kopiere das Playbook `downtimes.yml` auf deinen Ansible-Controller:

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
    comment: "Ansible Downtime"
    duration: 60
  tasks:
    - name: Set a downtime for a single host
      checkmk.general.downtime:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        hostname: "example.com"
        comment: "{{ comment }}"
        duration: "{{ duration }}"
        state: present
    - name: Set a downtime for multiple hosts
      checkmk.general.downtime:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        hostname: "{{ item }}"
        comment: "{{ comment }}"
        duration: "{{ duration }}"
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}"
    - name: Set a downtime for a service
      checkmk.general.downtime:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        hostname: "example.com"
        service: "Filesystem /"
        comment: "{{ comment }}"
        duration: "{{ duration }}"
        state: present
    - name: Set a downtime for a service on multiple hosts
      checkmk.general.downtime:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        hostname: "{{ item }}"
        service: "Ping"
        comment: "{{ comment }}"
        duration: "{{ duration }}"
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}"
```

### 2. Variablen anpassen
Passe die Variablen im Playbook an deine Umgebung an:
- **server_url**: Ersetze `http://localhost` durch die URL deines Checkmk-Servers (z. B. `https://monitoring.example.com`).
- **site**: Ersetze `mysite` durch den Namen deiner Checkmk-Site.
- **automation_user**: Verwende den Benutzernamen für die Automatisierungs-API (z. B. `automation`).
- **automation_secret**: Ersetze `mysecret` durch das API-Passwort oder -Token.
- **hostname**: Stelle sicher, dass der Host (z. B. `example.com`) in deiner Checkmk-Instanz existiert.
- **service**: Überprüfe, dass die Services (z. B. `Filesystem /`, `Ping`) in Checkmk definiert sind.
- **query**: Passe die Abfrage im Lookup-Plugin an, um die gewünschten Hosts zu filtern (z. B. `{"host_tags": {"os": "linux"}}` für Linux-Hosts).

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
Führe das Playbook aus, um die Ausfallzeiten zu setzen:

```bash
ansible-playbook downtimes.yml --vault-id vault.yml
```

### 4. Aufgaben des Playbooks
Das Playbook führt vier Aufgaben aus:
1. **Downtime für einen einzelnen Host**:
   - Setzt eine 60-minütige Ausfallzeit für den Host `example.com` mit dem Kommentar `Ansible Downtime`.
2. **Downtime für mehrere Hosts**:
   - Ruft alle Hosts mit dem Tag `os: linux` über das Lookup-Plugin `checkmk.general.host` ab und setzt für jeden eine 60-minütige Ausfallzeit.
3. **Downtime für einen Service**:
   - Setzt eine 60-minütige Ausfallzeit für den Service `Filesystem /` auf dem Host `example.com`.
4. **Downtime für einen Service auf mehreren Hosts**:
   - Setzt eine 60-minütige Ausfallzeit für den Service `Ping` auf allen Hosts mit dem Tag `os: linux`.

### 5. Überprüfen der Ausfallzeiten
Nach der Ausführung des Playbooks:
1. Melde dich in der Checkmk-Weboberfläche an und navigiere zu **Monitor > All hosts** oder **Monitor > All services**.
2. Überprüfe die Ausfallzeiten unter **Downtimes** (z. B. im Host- oder Service-Menü).
3. Alternativ, prüfe die Ausfallzeiten über die Checkmk-API:
   ```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/downtime/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json"
   ```

### 6. Fehlerbehandlung
- **Host/Service nicht gefunden**: Wenn der Host (z. B. `example.com`) oder der Service (z. B. `Filesystem /`) nicht existiert, schlägt die Aufgabe fehl. Überprüfe die Schreibweise und Existenz in Checkmk.
- **Ungültige Zugangsdaten**: Stelle sicher, dass `automation_user` und `automation_secret` korrekt sind.
- **Netzwerkprobleme**: Überprüfe die Erreichbarkeit des Checkmk-Servers (`server_url`) und die korrekte Portfreigabe (HTTP/HTTPS).
- **TLS-Zertifikate**: Bei HTTPS, stelle sicher, dass das Zertifikat gültig ist, oder setze `validate_certs: false` im Playbook (nur für Testumgebungen).
- **Lookup-Plugin-Fehler**: Wenn die Abfrage im Lookup-Plugin keine Hosts zurückgibt, überprüfe das `query`-Attribut (z. B. `{"host_tags": {"os": "linux"}}`).

### 7. Anpassungen und Erweiterungen
- **Dynamische Host-Listen**: Passe die Abfrage im Lookup-Plugin an, um andere Kriterien zu verwenden (z. B. `{"host_labels": {"env": "prod"}}`).
- **Andere Downtime-Parameter**: Füge weitere Parameter hinzu, wie `start_time` oder `end_time`, um die Ausfallzeiten genauer zu definieren (siehe [Checkmk-Dokumentation](https://docs.checkmk.com/latest/en/rest_api.html)).
- **Entfernen von Downtimes**: Setze `state: absent` in den Aufgaben, um bestehende Ausfallzeiten zu entfernen.
- **Automatisierung**: Plane das Playbook mit einem Scheduler (z. B. Ansible Tower/AWX oder Cron), um regelmäßige Ausfallzeiten zu setzen.

## Hinweise
- **Sicherheit**: Verwende immer eine Vault-Datei für das `automation_secret`, um sensible Daten zu schützen.
- **Checkmk-Version**: Stelle sicher, dass die `checkmk.general` Collection mit deiner Checkmk-Version kompatibel ist (siehe `SUPPORT.md` im Repository).
- **Dokumentation**: Weitere Details zu Modulen und Lookup-Plugins findest du in der [GitHub-Dokumentation](https://github.com/Checkmk/ansible-collection-checkmk.general) oder auf Ansible Galaxy.
- **Testumgebung**: Teste das Playbook in einer nicht-produktiven Umgebung, um unerwartete Auswirkungen zu vermeiden.
- **Beispielwerte**: Das Playbook verwendet Platzhalter (`example.com`, `http://localhost`). Passe diese an deine tatsächliche Umgebung an.

## Fazit
Das Playbook `downtimes.yml` bietet eine flexible Möglichkeit, Ausfallzeiten in Checkmk für Hosts und Services zu setzen, sowohl für einzelne als auch für mehrere Objekte. Mit der `checkmk.general` Collection kannst du Wartungsfenster effizient automatisieren, was besonders nützlich für geplante Ausfälle oder regelmäßige Wartungsarbeiten ist. Durch Anpassung der Variablen und Abfragen kannst du das Playbook an deine spezifischen Anforderungen anpassen.
