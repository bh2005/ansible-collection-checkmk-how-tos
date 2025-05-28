# Security Policy for `ansible-collection-checkmk-how-tos`

## 🇩🇪 Deutsch

Wir nehmen die Sicherheit unserer Projekte ernst. Obwohl dieses Repository hauptsächlich Anleitungen und Beispiel-Playbooks bereitstellt, ist es uns wichtig, potenzielle Sicherheitsrisiken zu identifizieren und zu beheben, die sich aus den bereitgestellten Inhalten oder deren Anwendung ergeben könnten.

---

### 🔒 Melden einer Sicherheitslücke

Wir bitten Sie dringend, verantwortungsvoll mit der Offenlegung von Sicherheitslücken umzugehen. Sollten Sie eine Sicherheitslücke oder ein potenzielles Sicherheitsproblem in den Anleitungen, Beispiel-Playbooks oder den empfohlenen Praktiken dieses Repositories entdecken, bitten wir Sie, uns dies unverzüglich mitzuteilen.

**Bitte melden Sie Sicherheitslücken nicht über öffentliche GitHub Issues.**

Senden Sie stattdessen eine E-Mail an:

* **noreply@example.com**

**Was Sie in Ihre Meldung aufnehmen sollten:**

* Eine detaillierte Beschreibung der Sicherheitslücke.
* Schritte zur Reproduktion (wenn möglich).
* Den betroffenen Dateipfad oder Abschnitt der Anleitung.
* Jegliche potenzielle Auswirkung der Lücke.
* Ihre Kontaktdaten, falls wir Rückfragen haben.

Wir werden Ihre Meldung prüfen und Sie über den Fortschritt der Behebung informieren.

---

### 🛡️ Sicherheit der Beispiel-Playbooks und Anleitungen

Die in diesem Repository bereitgestellten Ansible Playbooks und Anleitungen dienen als Beispiele und Ausgangspunkte für Ihre eigenen Automatisierungsprozesse.

**Wichtige Hinweise:**

* **Sensible Daten**: Die Beispiele zeigen, wie `vault` für sensible Daten verwendet werden kann. **Verwenden Sie niemals Klartext-Passwörter oder API-Secrets in Ihren Playbooks in einer Produktionsumgebung.** Nutzen Sie immer Ansible Vault oder andere sichere Mechanismen.
* **Berechtigungen**: Führen Sie Ansible Playbooks immer mit den minimal erforderlichen Berechtigungen aus. Die für die Checkmk API verwendeten Benutzer sollten nur die notwendigen Rechte haben, um die spezifischen Aufgaben auszuführen.
* **Checkmk API Sicherheit**: Stellen Sie sicher, dass Ihr Checkmk-Server und die API-Zugriffspunkte ordnungsgemäß gesichert sind (z.B. durch Firewall-Regeln, TLS/SSL, starke Passwörter).
* **Updates**: Halten Sie Ihre Ansible-Installation, die `checkmk.general` Collection und Ihren Checkmk-Server stets auf dem neuesten Stand, um von den neuesten Sicherheitsverbesserungen zu profitieren.
* **Überprüfung der Beispiele**: Auch wenn wir uns bemühen, sichere Praktiken zu demonstrieren, ist es Ihre Verantwortung, alle Beispiel-Playbooks und Anleitungen vor der Implementierung in Ihrer eigenen Umgebung gründlich zu prüfen und an Ihre spezifischen Sicherheitsanforderungen anzupassen.

---

Vielen Dank für Ihre Mithilfe, dieses Repository sicher und nützlich zu halten.

---

## 🇬🇧 English

We take the security of our projects seriously. Although this repository primarily provides guides and example playbooks, it is important for us to identify and address potential security risks that may arise from the provided content or its application.

---

### 🔒 Reporting a Vulnerability

We strongly encourage responsible disclosure of security vulnerabilities. If you discover a security vulnerability or a potential security issue in the guides, example playbooks, or recommended practices within this repository, please notify us immediately.

**Please do not report security vulnerabilities via public GitHub Issues.**

Instead, send an email to:

* **noreply@example.com**

**What to include in your report:**

* A detailed description of the vulnerability.
* Steps to reproduce (if possible).
* The affected file path or section of the guide.
* Any potential impact of the vulnerability.
* Your contact information, in case we have follow-up questions.

We will review your report and keep you informed of the remediation progress.

---

### 🛡️ Security of Example Playbooks and Guides

The Ansible playbooks and guides provided in this repository serve as examples and starting points for your own automation processes.

**Important Considerations:**

* **Sensitive Data**: The examples demonstrate how to use `vault` for sensitive data. **Never use plain-text passwords or API secrets directly in your playbooks in a production environment.** Always utilize Ansible Vault or other secure mechanisms.
* **Permissions**: Always run Ansible playbooks with the minimum necessary permissions. The users used for the Checkmk API should only have the rights required to perform specific tasks.
* **Checkmk API Security**: Ensure your Checkmk server and API access points are properly secured (e.g., with firewall rules, TLS/SSL, strong passwords).
* **Updates**: Keep your Ansible installation, the `checkmk.general` collection, and your Checkmk server up
