# HowTo: Create Hostgroups with Checkmk Ansible

This guide explains how to use the `checkmk.general.hostgroup` module from the Checkmk Ansible Collection to create hostgroups in Checkmk. The process involves defining hostgroups directly in an Ansible playbook and applying them to a Checkmk instance.

## Prerequisites
Before you begin, ensure the following requirements are met:
- **Ansible**: Ansible must be installed (version compatible with the collection, see SUPPORT.md in the Checkmk Ansible Collection repository).
- **Checkmk Ansible Collection**: The `checkmk.general` collection must be installed. Install it with:
  ```bash
  ansible-galaxy collection install checkmk.general
  ```
- **Checkmk Server**: A running Checkmk server with network access.
- **Credentials**: You need the `automation_user` and `automation_secret` for the Checkmk server.
- **Python Libraries**: The `netaddr` library may be required for certain roles:
  ```bash
  pip install netaddr
  ```

## Overview
The `checkmk.general.hostgroup` module allows you to manage hostgroups in Checkmk, including creating, updating, or deleting them. This guide focuses on using this module to create hostgroups by defining them in an Ansible playbook.

## Step-by-Step Instructions

### Step 1: Prepare the Inventory
Create an inventory file (`inventory/hosts.ini`) to define the target host. Since the playbook runs locally, a simple configuration is sufficient:

```ini
[localhost]
localhost ansible_connection=local
```

Save this file in a directory, e.g., `inventory/hosts.ini`.

### Step 2: Define Variables
Create a variables file (`group_vars/all.yml`) to store the required parameters for the Checkmk instance. Example:

```yaml
server_url: "http://checkmk-server.example.com/"
site: "mysite"
automation_user: "automation"
automation_secret: "your-secret"
hostgroups:
  - name: servers
    alias: Production Servers
  - name: databases
    alias: Database Systems
  - name: network
    alias: Network Devices
```

Replace the values with the actual URL, site name, and credentials of your Checkmk server. The `hostgroups` list defines the hostgroups to be created, including their names and optional aliases.

### Step 3: Create the Playbook
Create a playbook to create the hostgroups, e.g., `create_hostgroups.yml`:

```yaml
- name: Create Checkmk Hostgroups
  hosts: localhost
  tasks:
    - name: Create hostgroups
      checkmk.general.hostgroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item.name }}"
        alias: "{{ item.alias | default(omit) }}"
        state: present
      loop: "{{ hostgroups }}"
```

**Explanation**:
- The `checkmk.general.hostgroup` task iterates over the `hostgroups` list defined in the variables file.
- For each hostgroup, it sets the `name` and optional `alias` and uses `state: present` to create or update the hostgroup in Checkmk.
- The `default(omit)` filter ensures that the `alias` parameter is only included if defined, avoiding errors for hostgroups without an alias.

### Step 4: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 5: Run the Playbook
Execute the playbook to create the hostgroups:

```bash
ansible-playbook -i inventory/hosts.ini create_hostgroups.yml
```

Ensure the variables file (`group_vars/all.yml`) is in the same directory or a path recognized by Ansible.

### Step 6: Verify the Results
1. Log in to the Checkmk server.
2. Navigate to **Setup > Hosts > Hostgroups** and confirm that the hostgroups defined in the playbook have been created correctly.
3. Check for any errors in the Checkmk logs or Ansible output.

## Troubleshooting
- **Network Errors**: Ensure the `server_url` is correct and the Checkmk server is reachable.
- **Authentication Errors**: Verify the `automation_user` and `automation_secret` credentials.
- **Module Errors**: Refer to the `checkmk.general.hostgroup` module documentation: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/hostgroup.py
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini create_hostgroups.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files using `ansible-vault`.
- **Idempotency**: The playbook is idempotent, meaning repeated runs do not cause unintended changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Modular Variables**: Use a structured variables file to manage multiple hostgroups efficiently, as shown in the example.
- **Documentation**: Maintain clear documentation of your hostgroup definitions and variable configurations.

## Integration into CI/CD
To automate the creation of hostgroups in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file:

```yaml
name: Create Checkmk Hostgroups

on:
  push:
    branches:
      - main

jobs:
  create-hostgroups:
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
      - name: Run playbook
        env:
          ANSIBLE_AUTOMATION_USER: ${{ secrets.AUTOMATION_USER }}
          ANSIBLE_AUTOMATION_SECRET: ${{ secrets.AUTOMATION_SECRET }}
        run: |
          ansible-playbook -i inventory/hosts.ini create_hostgroups.yml
```

Store secrets like `AUTOMATION_USER` and `AUTOMATION_SECRET` in your CI/CD tool’s repository settings.

## Conclusion
The `create_hostgroups.yml` playbook provides an automated way to create hostgroups in Checkmk using the `checkmk.general.hostgroup` module. This guide enables you to execute the playbook locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.