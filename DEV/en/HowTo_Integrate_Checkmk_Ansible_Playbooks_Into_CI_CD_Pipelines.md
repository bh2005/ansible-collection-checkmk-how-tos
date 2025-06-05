Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

# HowTo to integrate Checkmk Ansible Playbooks in CI/CD pipelines

This guide describes how to integrate the ansible playbooks from the Checkmk Ansible Collection (https://github.com/Checkmk/ansible-collection-checkmk.general) into a CI/CD pipeline. The integration allows the automation of checkmk configurations, such as setting up servers, managing sites or adding hosts, in a continuous integration and deployment process. We use GitHub action as an example, but the steps are transferable to other CI/CD systems such as GitLab CI/CD or Jenkins.

## Conditions
Before you start, make sure that the following conditions are met:
- **Ansible installed**: Ansible must be available on the Runner or in the CI/CD environment.
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to a running checkmk server with API access.
- **Git-Repository**: A repository with your playbooks that uses the Checkmk Ansible Collection.
- **CI/CD-Tool**: In this guide we use GitHub Actions. For other tools, you need to adjust the syntax.
- **Python and dependencies**: The Checkmk Ansible Collection requires Python and, if necessary, the Python library `netaddr` for certain roles (e.g. `agent`).

## Step 1: Installation of the Checkmk Ansible Collection
The Checkmk Ansible Collection can be installed via Ansible Galaxy. This can be automated in your CI/CD pipeline.

1. **Installation command**:
♪
ansible-galaxy collection install checkmk.general
♪
Alternatively, you can clone the collection directly from the GitHub repository:
♪
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
♪

2. **dependence**:

Make sure the required Python libraries are installed. For the `agent` roll `netaddr` is required:
♪
pip install netaddr
♪

## Step 2: Creating an Ansible Playbook
Create a playbook that uses the modules of the Checkmk Ansible Collection. Here is an example that creates a folder in Checkmk:

♪
- name: Create a folder in Checkmk
hosts: localhost
tasks:
- name: Create a single folder
checkmk.general.folder:
server_url: "http://myserver/"
site: "mysite"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
path: "/my_folder"
name: "My Folder"
state: "present"
♪

Save this playbook as `create_folder.yml` in your repository.

## Step 3: Configuring the CI/CD pipeline
An example configuration for GitHub Actions is created below, which executes the Playbook.

1. **Create the workflow file**:
Create a `.github/workflows/checkmk.yml file in your repository:

♪
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
# Checkout of the repositories
- name: Checkout repository
uses: actions/checkout@v3

# Set up Python
- name: Set up Python
uses: actions/setup-python@v4
with:
python version: '3.x'

# Installing Ansible and Dependencies
- name: Install Ansible and dependencies
run:
pip install ansible
pip install netaddr
ansible-galaxy collection install checkmk.general

# Running the Ansible Playbook
- name: Run Ansible Playbook
env:
ANSIBLE_AUTOMATION_USER: ${ secrets.AUTOMATION_USER }
ANSIBLE_AUTOMATION_SECRET: ${ secrets.AUTOMATION_SECRET }
run:

ansible-playbook create_folder.yml -i inventory/hosts.ini
♪

2. **Declaration of steps**:
- **Checkout repository**: Clamps the repository that contains your playbooks.
- **Set up Python**: Sets a Python environment required for Ansible.
- **Install Ansible and dependencies**: Installs Ansible, the `netaddr` library and the Checkmk Ansible Collection.
- **Run Ansible Playbook**: Runs the Playbook and transfers the access data as environment variables.

3. **Safe storage of access data**:
Save sensitive data like `automation_user` and `automation_secret` as secrets in your CI/CD tool:
- In GitHub Actions: Go to `Settings > Secrets and variable > Actions > New repository secret` and add `AUTOMATION_USER` and `AUTOMATION_SECRET`.
- These secrets are used as environment variables in the workflow.

## Step 4: Inventory and Variables
1. **Inventory file**:
Create an inventory file (`inventory/hosts.ini`) in the repository to define the target host. For local execution it can look like this:
♪
[localhost]
localhost ansible_connection=local
♪

**Variablen**:
Define variables such as `server_url` and `site` either directly in the Playbook or in a separate variable file (`group_vars/all.yml`):
♪
server_url: "http://myserver/"
site: "mysite"
♪

## Step 5: Testing the pipeline
1. **Commit and Push**:
Add the workflow file, playbook and inventory file to your repository and push these changes.
2. **Pipeline version**:
The pipeline is automatically triggered for a push or pull request on the `main` bug. Check the execution in the GitHub Actions interface.
3. ** Bug fix**:
- Make sure the checkmk server URL is accessible.
- Check if the access data is correct.

- Consult the checkmk documentation or the 'README.md' of the collection for specific module parameters: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/README.md[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/maind/MEAD.

## Step 6: Advanced configurations
- **More Playbooks**: Organize multiple playbooks in a directory and run them one after the other in the pipeline.
- **Tagging**: Use Ansible tags to perform specific tasks, e.g. B.:
♪
ansible-playbook create_folder.yml -i inventory/hosts.ini --tags "create_folder"
♪
- **Distribued monitoring**: Use modules such as `checkmk.general.site` or `checkmk.general.sites` for distributed checkmk setups.[](https://github.com/Checkmk/ansible-collection-checkmk./releases)
- **Dynamic inventory**: Use the `checkmk.general.checkmk` inventory plugin to get hosts directly from Checkmk:
♪
plugin: checkmk.general.checkmk
server_url: "http://myserver/"
site: "mysite"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
groupsources: ["hosttags", "sites"]
♪
Save this as `checkmk.yml` and use it with `ansible-inventory -i checkmk.yml --graph`.[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/inventory/checkmk.py)

## Step 7: Best Practices
- **Idempotenz**: Make sure your playbooks are idempotent to avoid unexpected changes.
- **Logging**: Activate logging only for debugging purposes as sensitive information such as passwords can appear in logs.[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/roles/server/README.md)

- **Version**: Note the compatibility between Ansible, Checkmk and the Collection. Check the SUPPORT.md for tested versions: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md.[](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md)
- **Error Treatment**: Implement Error Treatment in Playbook, e.g. by `ignore_errors` or `failed_when` to avoid pipeline interruptions.

## Fazite
By integrating the Checkmk Ansible Collection into your CI/CD pipeline, you can automate and keep checkmk configurations consistent. This guide provides a basis that can be adapted to specific requirements. For further details on modules and roles, consult the collection documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.