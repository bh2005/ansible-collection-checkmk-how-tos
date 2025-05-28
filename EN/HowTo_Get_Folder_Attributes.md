# HowTo: Retrieve Folder Attributes in Checkmk

This guide explains how to use the `checkmk.general.folder` module from the Checkmk Ansible Collection to retrieve folder attributes from a Checkmk instance. The process involves querying the folder structure and attributes and saving them to a file for further use or analysis.

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
The `checkmk.general.folder` module allows you to manage folders in Checkmk, including querying their attributes such as name, path, and custom properties. This guide focuses on using this module to:
1. Retrieve folder attributes from a Checkmk instance.
2. Save the retrieved data to a file in YAML format for documentation or further processing.

The process uses an Ansible playbook to query the folder attributes and store them.

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
output_file: "/path/to/output/folder_attributes.yml"
```

Replace the values with the actual URL, site name, and credentials of your Checkmk server. The `output_file` specifies where the folder attributes will be saved.

### Step 3: Create the Playbook
Create a playbook to retrieve folder attributes, e.g., `get_folder_attributes.yml`:

```yaml
- name: Retrieve Checkmk Folder Attributes
  hosts: localhost
  tasks:
    - name: Query all folders
      checkmk.general.folder:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        state: query
      register: folders

    - name: Save folder attributes to file
      ansible.builtin.copy:
        content: "{{ folders.folders | to_nice_yaml }}"
        dest: "{{ output_file }}"
```

**Explanation**:
- The `checkmk.general.folder` task with `state: query` retrieves all folders and their attributes (e.g., name, path, and custom attributes) from the Checkmk server and stores them in the `folders` variable.
- The `ansible.builtin.copy` task writes the folder data to the specified `output_file` in YAML format for easy readability and further use.

### Step 4: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 5: Run the Playbook
Execute the playbook to retrieve and save the folder attributes:

```bash
ansible-playbook -i inventory/hosts.ini get_folder_attributes.yml
```

This creates a file (e.g., `/path/to/output/folder_attributes.yml`) containing the folder attributes in YAML format.

### Step 6: Verify the Results
1. Check the output file (e.g., `/path/to/output/folder_attributes.yml`) to ensure it contains the expected folder attributes, such as:
   ```yaml
   - name: Servers
     path: /servers
     attributes:
       tag_snmp_ds: snmp
       tag_agent: cmk-agent
   - name: Databases
     path: /databases
     attributes:
       tag_snmp_ds: no-snmp
       tag_agent: no-agent
   ```
2. Log in to the Checkmk server, navigate to **Setup > Hosts > Folders**, and verify that the folder structure and attributes match the data in the output file.
3. Check for any errors in the Checkmk logs or Ansible output.

## Troubleshooting
- **Network Errors**: Ensure the `server_url` is correct and the Checkmk server is reachable.
- **Authentication Errors**: Verify the `automation_user` and `automation_secret` credentials.
- **File Errors**: Ensure the `output_file` path is accessible and writable.
- **Module Errors**: Refer to the `checkmk.general.folder` module documentation: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/folder.py
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini get_folder_attributes.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files using `ansible-vault`.
- **Idempotency**: The playbook is idempotent for querying, as it only retrieves data without making changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Output File Management**: Use a consistent naming convention and directory structure for output files to organize retrieved data.
- **Documentation**: Maintain clear documentation of your variables and output file locations.

## Integration into CI/CD
To automate the retrieval of folder attributes in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file:

```yaml
name: Retrieve Checkmk Folder Attributes

on:
  schedule:
    - cron: '0 0 * * *' # Daily at midnight
  push:
    branches:
      - main

jobs:
  get-folder-attributes:
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
          ansible-playbook -i inventory/hosts.ini get_folder_attributes.yml
```

Store secrets like `AUTOMATION_USER` and `AUTOMATION_SECRET` in your CI/CD tool’s repository settings.

## Conclusion
The `get_folder_attributes.yml` playbook provides an automated way to retrieve folder attributes from a Checkmk instance using the `checkmk.general.folder` module and save them to a YAML file. This guide enables you to execute the playbook locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.