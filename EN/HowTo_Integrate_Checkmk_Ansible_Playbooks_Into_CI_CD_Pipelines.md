# HowTo: Integrate Checkmk Ansible Playbooks into CI/CD Pipelines

This guide explains how to integrate Ansible playbooks from the Checkmk Ansible Collection (`checkmk.general`) into a CI/CD pipeline, using GitHub Actions as an example. The process enables the automation of Checkmk configurations, such as creating hosts, folders, or rules, within a continuous integration and deployment workflow. The steps are adaptable to other CI/CD systems like GitLab CI/CD or Jenkins.

## Prerequisites
Before you begin, ensure the following requirements are met:
- **Ansible**: Ansible must be installed on the CI/CD runner or environment (version compatible with the collection, see SUPPORT.md).
- **Checkmk Ansible Collection**: The `checkmk.general` collection must be installed. Install it with:
  ```bash
  ansible-galaxy collection install checkmk.general
  ```
- **Checkmk Server**: A running Checkmk server with network access.
- **Credentials**: You need the `automation_user` and `automation_secret` for the Checkmk server.
- **Git Repository**: A repository containing your Ansible playbooks that use the Checkmk Ansible Collection.
- **CI/CD Tool**: This guide uses GitHub Actions, but the concepts apply to other tools with adjusted syntax.
- **Python Libraries**: The `netaddr` library is required for certain roles:
  ```bash
  pip install netaddr
  ```

## Step 1: Install the Checkmk Ansible Collection
The Checkmk Ansible Collection must be installed in the CI/CD environment. This can be automated as part of the pipeline.

1. **Installation Command**:
   ```bash
   ansible-galaxy collection install checkmk.general
   ```

2. **Dependencies**:
   Ensure required Python libraries are installed. For example, the `agent` role requires `netaddr`:
   ```bash
   pip install netaddr
   ```

## Step 2: Create an Ansible Playbook
Create a playbook that uses modules from the Checkmk Ansible Collection. Below is an example playbook (`create_host.yml`) that creates a host in Checkmk:

```yaml
- name: Create a host in Checkmk
  hosts: localhost
  tasks:
    - name: Create a single host
      checkmk.general.host:
        server_url: "{{ server_url }}"
        site: "{{ site }}"
        automation_user: "{{ automation_user }}"
        automation_secret: "{{ automation_secret }}"
        name: "webserver01"
        folder: "/servers"
        attributes:
          ipaddress: "192.168.1.10"
          alias: "Web Server 01"
        state: present
```

Save this playbook in your repository, e.g., as `create_host.yml`.

## Step 3: Configure the CI/CD Pipeline
Below is an example configuration for a GitHub Actions workflow to run the playbook.

1. **Create the Workflow File**:
   Create a file named `.github/workflows/checkmk.yml` in your repository:

```yaml
name: Checkmk Ansible Integration

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  ansible:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install Ansible and dependencies
        run: |
          pip install ansible
          pip install netaddr
          ansible-galaxy collection install checkmk.general

      - name: Run Ansible Playbook
        env:
          ANSIBLE_AUTOMATION_USER: ${{ secrets.AUTOMATION_USER }}
          ANSIBLE_AUTOMATION_SECRET: ${{ secrets.AUTOMATION_SECRET }}
        run: |
          ansible-playbook create_host.yml -i inventory/hosts.ini
```

2. **Explanation of Steps**:
   - **Checkout repository**: Clones the repository containing your playbooks.
   - **Set up Python**: Configures a Python environment required for Ansible.
   - **Install Ansible and dependencies**: Installs Ansible, the `netaddr` library, and the Checkmk Ansible saturationCollection.
   - **Run Ansible Playbook**: Executes the playbook, passing credentials as environment variables.

3. **Secure Storage of Credentials**:
   Store sensitive data like `automation_user` and `automation_secret` as secrets in your CI/CD tool:
   - In GitHub Actions: Go to `Settings > Secrets and variables > Actions > New repository secret` and add `AUTOMATION_USER` and `AUTOMATION_SECRET`.
   - These secrets are accessed in the workflow as environment variables.

## Step 4: Inventory and Variables
1. **Inventory File**:
   Create an inventory file (`inventory/hosts.ini`) in your repository to define the target hosts. For local execution, it can look like this:
   ```ini
   [localhost]
   localhost ansible_connection=local
   ```

2. **Variables**:
   Define variables like `server_url` and `site` either directly in the playbook or in a separate variables file (`group_vars/all.yml`):
   ```yaml
   server_url: "http://checkmk-server.example.com/"
   site: "mysite"
   ```

## Step 5: Test the Pipeline
1. **Commit and Push**:
   Commit the workflow file, playbook, and inventory file to your repository and push the changes.
2. **Pipeline Execution**:
   The pipeline will automatically trigger on a push or pull request to the `main` branch. Monitor the execution in the GitHub Actions interface.
3. **Troubleshooting**:
   - Ensure the Checkmk server URL is reachable.
   - Verify that the credentials are correct.
   - Refer to the Checkmk Ansible Collection documentation or the `README.md` for specific module parameters: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/README.md

## Step 6: Advanced Configurations
- **Multiple Playbooks**: Organize multiple playbooks in a directory and execute them sequentially in the pipeline.
- **Tagging**: Use Ansible tags to run specific tasks, e.g.:
  ```yaml
  ansible-playbook create_host.yml -i inventory/hosts.ini --tags "create_host"
  ```
- **Distributed Monitoring**: Use modules like `checkmk.general.site` for distributed Checkmk setups.
- **Dynamic Inventory**: Utilize the `checkmk.general.checkmk` inventory plugin to fetch hosts directly from Checkmk:
  ```yaml
  plugin: checkmk.general.checkmk
  server_url: "http://checkmk-server.example.com/"
  site: "mysite"
  automation_user: "{{ automation_user }}"
  automation_secret: "{{ automation_secret }}"
  groupsources: ["hosttags", "sites"]
  ```
  Save this as `checkmk.yml` and use it with `ansible-inventory -i checkmk.yml --graph`.

## Step 7: Best Practices
- **Idempotency**: Ensure your playbooks are idempotent to prevent unintended changes.
- **Logging**: Enable logging only for debugging, as sensitive information like passwords may appear in logs.
- **Versioning**: Verify compatibility between Ansible, Checkmk, and the collection. Check SUPPORT.md for tested versions: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Error Handling**: Implement error handling in the playbook (e.g., using `ignore_errors` or `failed_when`) to prevent pipeline failures.

## Conclusion
By integrating Checkmk Ansible playbooks into your CI/CD pipeline, you can automate and maintain consistent Checkmk configurations. This guide provides a foundation that can be adapted to specific requirements. For further details on modules and roles, consult the Checkmk Ansible Collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.