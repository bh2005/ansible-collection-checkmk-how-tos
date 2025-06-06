Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to automate monitoring configurations with the Checkmk Ansible Collection

This HowTo describes five concrete examples of how the `checkmk.general` Ansible Collection can be used to automate monitoring configurations in Checkmk. The examples include creating folders, rules, users, host groups and using the lookup plugin for folder attributes.

## Conditions
- **Ansible**: Installed and configured (compatible with the collection).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to a running checkmk server with API access.
- **API access data**: username (`automation_user`) and password/secret (`automation_secret`) for the checkmk automation API.
- **Vault (recommended)**: For safe storage of the `automation_secret`.
- **Ordner/Hosts**: Some examples require that certain folders or hosts exist.

## Example 1: Creating a Folder
This example shows how to create a folder in Checkmk to organize hosts.

### Playbook
Create a YAML file (e.g. `create_folder.yml`):

♪
- name: Create a folder for production server
hosts: localhost
tasks:
- name: Create folder
checkmk.general.checkmk_folder:
server_url: "https://monitoring.example.com"
site: "mysite"
automation_user: "automation"
automation_secret: "{ vault_automation_secret }"
path: "/production_servers"
attributes:
criticality: "prod"
network_segment: "dmz"
state: present
♪

### Execution
♪
ansible-playbook create_folder.yml --vault-id vault.yml
♪

### Result
A folder `/production_servers` is created with the attributes `criticality: prod` and `network_segment: dmz`.

## Example 2: Creating a Monitoring Rule
This example defines a rule for the memory monitoring of Linux servers.

### Playbook
Create a YAML file (e.g. `create_rule.yml`):

♪
- name: Set memory monitoring rule for Linux servers
hosts: localhost
tasks:
- name: Create rule
checkmk.general.checkmk_rule:
server_url: "https://monitoring.example.com"
site: "mysite"
automation_user: "automation"
automation_secret: "{ vault_automation_secret }"
ruleset: "memory"
folder: "/linux_servers"
conditions:
host_tags:
os: linux
properties:
Levels:
warning: 80
: 90 critical
state: present
♪

### Execution
♪
ansible-playbook create_rule.yml --vault-id vault.yml
♪

### Result
A rule is created that triggers warnings at 80% and critical alarms at 90% memory usage for Linux servers in the `/linux_servers folder.

## Example 3: User administration with role assignment
This example creates a new user with administrator rights.

### Playbook
Create a YAML file (e.g. `create_user.yml`):

♪
- name: Create a new user with admin rights
hosts: localhost
tasks:
- name: Create user
checkmk.general.checkmk_user:
server_url: "https://monitoring.example.com"
site: "mysite"
automation_user: "automation"
automation_secret: "{ vault_automation_secret }"
username: "jdoe"
fullname: "John Doe"
password: "{ vault_user_password }"
roles:
- admin
contactgroups:
"all_admins"
state: present
♪

### Execution
♪
ansible-playbook create_user.yml --vault-id vault.yml
♪

### Result
A user `jdoe` is created with administrator rights and the contact group `all_admins`.

## Example 4 Creating a Host Group
This example shows how to create a host group to group hosts.

### Playbook
Create a YAML file (e.g. `create_hostgroup.yml`):

♪
- name: Create a web server host group
hosts: localhost
tasks:
- name: Creating host group
checkmk.general.checkmk_hostgroup:
server_url: "https://monitoring.example.com"
site: "mysite"
automation_user: "automation"
automation_secret: "{ vault_automation_secret }"
name: "web_servers"
title: "Web Servers"
state: present
♪

### Execution
♪
ansible-playbook create_hostgroup.yml --vault-id vault.yml
♪

### Result
A host group `web_servers` is created that combines hosts with similar properties (e.g. web server).

## Example 5: Requesting folder attributes
This example shows how to query all attributes of a folder with the lookup plugin.

### Playbook
Create a YAML file (e.g. `show_folder_attributes.yml`):

♪
- name: Show all attributes of a folder
hosts: localhost
tasks:
- name: Request of folder attributes
ansible.builtin.debug:
msg: "{ lookup('checkmk.general.folder', folder_path, server_url='https://monitoring.example.com', site='mysite', automation_user='automation', automation_secret=automation_secret}"
vars:
folder_path: "/production_servers"
automation_secret: "{ vault_automation_secret }"
♪

### Execution
♪
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
♪

### Result
The attributes of the `/production_servers` folder (e.g. `criticality`, `network_segment`) are output in JSON format.

## Vault for secure access data (optional)
For all examples, you can save sensitive data such as `automation_secret` or `vault_user_password` in an Ansible Vault file:

♪
ansible-vault create vault.yml
♪

Content of the `vault.yml`:
♪
vault_automation_secret: your_secret_password
vault_user_password: user_password
♪

Run the Playbooks with the Vault file:
♪
ansible-playbook <playbook>.yml --vault-id vault.yml
♪

##
- **Error treatment**: Ensure that the checkmk server is accessible, the access data is correct and the specified folders/hosts exist.
- **Document**: For more details on modules and options, see the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- **TLS**: If your server uses HTTPS, check the certificate check (if applicable, add `validate_certs: false` if there is no valid certificate – only for test environments).
- **Checkmk version**: Make sure the checkmk version used is compatible with the collection (see `SUPPORT.md`).

## Fazite
The `checkmk.general` Collection offers powerful tools for automating checkmk configurations. With these examples you can efficiently manage and customize folders, rules, users, host groups and more.
