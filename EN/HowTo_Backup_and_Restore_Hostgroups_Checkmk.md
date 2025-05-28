# HowTo: Backup and Restore Hostgroups in Checkmk

This guide explains how to use the `checkmk.general.hostgroup` module from the Checkmk Ansible Collection to back up and restore hostgroups in Checkmk. The process involves creating a backup of hostgroup configurations and restoring them to the same or a different Checkmk instance.

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
The `checkmk.general.hostgroup` module allows you to manage hostgroups in Checkmk, including creating, updating, or deleting them. This guide focuses on using this module to:
1. Export (backup) hostgroup configurations to a file.
2. Restore hostgroup configurations from the backup file to a Checkmk instance.

The process uses two Ansible playbooks: one for backing up hostgroups and one for restoring them.

## Step-by-Step Instructions

### Step 1: Prepare the Inventory
Create an inventory file (`inventory/hosts.ini`) to define the target host. Since the playbook runs locally, a simple configuration is sufficient:

```ini
[localhost]
localhost ansible_connection=local
```

Save this file in a directory, e.g., `inventory/hosts.ini`.

### Step 2: Define Variables
Create a variables file (`group_vars/all.yml`) to store the required parameters. Example:

```yaml
server_url: "http://checkmk-server.example.com/"
site: "mysite"
automation_user: "automation"
automation_secret: "your-secret"
backup_file: "/path/to/backup/hostgroups.yml"
```

Replace the values with the actual URL, site name, and credentials of your Checkmk server. The `backup_file` specifies where the hostgroup configurations will be saved or read from during backup and restore.

### Step 3: Create the Backup Playbook
Create a playbook to back up hostgroups, e.g., `backup_hostgroups.yml`:

```yaml
- name: Backup Checkmk Hostgroups
  hosts: localhost
  tasks:
    - name: Fetch all hostgroups
      checkmk.general.hostgroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        state: query
      register: hostgroups

    - name: Save hostgroups to file
      ansible.builtin.copy:
        content: "{{ hostgroups.hostgroups | to_nice_yaml }}"
        dest: "{{ backup_file }}"
```

**Explanation**:
- The `checkmk.general.hostgroup` task with `state: query` retrieves all hostgroups from the Checkmk server and stores them in the `hostgroups` variable.
- The `ansible.builtin.copy` task writes the hostgroup data to the specified `backup_file` in YAML format.

### Step 4: Create the Restore Playbook
Create a playbook to restore hostgroups, e.g., `restore_hostgroups.yml`:

```yaml
- name: Restore Checkmk Hostgroups
  hosts: localhost
  tasks:
    - name: Read hostgroups from file
      ansible.builtin.slurp:
        src: "{{ backup_file }}"
      register: backup_data

    - name: Parse backup data
      ansible.builtin.set_fact:
        hostgroups: "{{ (backup_data.content | b64decode | from_yaml) }}"

    - name: Restore hostgroups
      checkmk.general.hostgroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item.name }}"
        state: present
      loop: "{{ hostgroups }}"
```

**Explanation**:
- The `ansible.builtin.slurp` task reads the backup file.
- The `ansible.builtin.set_fact` task parses the YAML content into the `hostgroups` variable.
- The `checkmk.general.hostgroup` task restores each hostgroup by iterating over the parsed data and setting `state: present`.

### Step 5: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 6: Run the Backup Playbook
Execute the backup playbook to save the hostgroup configurations:

```bash
ansible-playbook -i inventory/hosts.ini backup_hostgroups.yml
```

This creates a file (e.g., `/path/to/backup/hostgroups.yml`) containing the hostgroup configurations in YAML format.

### Step 7: Run the Restore Playbook
To restore the hostgroups to the same or a different Checkmk instance, update the `server_url`, `site`, `automation_user`, and `automation_secret` in `group_vars/all.yml` if necessary, then run:

```bash
ansible-playbook -i inventory/hosts.ini restore_hostgroups.yml
```

### Step 8: Verify the Results
1. Log in to the Checkmk server.
2. Navigate to **Setup > Hosts > Hostgroups** and confirm that the hostgroups have been restored correctly.
3. Check for any errors in the Checkmk logs or Ansible output.

## Troubleshooting
- **Network Errors**: Ensure the `server_url` is correct and the Checkmk server is reachable.
- **Authentication Errors**: Verify the `automation_user` and `automation_secret` credentials.
- **File Errors**: Ensure the `backup_file` path is accessible and writable for backup, and readable for restore.
- **Module Errors**: Refer to the `checkmk.general.hostgroup` module documentation: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/hostgroup.py
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini backup_hostgroups.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files using `ansible-vault`.
- **Idempotency**: The playbooks are idempotent, meaning repeated runs do not cause unintended changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Backup Regularity**: Schedule regular backups using a CI/CD pipeline or cron job to ensure up-to-date hostgroup configurations.
- **Documentation**: Maintain clear documentation of your variables and backup file locations.

## Integration into CI/CD
To automate backups in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file:

```yaml
name: Backup Checkmk Hostgroups

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  push:
    branches:
      - main

jobs:
  backup-hostgroups:
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
      - name: Run backup playbook
        env:
          ANSIBLE_AUTOMATION_USER: ${{ secrets.AUTOMATION_USER }}
          ANSIBLE_AUTOMATION_SECRET: ${{ secrets.AUTOMATION_SECRET }}
        run: |
          ansible-playbook -i inventory/hosts.ini backup_hostgroups.yml
```

Store secrets like `AUTOMATION_USER` and `AUTOMATION_SECRET` in your CI/CD tool’s repository settings.

## Conclusion
The `backup_hostgroups.yml` and `restore_hostgroups.yml` playbooks provide an automated way to back up and restore hostgroup configurations in Checkmk using the `checkmk.general.hostgroup` module. This guide enables you to execute these playbooks locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.