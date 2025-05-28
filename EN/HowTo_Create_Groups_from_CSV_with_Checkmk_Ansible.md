# HowTo: Create Hostgroups from a CSV File with Checkmk Ansible

This guide explains how to use the `checkmk.general.hostgroup` module from the Checkmk Ansible Collection to create hostgroups in Checkmk based on data from a CSV file. The process involves reading group definitions from a CSV file and using an Ansible playbook to create the corresponding hostgroups in a Checkmk instance.

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
- **CSV File**: A CSV file containing the hostgroup definitions (e.g., group names and optional attributes).

## Overview
The `checkmk.general.hostgroup` module allows you to manage hostgroups in Checkmk, including creating, updating, or deleting them. This guide focuses on using this module to:
1. Read hostgroup data from a CSV file.
2. Create hostgroups in Checkmk based on the CSV data.

The process uses an Ansible playbook to read the CSV file and create the hostgroups.

## Step-by-Step Instructions

### Step 1: Prepare the CSV File
Create a CSV file (e.g., `hostgroups.csv`) with the hostgroup definitions. The file should include at least a column for the group name. Optional attributes like aliases can be included. Example:

```csv
name,alias
servers,Production Servers
databases,Database Systems
network,Network Devices
```

Save the file in a directory, e.g., `data/hostgroups.csv`.

### Step 2: Prepare the Inventory
Create an inventory file (`inventory/hosts.ini`) to define the target host. Since the playbook runs locally, a simple configuration is sufficient:

```ini
[localhost]
localhost ansible_connection=local
```

Save this file in a directory, e.g., `inventory/hosts.ini`.

### Step 3: Define Variables
Create a variables file (`group_vars/all.yml`) to store the required parameters. Example:

```yaml
server_url: "http://checkmk-server.example.com/"
site: "mysite"
automation_user: "automation"
automation_secret: "your-secret"
csv_file: "data/hostgroups.csv"
```

Replace the values with the actual URL, site name, and credentials of your Checkmk server. The `csv_file` specifies the path to the CSV file containing the hostgroup definitions.

### Step 4: Create the Playbook
Create a playbook to read the CSV file and create hostgroups, e.g., `create_hostgroups_from_csv.yml`:

```yaml
- name: Create Checkmk Hostgroups from CSV
  hosts: localhost
  tasks:
    - name: Read hostgroups from CSV
      ansible.builtin.read_csv:
        path: "{{ csv_file }}"
      register: hostgroup_data

    - name: Create hostgroups
      checkmk.general.hostgroup:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item.name }}"
        alias: "{{ item.alias | default(omit) }}"
        state: present
      loop: "{{ hostgroup_data.list }}"
```

**Explanation**:
- The `ansible.builtin.read_csv` task reads the CSV file and stores the data in the `hostgroup_data` variable.
- The `checkmk.general.hostgroup` task iterates over the CSV data to create each hostgroup, using the `name` and optional `alias` fields. The `state: present` ensures the hostgroups are created or updated if they already exist.

### Step 5: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 6: Run the Playbook
Execute the playbook to create the hostgroups based on the CSV file:

```bash
ansible-playbook -i inventory/hosts.ini create_hostgroups_from_csv.yml
```

Ensure the `hostgroups.csv` file is in the specified `csv_file` path and the variables file is correctly configured.

### Step 7: Verify the Results
1. Log in to the Checkmk server.
2. Navigate to **Setup > Hosts > Hostgroups** and confirm that the hostgroups from the CSV file have been created correctly.
3. Check for any errors in the Checkmk logs or Ansible output.

## Troubleshooting
- **CSV File Errors**: Ensure the CSV file is properly formatted and accessible. The `name` column is mandatory; other columns like `alias` are optional.
- **Network Errors**: Verify that the `server_url` is correct and the Checkmk server is reachable.
- **Authentication Errors**: Confirm the `automation_user` and `automation_secret` credentials are valid.
- **Module Errors**: Refer to the `checkmk.general.hostgroup` module documentation: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/hostgroup.py
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini create_hostgroups_from_csv.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files using `ansible-vault`.
- **Idempotency**: The playbook is idempotent, meaning repeated runs do not cause unintended changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **CSV Validation**: Validate the CSV file format before running the playbook to avoid errors (e.g., ensure no missing or malformed headers).
- **Documentation**: Maintain clear documentation of your CSV file structure and variable configurations.

## Integration into CI/CD
To automate the creation of hostgroups in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file:

```yaml
name: Create Checkmk Hostgroups from CSV

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
          ansible-playbook -i inventory/hosts.ini create_hostgroups_from_csv.yml
```

Store secrets like `AUTOMATION_USER` and `AUTOMATION_SECRET` in your CI/CD tool’s repository settings.

## Conclusion
The `create_hostgroups_from_csv.yml` playbook provides an automated way to create hostgroups in Checkmk using data from a CSV file with the `checkmk.general.hostgroup` module. This guide enables you to execute the playbook locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.