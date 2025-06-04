# Wie man alle Attribute eines Ordners in Checkmk mit Ansible anzeigt

Dieses HowTo beschreibt, wie man mit der `checkmk.general` Ansible Collection die Attribute eines Ordners in Checkmk abfragt und anzeigt. Die Anleitung verwendet das Lookup-Plugin `checkmk.general.folder`, um die Details eines Ordners, wie z. B. Kritikalität oder Netzwerksegmente, zu erhalten.

## Voraussetzungen
- **Ansible**: Installiert und konfiguriert (Version kompatibel mit der Collection).
- **checkmk.general Collection**: Installiert via `ansible-galaxy collection install checkmk.general`.
- **Checkmk-Server**: Zugang zu einem laufenden Checkmk-Server mit API-Zugriff.
- **API-Zugangsdaten**: Benutzername (`automation_user`) und Passwort/Secret (`automation_secret`) für die Checkmk Automatisierungs-API.
- **Ordner**: Der abzufragende Ordner (z. B. `/production_servers`) muss in Checkmk existieren.
- **Vault (optional)**: Für die sichere Speicherung des `automation_secret`.

## Schritte

### 1. Ansible Playbook erstellen
Erstelle eine YAML-Datei (z. B. `show_folder_attributes.yml`), um die Attribute eines Ordners abzufragen.

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

**Erklärung der Parameter**:
- `folder_path`: Der Pfad des Ordners in Checkmk (z. B. `/production_servers`).
- `server_url`: Die URL des Checkmk-Servers (z. B. `https://monitoring.example.com`).
- `site`: Der Name der Checkmk-Site (z. B. `mysite`).
- `automation_user`: Der Benutzername für die Automatisierungs-API (z. B. `automation`).
- `automation_secret`: Das Passwort oder API-Token (sicher in einer Ansible Vault-Variablen gespeichert, z. B. `vault_automation_secret`).

### 2. Vault für sichere Zugangsdaten (optional)
Falls du das `automation_secret` sicher speichern möchtest, erstelle eine verschlüsselte Vault-Datei:

```bash
ansible-vault create vault.yml
```

Füge die Zugangsdaten hinzu, z. B.:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

Führe das Playbook mit der Vault-Datei aus:
```bash
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
```

### 3. Playbook ausführen
Führe das Playbook aus, um die Attribute des Ordners anzuzeigen:
```bash
ansible-playbook show_folder_attributes.yml
```

### 4. Ausgabe interpretieren
Das Lookup-Plugin gibt ein JSON-ähnliches Dictionary zurück, das die Attribute des Ordners enthält. Typische Attribute können sein:
- `criticality`: Kritikalitätsstufe des Ordners (z. B. `prod`).
- `network_segment`: Netzwerksegment (z. B. `dmz`).
- Benutzerdefinierte Tags oder andere Metadaten, je nach Checkmk-Konfiguration.

Beispielausgabe:
```json
{
  "title": "production_servers",
  "attributes": {
    "criticality": "prod",
    "network_segment": "dmz"
  }
}
```

### 5. Fehlerbehandlung
- **Ordner existiert nicht**: Das Plugin gibt eine Fehlermeldung zurück, wenn der angegebene Ordner nicht existiert.
- **Ungültige Zugangsdaten**: Überprüfe `automation_user` und `automation_secret`.
- **Netzwerkprobleme**: Stelle sicher, dass die `server_url` korrekt ist und der Server erreichbar ist.

## Alternative: Direkte API-Abfrage
Falls du die API direkt nutzen möchtest (ohne Ansible), kannst du die Checkmk Web API verwenden:
```bash
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/objects/folder_config/production_servers" \
  -H "Authorization: Bearer automation dein_geheimes_passwort" \
  -H "Accept: application/json"
```

Dies gibt die Ordnerdetails direkt im JSON-Format zurück.

## Hinweise
- Die verfügbaren Attribute hängen von der Checkmk-Version und den gesetzten Konfigurationen ab. Überprüfe die Checkmk-Dokumentation für Details.
- Für weitere Informationen zum Lookup-Plugin siehe die Dokumentation der `checkmk.general` Collection auf [GitHub](https://github.com/Checkmk/ansible-collection-checkmk.general) oder Ansible Galaxy.
- Stelle sicher, dass die TLS-Zertifikatsprüfung korrekt konfiguriert ist, falls dein Server HTTPS verwendet.

## Fazit
Mit dem `checkmk.general.folder` Lookup-Plugin kannst du einfach und effizient alle Attribute eines Ordners in Checkmk abrufen. Dies ist besonders nützlich für die Automatisierung von Monitoring-Konfigurationen und die Dokumentation der Ordnerstruktur.
