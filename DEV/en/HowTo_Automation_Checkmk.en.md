# How to automate monitoring configurations with the Checkmk Ansible Collection

> This document was translated by machine and may contain errors. Please read with caution!


This Howto describes five concrete examples of how the `checkmk.general` ansible collection can be used to automate monitoring configurations in CheckMK. The examples include creating folders, rules, users, host groups and the use of the Lookup plugin for folder attributes.

## Prerequisites
- **Ansible**: Installed and configured (compatible with the collection).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to an ongoing CheckMK server with API access.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the CheckMK automation API.
- **Vault (recommended)**: For the safe storage of the `automation_secret`.
- **Folder/hosts**: Some examples require that certain folders or hosts exist.

## Example 1: Creating a folder
This example shows how to create a folder in CheckMK to organize hosts.

### Playbook
Create a Yaml file (e.g.`create_folder.yml`):

```yaml
- name: Erstelle einen Ordner für Produktionsserver
  hosts: localhost
  tasks:
    - name: Ordner erstellen
      checkmk.general.checkmk_folder:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        path: "/production_servers" 
        attributes:
          criticality: "prod" 
          network_segment: "dmz" 
        state: present
```

### Carry out
```bash
ansible-playbook create_folder.yml --vault-id vault.yml
```

### Result
A folder `/production_servers` will be with the attributes `criticality: prod` and `network_segment: dmz` created.

## Example 2: Creating a monitoring rule
This example defines a rule for the memory monitoring of Linux servers.

### Playbook
Create a Yaml file (e.g.`create_rule.yml`):

```yaml
- name: Setze Speicherüberwachungsregel für Linux-Server
  hosts: localhost
  tasks:
    - name: Regel erstellen
      checkmk.general.checkmk_rule:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        ruleset: "memory" 
        folder: "/linux_servers" 
        conditions:
          host_tags:
            os: linux
        properties:
          levels:
            warning: 80
            critical: 90
        state: present
```

### Carry out
```bash
ansible-playbook create_rule.yml --vault-id vault.yml
```

### Result
A rule is created, the warnings in 80 % and critical alarms with a 90 % memory utilization for Linux servers in the folder `/linux_servers` triggered.

## Example 3: User management with role assignment
This example creates a new user with administrator rights.

### Playbook
Create a Yaml file (e.g.`create_user.yml`):

```yaml
- name: Erstelle einen neuen Benutzer mit Admin-Rechten
  hosts: localhost
  tasks:
    - name: Benutzer erstellen
      checkmk.general.checkmk_user:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        username: "jdoe" 
        fullname: "John Doe" 
        password: "{{ vault_user_password }}" 
        roles:
          - admin
        contactgroups:
          - "all_admins" 
        state: present
```

### Carry out
```bash
ansible-playbook create_user.yml --vault-id vault.yml
```

### Result
A user `jdoe` will be with administrator rights and the contact group `all_admins` created.

## Example 4: Creating a host group
This example shows how to create a host group to group hosts.

### Playbook
Create a Yaml file (e.g.`create_hostgroup.yml`):

```yaml
- name: Erstelle eine Hostgruppe für Webserver
  hosts: localhost
  tasks:
    - name: Hostgruppe erstellen
      checkmk.general.checkmk_hostgroup:
        server_url: "https://monitoring.example.com" 
        site: "mysite" 
        automation_user: "automation" 
        automation_secret: "{{ vault_automation_secret }}" 
        name: "web_servers" 
        title: "Web Servers" 
        state: present
```

### Carry out
```bash
ansible-playbook create_hostgroup.yml --vault-id vault.yml
```

### Result
A host group `web_servers` is created that summarizes hosts with similar properties (e.g. web server).

## Example 5: Queries of folder attributes
This example shows how you ask all attributes of a folder with the Lookup plugin.

### Playbook
Create a Yaml file (e.g.`show_folder_attributes.yml`):

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

### Carry out
```bash
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
```

### Result
The attributes of the folder `/production_servers`(e.g.`criticality`,,`network_segment`) are output in the JSON format.

## Vault for secure access data (optional)
For all examples you can use sensitive data such as `automation_secret` or `vault_user_password` save in an Ansible Vault file:

```bash
ansible-vault create vault.yml
```

Content of the `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
vault_user_password: benutzer_passwort
```

Perform the playbooks with the Vault file:
```bash
ansible-playbook <playbook>.yml --vault-id vault.yml
```

## References
- **Troubleshooting**: Make sure that the CheckMK server can be reached, the access data is correct and the specified folder/hosts exist.
- - **documentation**: Further details about modules and options can be found in the [Github documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or on Ansible Galaxy.
- **TLS**: If your server uses HTTPS, check the certificate test (add `validate_certs: false` in addition, if there is no valid certificate - only for test environments).
- **Checkmk version**: Make sure that the CheckMK version used is compatible with the collection (see `SUPPORT.md`).

## Conclusion
The `checkmk.general` collection offers powerful tools for automation of CheckMK configurations. With these examples you can manage and adapt folders, rules, users, host groups and more efficiently.