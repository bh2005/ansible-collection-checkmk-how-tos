# HowTo: Set Up Distributed Monitoring with Checkmk Including CI/CD Integration

This guide explains how to use the `checkmk.general.site` module from the Checkmk Ansible Collection to set up a distributed monitoring environment in Checkmk and integrate this process into a CI/CD pipeline. The process automates the configuration of a central Checkmk server and the registration of one or more remote servers for distributed monitoring.

## Prerequisites
Before you begin, ensure the following requirements are met:
- **Ansible**: Ansible must be installed (version compatible with the collection, see SUPPORT.md in the Checkmk Ansible Collection repository).
- **Checkmk Ansible Collection**: The `checkmk.general` collection must be installed. Install it with:
  ```bash
  ansible-galaxy collection install checkmk.general
  ```
- **Checkmk Servers**: A central Checkmk server and at least one remote server must be running and accessible.
- **Credentials**: You need the `automation_user` and `automation_secret` for both the central and remote Checkmk servers.
- **Network Connectivity**: The servers must be able to communicate via the specified URLs.
- **Python Libraries**: The `netaddr` library is required for certain roles:
  ```bash
  pip install netaddr
  ```
- **CI/CD Tool**: This guide uses GitHub Actions for CI/CD integration, but the steps are adaptable to other tools like GitLab CI/CD or Jenkins.

## Overview
The `checkmk.general.site` module enables the management of Checkmk sites, including configuring distributed monitoring and registering remote sites. This guide focuses on:
1. Setting up distributed monitoring by configuring a central server and registering remote servers using an Ansible playbook.
2. Integrating the setup process into a CI/CD pipeline.

The process uses an Ansible playbook for distributed monitoring setup and a CI/CD workflow to automate the execution.

## Step-by-Step Instructions

### Step 1: Prepare the Inventory
Create an inventory file (`inventory/hosts.ini`) to define the target host. Since the playbook runs locally, a simple configuration is sufficient:

```ini
[localhost]
localhost ansible_connection=local
```

Save this file in a directory, e.g., `inventory/hosts.ini`.

### Step 2: Define Variables
Create a variables file (`group_vars/all.yml`) to store the required parameters for the central and remote Checkmk servers. Example:

```yaml
central_server_url: "http://central-server.example.com/"
central_site: "central"
central_automation_user: "automation"
central_automation_secret: "your-central-secret"
remote_servers:
  - remote_url: "http://remote1.example.com/"
    remote_site: "remote1"
    remote_automation_user: "automation"
    remote_automation_secret: "your-remote1-secret"
  - remote_url: "http://remote2.example.com/"
    remote_site: "remote2"
    remote_automation_user: "automation"
    remote_automation_secret: "your-remote2-secret"
```

Replace the values with the actual URLs, site names, and credentials of your Checkmk servers. The `remote_servers` list allows for multiple remote servers to be registered.

### Step 3: Create the Playbook
Create a playbook to set up distributed monitoring, e.g., `setup_distributed_monitoring.yml`:

```yaml
- name: Setup Distributed Monitoring in Checkmk
  hosts: localhost
  tasks:
    - name: Configure central site for distributed monitoring
      checkmk.general.site:
        server_url: "{{ central_server_url }}"
        site: "{{ central_site }}"
        automation_user: "{{ central_automation_user }}"
        automation_secret: "{{ central_automation_secret }}"
        distributed_monitoring: true
        state: present

    - name: Register remote sites
      checkmk.general.site:
        server_url: "{{ central_server_url }}"
        site: "{{ central_site }}"
        automation_user: "{{ central_automation_user }}"
        automation_secret: "{{ central_automation_secret }}"
        remote_url: "{{ item.remote_url }}"
        remote_site: "{{ item.remote_site }}"
        remote_automation_user: "{{ item.remote_automation_user }}"
        remote_automation_secret: "{{ item.remote_automation_secret }}"
        state: present
      loop: "{{ remote_servers }}"
```

**Explanation**:
- The first `checkmk.general.site` task configures the central site for distributed monitoring by setting `distributed_monitoring: true`.
- The second `checkmk.general.site` task registers each remote site from the `remote_servers` list, linking them to the central server.
- The `state: present` ensures the configuration is applied or updated.

### Step 4: Install Dependencies
Install the Checkmk Ansible Collection and required Python libraries:

```bash
ansible-galaxy collection install checkmk.general
pip install netaddr
```

### Step 5: Run the Playbook Locally
Execute the playbook to set up distributed monitoring:

```bash
ansible-playbook -i inventory/hosts.ini setup_distributed_monitoring.yml
```

Ensure the variables file (`group_vars/all.yml`) is in the same directory or a path recognized by Ansible.

### Step 6: Verify the Setup
1. Log in to the central Checkmk server.
2. Navigate to **Setup > Distributed monitoring** and confirm that the central server is configured for distributed monitoring and the remote servers are registered.
3. Verify that the connections are active and data is synchronized between the servers.

### Step 7: Integrate into CI/CD
To automate the distributed monitoring setup in a CI/CD pipeline (e.g., GitHub Actions), create a workflow file, e.g., `.github/workflows/checkmk_distributed_monitoring.yml`:

```yaml
name: Setup Checkmk Distributed Monitoring

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  setup-distributed-monitoring:
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
          ansible-playbook -i inventory/hosts.ini setup_distributed_monitoring.yml
```

**Explanation**:
- **Checkout repository**: Clones the repository containing the playbook and inventory.
- **Set up Python**: Configures a Python environment for Ansible.
- **Install dependencies**: Installs Ansible, `netaddr`, and the Checkmk Ansible Collection.
- **Run Ansible Playbook**: Executes the playbook, using secrets stored in the CI/CD tool for credentials.

Store secrets (`CENTRAL_AUTOMATION_USER`, `CENTRAL_AUTOMATION_SECRET`, `REMOTE_AUTOMATION_USER`, `REMOTE_AUTOMATION_SECRET`) in your CI/CD tool’s repository settings (e.g., in GitHub Actions under `Settings > Secrets and variables > Actions > New repository secret`). Note that for multiple remote servers, you may need to adjust the secret naming or pass credentials differently depending on your CI/CD tool.

### Step 8: Test the CI/CD Pipeline
1. Commit and push the workflow file, playbook, inventory, and variables file to your repository.
2. Monitor the pipeline execution in the GitHub Actions interface.
3. Verify that the distributed monitoring setup is completed successfully by checking the central Checkmk server.

## Troubleshooting
- **Network Errors**: Ensure the `central_server_url` and `remote_url` are correct and the servers are reachable.
- **Authentication Errors**: Verify the `automation_user` and `automation_secret` credentials for all servers.
- **Module Errors**: Refer to the `checkmk.general.site` module documentation: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/site.py
- **CI/CD Errors**: Check the pipeline logs for issues related to dependency installation or playbook execution.
- **Debugging**: Run the playbook with verbose output to identify issues:
  ```bash
  ansible-playbook -i inventory/hosts.ini setup_distributed_monitoring.yml -vvv
  ```

## Best Practices
- **Secure Storage of Secrets**: Store sensitive data like `automation_secret` in encrypted variables files (e.g., with `ansible-vault`) or CI/CD secrets.
- **Idempotency**: The playbook is idempotent, meaning repeated runs do not cause unintended changes.
- **Version Compatibility**: Check the compatibility of Checkmk and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Scalability**: Use a loop for multiple remote servers to simplify the playbook, as shown in the example.
- **Documentation**: Maintain clear documentation of your variables, playbook, and CI/CD configuration.

## Conclusion
The `setup_distributed_monitoring.yml` playbook automates the setup of a distributed monitoring environment in Checkmk using the `checkmk.general.site` module. By integrating this playbook into a CI/CD pipeline, you can streamline and automate the configuration process. This guide enables you to execute the playbook locally or within a CI/CD pipeline. For further details, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.