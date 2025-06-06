Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

# HowTo: Use of remote-registration.yml Playbooks for Checkmk

This document describes how to use the Ansible Playbook `remote-registration.yml` from the Checkmk Ansible Collection (`checkmk.general`) to register a remote checkmk server in a distributed monitoring environment. The Playbook automates the registration of a remote server on a central checkmk server. The steps include preparation, configuration and execution of the Playbook.

## Conditions
Before using the Playbook, make sure that the following conditions are met:
- **Ansible**: Ansible (version compatible with the Collection, see SUPPORT.md) must be installed.
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: A central checkmk server and a remote server must run. Both must be accessible.
- **Access data**: You need the access data for the `automation_user` and `automation_secret` for both the central and the remote server.
- ** Network connectivity**: The servers must be able to communicate with each other via the specified URLs.
- **Python libraries**: The `netaddr` library is required for some roles:
♪
pip install netaddr
♪

## Overview of the Playbook
The Playbook `remote-registration.yml` (available at: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/usecases/remote-registration.yml) performs the following tasks:
1. Registers a remote checkmk server at a central checkmk server.
Two. Configures the connection for distributed monitoring.
3. Activates the changes on the central server.

Here is an example of the playbook (based on the structure from the repository):

♪
- name: Register a remote site
hosts: localhost
tasks:
- name: Register remote site
checkmk.general.site:
server_url: "{ central_server_url }"
site: "{ central_site }"
automation_user: "{ central_automation_user }"
automation_secret: "{ central_automation_secret }"
remote_url: "{ remote_server_url }"
remote_site: "{ remote_site }"
remote_automation_user: "{ remote_automation_user }"
remote_automation_secret: "{ remote_automation_secret }"
state: present
♪

## Step-by-step guide

### Step 1: Preparing the inventory
Create an inventory file (`inventory/hosts.ini`) to define target hosts. Since the playbook is executed on `localhost`, a simple configuration is sufficient:

♪
[localhost]
localhost ansible_connection=local
♪

Save this file in a directory like `inventory/hosts.ini`.

### Step 2: Defining variables
Create a variable file (`group_vars/all.yml`) to define the required parameters. An example:

♪
central_server_url: "http://central-server.example.com/"
central_site: "central"
central_automation_user: "automation"
central_automation_secret: "your-central-secret"
remote_server_url: "http://remote-server.example.com/"
remote_site: "remote"
remote_automation_user: "automation"
remote_automation_secret: "your-remote-secret"
♪

Replace the values by the actual URLs and access data of your checkmk server.

### Step 3: Cloning or copying the Playbook
clone the repository of the Checkmk Ansible Collection or copy the `remote-registration.yml`-Playbook to your project directory:

♪
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
♪

Alternatively, you can copy the playbook directly from the repository: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/usecases/remote-registration.yml

Save the playbook for example as `remote-registration.yml` in your project.

### Step 4: Installation of dependencies
Install the Checkmk Ansible Collection and the required Python libraries:

♪
ansible-galaxy collection install checkmk.general
pip install netaddr
♪

### Step 5: Running the Playbook
Run the Playbook with the following command:

♪
ansible-playbook -i inventory/hosts.ini remote-registration.yml
♪

Make sure that the variable file (`group_vars/all.yml`) is in the same directory or in a path recognized by Ansible.

### Step 6: Check registration
1. Log in to the central checkmk server.
Two. Navigate to **Setup > Distributed Monitoring** and check if the remote server has been registered correctly.
3. Verify that the connection is active and data are synchronized.

## Bug fix
- **Network Error**: Make sure the `central_server_url` and `remote_server_url` are correct and the servers are accessible.
- **Authentication error**: check the access data (`automation_user` and `automation_secret`) for both servers.
- **Module Error**: Consult the documentation of the `checkmk.general.site` modules: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/plugins/modules/site.py
- **Logs**: Enable detailed logging with `-v` or `-vvv` at the Playbook version to identify errors:
♪
ansible-playbook -i inventory/hosts.ini remote-registration.yml -vvv
♪

## Best Practices
- **Safe storage of Secrets**: Save sensitive data such as `automation_secret` in encrypted variable files (e.g. with `ansible-vault`).
- **Idempotenz**: The playbook is idempotent, i.e. repeated versions do not lead to unexpected changes.
- **Version**: Check the compatibility of Checkmk versions and the Ansible Collection in SUPPORT.md: https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/SUPPORT.md
- **Document**: Keep your variables and configurations well documented to facilitate subsequent changes.

## Integration in CI/CD
To integrate the playbook into a CI/CD pipeline (e.g. with GitHub Actions), create a workflow file:

♪
name: Register Remote Checkmk Site

on:
push:
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
python version: '3.x'
- name: Install dependencies
run:
pip install ansible netaddr
ansible-galaxy collection install checkmk.general
- name: Run Ansible Playbook
env:
ANSIBLE_CENTRAL_AUTOMATION_USER: ${ secrets.CENTRAL_AUTOMATION_USER }
ANSIBLE_CENTRAL_AUTOMATION_SECRET: ${ secrets.CENTRAL_AUTOMATION_SECRET }
ANSIBLE_REMOTE_AUTOMATION_USER: ${ secrets.REMOTE_AUTOMATION_USER }
ANSIBLE_REMOTE_AUTOMATION_SECRET: ${ secrets.REMOTE_AUTOMATION_SECRET }
run:
ansible-playbook -i inventory/hosts.ini remote-registration.yml
♪

Save Secrets in the repository settings of your CI/CD tool.

## Fazite
The `remote-registration.yml`-Playbook automates the registration of a remote checkmk server in a distributed monitoring environment. With the steps described above, you can run it locally or in a CI/CD pipeline. For further details on the modules and options, consult the official documentation: https://github.com/Checkmk/ansible-collection-checkmk.general.
