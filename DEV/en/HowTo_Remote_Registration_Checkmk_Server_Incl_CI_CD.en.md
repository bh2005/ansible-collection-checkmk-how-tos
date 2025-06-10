# Howto: Use of the Remote Registration.yml Playbooks for Checkmk

> This document was translated by machine and may contain errors. Please read with caution!


This document describes how to do the Ansible playbook `remote-registration.yml` from the Checkmk Ansible Collection (`checkmk.general`) Use to register a remote checkmk server in a distributed surveillance environment. The PlayBook automates the registration of a remote server with a central CheckMK server. The steps include the preparation, configuration and execution of the playbook.

## Prerequisites
Before using the PlayBook, make sure that the following requirements are met:
- **Ansible**: Ansible (version compatible with the collection, see support.md) must be installed.
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: A central CheckMK server and a remote server have to run. Both must be accessible.
- **Access data**: You need the access data for the `automation_user` and `automation_secret` for both the central and the remote server.
- **Network connectivity**: The servers must be able to communicate with each other via the specified URLs.
- **Python libraries**: The `netaddr`-Bibliothek ist für einige Rollen erforderlich:
```bash
  pip install netaddr
  ```

## Overview of the Playbook
The playbook `remote-registration.yml`(Available at: https://github.com/checkmk/ansible-collection-checkmk.general/blob/playbooks/usecases/remote-registration.yml) performs the following tasks:
1. Register a remote checkmk server with a central CheckMK server.
2. Configures the connection for the distributed surveillance.
3. Activates the changes on the central server.

Here is an example of the Playbook (based on the structure from the repository):

```yaml
- name: Register a remote site
  hosts: localhost
  tasks:
    - name: Register remote site
      checkmk.general.site:
        server_url: "{{ central_server_url }}" 
        site: "{{ central_site }}" 
        automation_user: "{{ central_automation_user }}" 
        automation_secret: "{{ central_automation_secret }}" 
        remote_url: "{{ remote_server_url }}" 
        remote_site: "{{ remote_site }}" 
        remote_automation_user: "{{ remote_automation_user }}" 
        remote_automation_secret: "{{ remote_automation_secret }}" 
        state: present
```

## Step-by-step instructions

### Step 1: Preparation of the inventory
Create an inventory file (`inventory/hosts.ini`) to define the target hosts. Because the playbook on `localhost` a simple configuration is sufficient:

```ini
[localhost]
localhost ansible_connection=local
```

Save this file in a directory like `inventory/hosts.ini`.

### Step 2: Define the variables
Create a variable file (`group_vars/all.yml`) to define the required parameters. An example:

```yaml
central_server_url: "http://central-server.example.com/" 
central_site: "central" 
central_automation_user: "automation" 
central_automation_secret: "your-central-secret" 
remote_server_url: "http://remote-server.example.com/" 
remote_site: "remote" 
remote_automation_user: "automation" 
remote_automation_secret: "your-remote-secret" 
```

Replace the values ​​with the actual URLs and access data of your CheckMK server.

### Step 3: Clone or copy of the Playbook
Clone the repository of the Checkmk Ansible Collection or copy this `remote-registration.yml`-Playbook in Ihr Projektverzeichnis:

```bash
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
```

Alternatively, you can copy the PlayBook directly from the repository: https://github.com/checkmk/ansible-collection-checkmk.general/blob/main/playbooks/usecases/remote-registration.yml

Save the Playbook z. B. as `remote-registration.yml` in your project.

### Step 4: Installation of dependencies
Install the CheckMK Ansible Collection and the required python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 5: executing the playbook
Perform the Playbook with the following command:

```bash
ansible-playbook -i inventory/hosts.ini remote-registration.yml
```

Make sure that the variable file (`group_vars/all.yml`) lies in the same directory or in a path recognized by Ansible.

### Step 6: Check registration
1. Register at the central CheckMK server.
2. Navigate too **Setup> Distributed Monitoring** and check whether the remote server has been registered correctly.
3. Verify that the connection is active and data is synchronized.

## Troubleshooting
- **Network error**: Make sure that `central_server_url` and `remote_server_url` are correct and the servers can be reached.
- **Authentication error**: Check the access data (`automation_user` and `automation_secret`) for both servers.
- **Module error**: Consult the documentation of the `checkmk.general.site`-Module: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/site.py
- **Logs**: Activate detailed logging `-v` or `-vvv` in the Playbook version to identify errors:
```bash
  ansible-playbook -i inventory/hosts.ini remote-registration.yml -vvv
  ```

## Best practices
- **Secure storage of secrets**: Save sensitive data such as `automation_secret` in encrypted variable files (e.g. with `ansible-vault`).
- **Idem**: The Playbook is idempotent, i.e. that is, repeated explanations do not lead to unexpected changes.
- **Versioning**: Check the compatibility of the CheckMK versions and the Ansible Collection in the Support.md: https://github.com/checkmk/ansible-collection-checkmk.general/blob/main/support.md
- **documentation**: Keep your variables and configurations well documented to facilitate later changes.

## Integration in CI/CD
To integrate the PlayBook into a CI/CD pipeline (e.g. with Github Actions), create a workflow file:

```yaml
name: Register Remote Checkmk Site

on:
  push:
    branches:
      - main

jobs:
  register-site:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          pip install ansible netaddr
          ansible-galaxy collection install checkmk.general
      - name: Run Ansible Playbook
        env:
          ANSIBLE_CENTRAL_AUTOMATION_USER: ${{ secrets.CENTRAL_AUTOMATION_USER }}
          ANSIBLE_CENTRAL_AUTOMATION_SECRET: ${{ secrets.CENTRAL_AUTOMATION_SECRET }}
          ANSIBLE_REMOTE_AUTOMATION_USER: ${{ secrets.REMOTE_AUTOMATION_USER }}
          ANSIBLE_REMOTE_AUTOMATION_SECRET: ${{ secrets.REMOTE_AUTOMATION_SECRET }}
        run: |
          ansible-playbook -i inventory/hosts.ini remote-registration.yml
```

Save Secrets in the repository settings of your CI/CD tool.

## Conclusion
The `remote-registration.yml`-Playbook automatisiert die Registrierung eines Remote-Checkmk-Servers in einer verteilten Überwachungsumgebung. Mit den oben beschriebenen Schritten können Sie es lokal oder in einer CI/CD-Pipeline ausführen. Für weitere Details zu den Modulen und Optionen konsultieren Sie die offizielle Dokumentation: https://github.com/Checkmk/ansible-collection-checkmk.general.