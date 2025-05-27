# Ansible-Collection für Checkmk: HowTo für deutschsprachige Nutzer

Willkommen in diesem Repository! Hier biete ich deutschsprachigen Nutzern ein umfassendes HowTo zur Verwendung der `checkmk.general` Ansible Collection für Checkmk. Ziel ist es, die Automatisierung von Checkmk-Aufgaben wie das Verwalten von Hosts, Services, Regeln, Ausfallzeiten und mehr zu vereinfachen.

## Über dieses Repository
In diesem Repository ([bh2005/ansible-things/ansible-collection](https://github.com/bh2005/ansible-things/tree/main/ansible-collection)) findest du Anleitungen, Beispiele und Tipps, wie du die Checkmk Ansible Collection effektiv einsetzen kannst. Die Inhalte sind speziell für deutschsprachige Nutzer aufbereitet, um die Einstiegshürden zu minimieren.

## Die Checkmk Ansible Collection
Die `checkmk.general` Collection wird von Checkmk entwickelt und gepflegt. Sie ermöglicht die Automatisierung von Monitoring-Aufgaben in Checkmk über Ansible, einschließlich:
- Erstellen und Verwalten von Ordnern, Hosts, Regeln und Benutzern.
- Planen von Ausfallzeiten (Downtimes).
- Verwalten von Agenten und Hostgruppen.
- Dynamische Inventarisierung basierend auf Checkmk-Daten.

Das offizielle Repository der Collection findest du hier:  
[https://github.com/Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general)

## Demo-Playbooks
Die offizielle Collection enthält eine Reihe von Demo-Playbooks, die verschiedene Anwendungsfälle demonstrieren. Diese findest du im Verzeichnis:  
[https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo](https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo)

Beispiele umfassen:
- **downtimes.yml**: Planen von Ausfallzeiten für Hosts und Services.
- Andere Playbooks für die Verwaltung von Hosts, Agenten und Regeln.

Diese Demo-Playbooks dienen als Ausgangspunkt, um die Funktionalitäten der Collection zu verstehen und eigene Playbooks zu erstellen.

## Wie du beginnst
1. **Collection installieren**:
   ```bash
   ansible-galaxy collection install checkmk.general
   ```
2. **Voraussetzungen**:
   - Ansible (kompatible Version).
   - Zugang zu einem Checkmk-Server mit aktivierter Web-API.
   - API-Zugangsdaten (`automation_user` und `automation_secret`).
   - Optional: Ansible Vault für sichere Speicherung von Zugangsdaten.
3. **Beispiele nutzen**:
   - Klone das Repository der Collection oder dieses Repository, um die Demo-Playbooks zu testen.
   - Passe die Variablen (z. B. `server_url`, `site`, `automation_user`) an deine Umgebung an.
4. **Dokumentation lesen**:
   - Die offizielle Dokumentation der Collection findest du im [GitHub-Repository](https://github.com/Checkmk/ansible-collection-checkmk.general).
   - Weitere Details zu Checkmk und seiner API sind in der [Checkmk-Dokumentation](https://docs.checkmk.com) verfügbar.

## Beiträge
Dieses Repository soll wachsen! Wenn du eigene Anleitungen, Playbooks oder Tipps für deutschsprachige Nutzer beitragen möchtest, erstelle gerne einen Pull Request oder kontaktiere mich über [bh2005/ansible-things](https://github.com/bh2005/ansible-things).

## Lizenz
Die Inhalte dieses Repositories unterliegen der gleichen Lizenz wie die `checkmk.general` Collection (siehe [LICENSE](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/LICENSE) im offiziellen Repository).

Viel Spaß beim Automatisieren mit Checkmk und Ansible!
