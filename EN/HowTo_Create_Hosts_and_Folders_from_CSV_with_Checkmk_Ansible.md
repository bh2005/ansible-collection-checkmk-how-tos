# HowTo: Create Hosts and Folders from a CSV File with Checkmk Ansible

This guide explains how to use the `checkmk.general.folder` and `checkmk.general.host` modules from the Checkmk Ansible Collection to create folders and hosts in Checkmk based on data from a CSV file. The process involves reading folder and host definitions from a CSV file and using an Ansible playbook to create the corresponding folders and hosts in a Checkmk instance.

## Prerequisites
Before you begin, ensure the following requirements are met:
- **Ansible**: Ansible must be installed (version compatible with the collection, see SUPPORT.md in the Checkmk Ansible Collection repository).
- **Checkmk Ansible Collection**: The `checkmk.general` collection must be installed. Install it with:
  ```bash
  ansible-galaxy collection install checkmk.general
  ```
- **Checkmk Server**: A running Checkmk server with network access.
- **Credentials**: You need the `automation_user` and `automation_secret` for the Checkmk server.
- **Python Libraries**: The `netaddr` library is required for certain roles:
  ```bash
  pip install netaddr
  ```
- **CSV File**: A CSV file containing the folder and host definitions (e.g., folder paths, hostnames, and optional attributes like IP addresses).

## Overview
The `checkmk.general.folder` and `checkmk.general.host` modules allow you to manage folders and hosts in Checkmk, including creating, updating, or deleting them. This guide focuses on using these modules to:
1. Read folder and host data from a CSV file.
2. Create folders and hosts in Checkmk based on the CSV data.

The process uses an Ansible playbook to read the CSV file and create the folders and hosts.

## Step-by-Step Instructions

### Step 1: Prepare the CSV File
Create a CSV file (e.g., `hosts_and_folders.csv`) with the folder and host definitions. The file should include columns for the folder path, folder name, hostname, and optional attributes like IP address or alias. Example:

```csv
folder_path,folder_name,hostname,ip_address,alias
/servers,Servers,web01,192.168.1.10,Web Server 01
/servers,Servers,web02,192.168.1.11,Web Server 02
/databases,Databases,db01,192.168.1.20,Database Server
```

Save the file in a directory, e.g., `data/hosts_and_folders.csv`. The `folder_path` and `folder_name` define the folder structure, while `hostname`, `ip_address`, and `alias` define the hosts.

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
csv_file: "data/hosts_and_folders.csv"
```

Replace the values with the actual URL, site name, and credentials of your Checkmk server. The `csv_file` specifies the path to the CSV file containing the folder and host definitions.

### Step 4: Create the Playbook
Create a playbook to read the CSV file and create folders and hosts, e.g., `create_hosts_and_folders_from_csv.yml`:

```yaml
- name: Create Checkmk Folders and Hosts from CSV
  hosts: localhost
  tasks:
    - name: Read folders and hosts from CSV
      ansible.builtin.read_csv:
        path: "{{ csv_file }}"
      register: csv_data

    - name: Create folders
      checkmk.general.folder:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        path: "{{ item.folder_path }}"
        name: "{{ item.folder_name }}"
        state: present
      loop: "{{ csv_data.list | unique }}"
      when: item.folder_path is defined and item.folder_name is defined

    - name: Create hosts
      checkmk.general.host:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "{{ item.hostname }}"
        folder: "{{ item.folder_path }}"
        attributes:
          ipaddress: "{{ item.ip_address | default(omit) }}"
          alias: "{{ item.alias | default(omit) }}"
        state: present
      loop: "{{ csv_data.list }}"
      when: item.hostname is defined
```

**Explanation**:
- The `ansible.builtin.read_csv` task reads the CSV file and stores the data in the `csv_data` variable.
- The `checkmk.general.folder` task creates folders based on the `folder_path` and `folder_name` columns. The `unique` filter ensures each folder is created only once.
- The `checkmk.general.host` task creates hosts based on the `hostname`, `folder_path`, and optional `ip_address` and `alias` columns. The `state: present` ensures folders and hosts are created or updated if they already exist.
- The `when` conditions ensure that only valid entries are processed.

### Step 5: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 6: Run the Playbook
Execute the playbook to create the folders and hosts based on the CSV file:

```bash
ansible-playbook -i inventory/hosts.ini create_hosts_and_folders_from_csv.yml
```

Ensure the `hosts_and_folders.csv` file is in the specified `csv_file` path and the variables file is correctly configured.

### Step 7: Verify the Results
1. Log in to the Checkmk server.
2. Navigate to **Setup > Hosts > Folders** and confirm that the folder structure from the CSV file has been created correctly.
3. Navigate to **Setup > Hosts** and verify that the hosts are assigned to the correct folders with the specified attributes (e.g., IP address, alias).
4. Check for any errors in the Checkmk logs or Ansible output.

## Troubleshooting
- **CSV File Errors**: Ensure the CSV file is properly formatted and accessible. Mandatory columns are `folder_path`, `folder_name`, and `hostname`; others like `ip_address` and `alias` are optional.
- **Network Errors**: Verify that the `server_url` is correct and the Checkmk server is reachable.
- **Authentication Errors**: Confirm the `automation_user` and `automation_secret` credentials are valid.
- **Module Errors**: Refer to the `checkmk.general.folder` and `checkmk.general.host` module documentation:
  - https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/folder.py
  - https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/host.py
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini create_hosts_and_folders_from_csv.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files using `ansible-vault`.
- **Idempotency**: The playbook is idempotent, meaning repeated runs do not cause unintended changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **CSV Validation**: Validate the CSV file format before running the playbook to avoid errors (e.g., ensure no missing or malformed headers).
- **Documentation**: Maintain clear documentation of your CSV file structure and variable configurations.

## Integration into CI/CD
To automate the creation of folders and hosts in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file:

```yaml
name: Create Checkmk Folders and Hosts from CSV

on:
  push:
    branches:
      - main

jobs:
  create-hosts-and-folders:
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
          ansible-playbook -i inventory/hosts.ini create_hosts_and_folders_from_csv.yml
```

Store secrets like `AUTOMATION_USER` and `AUTOMATION_SECRET` in your CI/CD tool’s repository settings.

## Conclusion
The `create_hosts_and_folders_from_csv.yml` playbook provides an automated way to create folders and hosts in Checkmk using data from a CSV file with the `checkmk.general.folder` and `checkmk.general.host` modules. This guide enables you to execute the playbook locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.