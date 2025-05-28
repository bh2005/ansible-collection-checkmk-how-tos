# HowTo: Copy Folder Structure in Checkmk

This guide explains how to use the `checkmk.general.folder` module from the Checkmk Ansible Collection to copy the folder structure from one Checkmk instance to another. The process involves exporting the folder structure from a source Checkmk instance and importing it into a target Checkmk instance.

## Prerequisites
Before you begin, ensure the following requirements are met:
- **Ansible**: Ansible must be installed (version compatible with the collection, see SUPPORT.md in the Checkmk Ansible Collection repository).
- **Checkmk Ansible Collection**: The `checkmk.general` collection must be installed. Install it with:
  ```bash
  ansible-galaxy collection install checkmk.general
  ```
- **Checkmk Servers**: Both the source and target Checkmk servers must be running and accessible.
- **Credentials**: You need the `automation_user` and `automation_secret` for both the source and target Checkmk servers.
- **Python Libraries**: The `netaddr` library may be required for certain roles:
  ```bash
  pip install netaddr
  ```

## Overview
The `checkmk.general.folder` module allows you to manage folders in Checkmk, including creating, updating, or deleting them. This guide focuses on using this module to:
1. Export the folder structure from a source Checkmk instance to a file.
2. Import the folder structure into a target Checkmk instance.

The process uses two Ansible playbooks: one for exporting the folder structure and one for importing it.

## Step-by-Step Instructions

### Step 1: Prepare the Inventory
Create an inventory file (`inventory/hosts.ini`) to define the target host. Since the playbook runs locally, a simple configuration is sufficient:

```ini
[localhost]
localhost ansible_connection=local
```

Save this file in a directory, e.g., `inventory/hosts.ini`.

### Step 2: Define Variables
Create a variables file (`group_vars/all.yml`) to store the required parameters for both the source and target Checkmk instances. Example:

```yaml
source_server_url: "http://source-checkmk.example.com/"
source_site: "source_site"
source_automation_user: "automation"
source_automation_secret: "your-source-secret"
target_server_url: "http://target-checkmk.example.com/"
target_site: "target_site"
target_automation_user: "automation"
target_automation_secret: "your-target-secret"
folder_file: "/path/to/backup/folders.yml"
```

Replace the values with the actual URLs, site names, and credentials of your Checkmk servers. The `folder_file` specifies where the folder structure will be saved or read from during export and import.

### Step 3: Create the Export Playbook
Create a playbook to export the folder structure, e.g., `export_folders.yml`:

```yaml
- name: Export Checkmk Folder Structure
  hosts: localhost
  tasks:
    - name: Fetch all folders
      checkmk.general.folder:
        server_url: "{{ source_server_url }}"
        site: "{{ source_site }}"
        automation_user: "{{ source_automation_user }}"
        automation_secret: "{{ source_automation_secret }}"
        state: query
      register: folders

    - name: Save folders to file
      ansible.builtin.copy:
        content: "{{ folders.folders | to_nice_yaml }}"
        dest: "{{ folder_file }}"
```

**Explanation**:
- The `checkmk.general.folder` task with `state: query` retrieves all folders from the source Checkmk server and stores them in the `folders` variable.
- The `ansible.builtin.copy` task writes the folder data to the specified `folder_file` in YAML format.

### Step 4: Create the Import Playbook
Create a playbook to import the folder structure, e.g., `import_folders.yml`:

```yaml
- name: Import Checkmk Folder Structure
  hosts: localhost
  tasks:
    - name: Read folders from file
      ansible.builtin.slurp:
        src: "{{ folder_file }}"
      register: folder_data

    - name: Parse folder data
      ansible.builtin.set_fact:
        folders: "{{ (folder_data.content | b64decode | from_yaml) }}"

    - name: Import folders
      checkmk.general.folder:
        server_url: "{{ target_server_url }}"
        site: "{{ target_site }}"
        automation_user: "{{ target_automation_user }}"
        automation_secret: "{{ target_automation_secret }}"
        path: "{{ item.path }}"
        name: "{{ item.name }}"
        state: present
      loop: "{{ folders }}"
```

**Explanation**:
- The `ansible.builtin.slurp` task reads the folder file.
- The `ansible.builtin.set_fact` task parses the YAML content into the `folders` variable.
- The `checkmk.general.folder` task imports each folder into the target Checkmk instance by iterating over the parsed data and setting `state: present`.

### Step 5: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 6: Run the Export Playbook
Execute the export playbook to save the folder structure:

```bash
ansible-playbook -i inventory/hosts.ini export_folders.yml
```

This creates a file (e.g., `/path/to/backup/folders.yml`) containing the folder structure in YAML format.

### Step 7: Run the Import Playbook
To import the folder structure to the target Checkmk instance, update the `target_server_url`, `target_site`, `target_automation_user`, and `target_automation_secret` in `group_vars/all.yml` if necessary, then run:

```bash
ansible-playbook -i inventory/hosts.ini import_folders.yml
```

### Step 8: Verify the Results
1. Log in to the target Checkmk server.
2. Navigate to **Setup > Hosts > Folders** and confirm that the folder structure has been copied correctly.
3. Check for any errors in the Checkmk logs or Ansible output.

## Troubleshooting
- **Network Errors**: Ensure the `source_server_url` and `target_server_url` are correct and the Checkmk servers are reachable.
- **Authentication Errors**: Verify the `automation_user` and `automation_secret` credentials for both servers.
- **File Errors**: Ensure the `folder_file` path is accessible and writable for export, and readable for import.
- **Module Errors**: Refer to the `checkmk.general.folder` module documentation: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/folder.py
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini export_folders.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files using `ansible-vault`.
- **Idempotency**: The playbooks are idempotent, meaning repeated runs do not cause unintended changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Backup Regularity**: Schedule regular exports to maintain an up-to-date copy of the folder structure.
- **Documentation**: Maintain clear documentation of your variables and file locations.

## Integration into CI/CD
To automate the export process in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file:

```yaml
name: Copy Checkmk Folder Structure

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  push:
    branches:
      - main

jobs:
  copy-folders:
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
      - name: Run export playbook
        env:
          ANSIBLE_SOURCE_AUTOMATION_USER: ${{ secrets.SOURCE_AUTOMATION_USER }}
          ANSIBLE_SOURCE_AUTOMATION_SECRET: ${{ secrets.SOURCE_AUTOMATION_SECRET }}
        run: |
          ansible-playbook -i inventory/hosts.ini export_folders.yml
```

Store secrets like `SOURCE_AUTOMATION_USER` and `SOURCE_AUTOMATION_SECRET` in your CI/CD tool’s repository settings. For importing, create a similar workflow for `import_folders.yml` with the appropriate target secrets.

## Conclusion
The `export_folders.yml` and `import_folders.yml` playbooks provide an automated way to copy folder structures between Checkmk instances using the `checkmk.general.folder` module. This guide enables you to execute these playbooks locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.