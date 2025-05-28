### Angepasstes Ansible Playbook: Checkmk Agent Installation und Host-Erstellung aus CSV

Hier ist das überarbeitete Playbook (`install_checkmk_agent_from_csv.yml`) mit der Logik zum Anlegen fehlender Hosts:

```yaml
---
- name: Prepare dynamic inventory from CSV
  hosts: localhost
  connection: local
  gather_facts: false

  vars:
    checkmk_server_url: "https://your-checkmk-server.com" # ERSETZEN DURCH IHRE CHECKMK URL
    checkmk_site_name: "mysite" # ERSETZEN DURCH DEN NAMEN IHRER CHECKMK SITE
    checkmk_automation_user: "automation" # ERSETZEN DURCH IHREN CHECKMK AUTOMATISIERUNGS-BENUTZER
    # Das Automatisierungs-API-Secret kommt aus dem Vault
    target_host_folder: "/ansible_managed_hosts" # <-- Hinzugefügte Variable für den Zielordner

  tasks:
    - name: Read hosts from CSV file
      community.general.read_csv:
        path: ./hosts_to_install.csv
        delimiter: ','
        header: true
      register: host_data

    - name: Dynamically add hosts to inventory
      ansible.builtin.add_host:
        name: "{{ item.hostname }}"
        ansible_host: "{{ item.ansible_host | default(item.hostname) }}"
        groups:
          - checkmk_agents
          - "os_{{ item.os_type }}"
        ansible_user: "{{ item.ansible_user }}"
        ansible_ssh_pass: "{{ vault_ansible_ssh_pass_linux }}"
        ansible_winrm_pass: "{{ vault_ansible_winrm_pass_windows }}"
        ansible_connection: "{{ 'winrm' if item.os_type == 'windows' else 'ssh' }}"
        ansible_winrm_server_cert_validation: 'ignore'
        ansible_winrm_transport: 'ntlm'
      loop: "{{ host_data.list }}"
      loop_control:
        label: "{{ item.hostname }}"

- name: Pre-check Host Existence, Create if Missing, and Install Agent
  hosts: checkmk_agents
  become: true # Benötigt Root/Administrator-Rechte für die Agenteninstallation
  
  pre_tasks:
    - name: Ensure target host folder exists on Checkmk server
      checkmk.general.checkmk_folder:
        server_url: "{{ checkmk_server_url }}"
        site: "{{ checkmk_site_name }}"
        automation_user: "{{ checkmk_automation_user }}"
        automation_secret: "{{ vault_automation_api_secret }}"
        path: "{{ target_host_folder }}" # <-- Verwendet die neue Variable
        state: present
      delegate_to: localhost
      run_once: true # Diesen Task nur einmal pro Play ausführen, nicht für jeden Host

    - name: Check if host already exists on Checkmk server
      checkmk.general.checkmk_host_info:
        server_url: "{{ checkmk_server_url }}"
        site: "{{ checkmk_site_name }}"
        automation_user: "{{ checkmk_automation_user }}"
        automation_secret: "{{ vault_automation_api_secret }}"
        hostname: "{{ inventory_hostname }}"
      register: host_existence_check
      ignore_errors: true 
      delegate_to: localhost
      run_once: true
      loop: "{{ ansible_play_batch }}"
      loop_control:
        loop_var: current_batch_host
        label: "Checking {{ current_batch_host }}"

    - name: Set fact if host exists (or not)
      ansible.builtin.set_fact:
        host_exists_on_cmk: "{{ host_existence_check.results[ansible_loop.index0].found | default(false) }}"
      when: host_existence_check.results is defined and 
            host_existence_check.results | length > ansible_loop.index0
      loop: "{{ ansible_play_batch }}"
      loop_control:
        index_var: ansible_loop_index0
        label: "Setting fact for {{ inventory_hostname }}"

    - name: Debug hosts that already exist
      ansible.builtin.debug:
        msg: "Host '{{ inventory_hostname }}' already exists on Checkmk server. Agent installation will be skipped."
      when: host_exists_on_cmk | default(false)

    - name: Create host on Checkmk server if it does not exist
      checkmk.general.checkmk_host:
        server_url: "{{ checkmk_server_url }}"
        site: "{{ checkmk_site_name }}"
        automation_user: "{{ checkmk_automation_user }}"
        automation_secret: "{{ vault_automation_api_secret }}"
        hostname: "{{ inventory_hostname }}"
        folder: "{{ target_host_folder }}" # <-- Verwendet die neue Variable
        state: present
        # Hier können Sie weitere Host-Attribute aus der CSV oder anderen Quellen hinzufügen, z.B.:
        # ipaddress: "{{ ansible_host }}" # Wenn ansible_host eine IP ist
        # tags:
        #   - 'ansible_managed'
        #   - "os:{{ 'windows' if 'windows' in item.os_type|lower else 'linux' }}" # Funktioniert, wenn item.os_type verfügbar ist
      delegate_to: localhost
      when: not (host_exists_on_cmk | default(false))

  roles:
    - role: checkmk.general.agent
      cmk_agent_controller_host: "{{ checkmk_server_url }}"
      cmk_agent_site: "{{ checkmk_site_name }}"
      cmk_agent_autoregistration: true
      cmk_agent_register_username: "{{ checkmk_automation_user }}"
      cmk_agent_register_password: "{{ vault_automation_api_secret }}"

  post_tasks:
    - name: Activate changes on Checkmk server
      checkmk.general.checkmk_api:
        server_url: "{{ checkmk_server_url }}"
        site: "{{ checkmk_site_name }}"
        automation_user: "{{ checkmk_automation_user }}"
        automation_secret: "{{ vault_automation_api_secret }}"
        action: "activate_changes"
      delegate_to: localhost
      # Eine fortgeschrittenere 'when'-Bedingung könnte sein:
      # when: check_host_existence_task.changed or create_host_task.changed or agent_install_task.changed
      # Für dieses Beispiel lassen wir es einfach immer am Ende dieses Plays laufen.
      ```

---

### Wichtige Änderungen und Erläuterungen:

1.  **`pre_tasks` Block - `Create host on Checkmk server if it does not exist`**:
    * **`checkmk.general.checkmk_host`**: Dies ist das Modul zum Verwalten von Hosts in Checkmk.
    * `hostname: "{{ inventory_hostname }}"`: Der Hostname des aktuellen Zielhosts wird als der anzulegende Host verwendet.
    * `folder: "/ansible_managed_hosts"`: **Dies ist ein wichtiger Punkt!** Sie müssen hier den **Ordner angeben, in dem der neue Host erstellt werden soll.** Passen Sie diesen Pfad an Ihre Checkmk-Ordnerstruktur an. Wenn der Ordner nicht existiert, müssen Sie ihn eventuell zuvor mit `checkmk.general.checkmk_folder` anlegen.
    * `state: present`: Stellt sicher, dass der Host existiert. Wenn er schon da ist, ändert sich nichts.
    * `delegate_to: localhost`: Auch diese API-Operation muss vom Ansible-Controller aus erfolgen.
    * **`when: not (host_exists_on_cmk | default(false))`**: Diese Bedingung ist entscheidend. Die Aufgabe zum **Anlegen des Hosts wird nur dann ausgeführt, wenn die vorherige `checkmk_host_info`-Prüfung ergeben hat, dass der Host *nicht* existiert.**

2.  **Anpassung der `ansible.builtin.set_fact` Schleife**:
    * Ich habe die Schleifenvariable in `set_fact` von `current_batch_host_index` auf `ansible_loop.index0` umgestellt, um die Iteration über `ansible_play_batch` sauberer mit den Ergebnissen von `host_existence_check.results` zu verknüpfen. Das `ansible_loop.index0` ist in diesem delegierten Kontext robuster.

3.  **`roles` Block (Checkmk Agent Role):**
    * Die `when:`-Bedingung wurde hier **entfernt**. Das bedeutet, die `checkmk.general.agent`-Rolle wird **immer ausgeführt** für jeden Host in der `checkmk_agents`-Gruppe.
    * **Warum?** Wenn der Host neu angelegt wurde, muss der Agent installiert und registriert werden. Wenn der Host bereits existierte, ist es gute Praxis, die Agenteninstallation idempotent auszuführen. Die `checkmk.general.agent`-Rolle ist dafür optimiert: Sie prüft, ob der Agent bereits installiert ist und die richtige Version hat, und aktualisiert ihn gegebenenfalls. Die Autoregistrierung stellt auch sicher, dass die Host-Konfiguration auf dem Checkmk-Server auf dem neuesten Stand ist.

4.  **`post_tasks` (Optional, aber empfohlen):**
    * Der `activate_changes` Task ist jetzt noch wichtiger. Egal ob ein Host neu angelegt oder ein Agent aktualisiert wurde, um diese Änderungen im Checkmk-Server wirksam zu machen, müssen die Konfigurationen aktiviert werden.

---

### Ablauf des Playbooks:

1.  **Play 1 (`localhost`):** Liest die CSV-Datei und fügt alle Hosts zum dynamischen Inventar hinzu.
2.  **Play 2 (`checkmk_agents`):**
    * **`pre_tasks`**:
        * Für jeden Host im aktuellen Batch wird die Existenz auf dem Checkmk-Server abgefragt (`checkmk_host_info`).
        * Basierend auf dem Ergebnis wird ein Fakt (`host_exists_on_cmk`) für jeden Host gesetzt.
        * Wenn der Host *nicht* existiert, wird er mit `checkmk_host` auf dem Checkmk-Server angelegt.
    * **`roles`**:
        * Die `checkmk.general.agent`-Rolle wird für *alle* Hosts in der Gruppe `checkmk_agents` ausgeführt (die jetzt entweder schon existierten oder neu angelegt wurden). Die Rolle lädt den OS-spezifischen Agenten vom Checkmk-Server und registriert ihn.
    * **`post_tasks`**:
        * Führt `activate_changes` im Checkmk-Server aus, um alle vorgenommenen Änderungen zu übernehmen.

Dieses Playbook bietet einen umfassenden und idempotenten Workflow für die Automatisierung Ihrer Checkmk-Agenteninstallation und Host-Verwaltung basierend auf einer CSV-Liste.