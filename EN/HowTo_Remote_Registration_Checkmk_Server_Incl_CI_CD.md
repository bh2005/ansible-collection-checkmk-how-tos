# HowTo: Remote Registration of a Checkmk Server Including CI/CD Integration

This guide explains how to use the `checkmk.general.site` module from the Checkmk Ansible Collection to register a remote Checkmk server in a distributed monitoring environment and integrate this process into a CI/CD pipeline. The process automates the registration of a remote Checkmk server with a central Checkmk server, ensuring seamless distributed monitoring setup.

## Prerequisites
Before you begin, ensure the following requirements are met:
- **Ansible**: Ansible must be installed (version compatible with the collection, see SUPPORT.md in the Checkmk Ansible Collection repository).
- **Checkmk Ansible Collection**: The `checkmk.general` collection must be installed. Install it with:
  ```bash
  ansible-galaxy collection install checkmk.general
  ```
- **Checkmk Servers**: Both the central and remote Checkmk servers must be running and accessible.
- **Credentials**: You need the `automation_user` and `automation_secret` for both the central and remote Checkmk servers.
- **Network Connectivity**: The servers must be able to communicate via the specified URLs.
- **Python Libraries**: The `netaddr` library is required for certain roles:
  ```bash
  pip install netaddr
  ```
- **CI/CD Tool**: This guide uses GitHub Actions for CI/CD integration, but the steps are adaptable to other tools like GitLab CI/CD or Jenkins.

## Overview
The `checkmk.general.site` module enables the management of Checkmk sites, including the registration of remote sites for distributed monitoring. This guide focuses on:
1. Registering a remote Checkmk server with a central server using an Ansible playbook.
2. Integrating the registration process into a CI/CD pipeline.

The process uses an Ansible playbook for remote registration and a CI/CD workflow to automate the execution.

## Step-by-Step Instructions

### Step 1: Prepare the Inventory
Create an inventory file (`inventory/hosts.ini`) to define the target host. Since the playbook runs locally, a simple configuration is sufficient:

```ini
[localhost]
localhost ansible_connection=local
```

Save this file in a directory, e.g., `inventory/hosts.ini`.

### Step 2: Define Variables
Create a variables file (`group_vars/all.yml`) to store the required parameters for both the central and remote Checkmk servers. Example:

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

Replace the values with the actual URLs, site names, and credentials of your Checkmk servers.

### Step 3: Create the Playbook
Create a playbook to register the remote Checkmk server, e.g., `remote_registration.yml`:

```yaml
- name: Register a Remote Checkmk Site
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

**Explanation**:
- The `checkmk.general.site` task registers the remote site with the central Checkmk server using the provided credentials and URLs.
- The `state: present` ensures the remote site is registered and configured for distributed monitoring.

### Step 4: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 5: Run the Playbook Locally
Execute the playbook to register the remote site:

```bash
ansible-playbook -i inventory/hosts.ini remote_registration.yml
```

Ensure the variables file (`group_vars/all.yml`) is in the same directory or a path recognized by Ansible.

### Step 6: Verify the Registration
1. Log in to the central Checkmk server.
2. Navigate to **Setup > Distributed monitoring** and confirm that the remote server is correctly registered.
3. Verify that the connection is active and data is synchronized between the servers.

### Step 7: Integrate into CI/CD
To automate the remote registration in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file, e.g., `.github/workflows/checkmk_remote_registration.yml`:

```yaml
name: Register Remote Checkmk Site

on:
  push:
    branches:
      - main
  pull_request:
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
          ansible-playbook -i inventory/hosts.ini remote_registration.yml
```

**Explanation**:
- **Checkout repository**: Clones the repository containing the playbook and inventory.
- **Set up Python**: Configures a Python environment for Ansible.
- **Install dependencies**: Installs Ansible, `netaddr`, and the Checkmk Ansible Collection.
- **Run Ansible Playbook**: Executes the playbook, using secrets stored in the CI/CD tool for credentials.

Store secrets (`CENTRAL_AUTOMATION_USER`, `CENTRAL_AUTOMATION_SECRET`, `REMOTE_AUTOMATION_USER`, `REMOTE_AUTOMATION_SECRET`) in your CI/CD tool’s repository settings (e.g., in GitHub Actions under `Settings > Secrets and variables > Actions > New repository secret`).

### Step 8: Test the CI/CD Pipeline
1. Commit and push the workflow file, playbook, inventory, and variables file to your repository.
2. Monitor the pipeline execution in the GitHub Actions interface.
3. Verify that the remote site is registered successfully by checking the central Checkmk server.

## Troubleshooting
- **Network Errors**: Ensure the `central_server_url` and `remote_server_url` are correct and the servers are reachable.
- **Authentication Errors**: Verify the `automation_user` and `automation_secret` credentials for both servers.
- **Module Errors**: Refer to the `checkmk.general.site` module documentation: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/site.py
- **CI/CD Errors**: Check the pipeline logs for issues related to dependency installation or playbook execution.
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini remote_registration.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files (e.g., with `ansible-vault`) or CI/CD secrets.
- **Idempotency**: The playbook is idempotent, meaning repeated runs do not cause unintended changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Pipeline Triggers**: Configure the CI/CD pipeline to run on specific events (e.g., push, pull request, or schedule) to align with your workflow.
- **Documentation**: Maintain clear documentation of your variables, playbook, and CI/CD configuration.

## Conclusion
The `remote_registration.yml` playbook automates the registration of a remote Checkmk server in a distributed monitoring environment using the `checkmk.general.site` module. By integrating this playbook into a CI/CD pipeline, you can streamline and automate the setup process. This guide enables you to execute the playbook locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.