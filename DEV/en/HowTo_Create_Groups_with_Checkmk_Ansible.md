Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to create host and service groups in Checkmk with the Ansible Collection

This HowTo describes how to use the Playbook `groups.yml` from the repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/groups.yml) to create host and service groups in checkmk group dynamically. The Playbook uses the `checkmk.general` Ansible Collection to create a host group (`my_hostgroup`) and a service group (`my_servicegroup`), as well as to assign hosts based on tags (e.g. `os: linux`) to a host group.

## Conditions
- **Ansible**: Installed and configured (compatible with the collection).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to a checkmk instance with activated web API.
- **API access data**: Username (`automation_user`) and Password/Secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For safe storage of the `automation_secret`.
- ** Network access**: The Ansible controller must be able to reach the checkmk server via HTTP/HTTPS.
- **Hosts**: The hosts mentioned in the Playbook (e.g. with the tag `os: linux`) must exist in the Checkmk instance.

Steps

### 1. Download Playbook
Clone the repository or copy the Playbook `groups.yml` on your Ansible controller:

♪
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
cd ansible-collection-checkmk.general/playbooks/demo
♪

The Playbook looks as follows (excerpt to overview):
♪
- hosts: localhost
to be:
vars:
server_url: "http://localhost"
site: "mysite"
automation_user: "automation"
automation_secret: "mysecret"
tasks:
- name: Create a host group
checkmk.general.checkmk_hostgroup:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
name: "my_hostgroup"
title: "My Hostgroup"
state: present
- name: Create a service group
checkmk.general.checkmk_servicegroup:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
name: "my_servicegroup"
title: "My Servicegroup"
state: present
- name: Add hosts to a host group
checkmk.general.checkmk_host:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
name: "{ item }"
attributes:
groups:
host:
- "my_hostgroup"
state: present
loop: "{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret_secret}"
♪

### 2. Customize variables
Adjust the variables in the Playbook to your environment:
- **server_url**: Replace `http://localhost` by the URL of your checkmk server (e.g. `https://monitoring.example.com`).
- **site**: Replace `mysite` by the name of your checkmk site.
- **automation_user**: Use the username for the automation API (e.g. `automation`).
- **automation_secret**: Replace `mysecret` by the API password or token.
- **name/title**: Customize the names (`my_hostgroup`, `my_servicegroup`) and title (`My Hostgroup`, `My Servicegroup`) to your desired group names.
- **query**: Customize the query in the lookup plugin to filter the desired hosts (e.g. `{"host_tags": {"os": "linux"}` for Linux hosts or `{"host_labels": {"env": "prod"}` for production environments).

**Recommendation**: Save the `automation_secret` in an Ansible Vault file to increase security.

#### Create Vault file
♪
ansible-vault create vault.yml
♪

Content of the `vault.yml`:
♪
vault_automation_secret: your_secret_password
♪

Edit the Playbook to use the Vault variable:
♪
automation_secret: "{ vault_automation_secret }"
♪

### 3. Run playbook
Run the Playbook to create the host and service groups and assign hosts:

♪
ansible-playbook groups.yml --vault-id vault.yml
♪

### 4. Playbook tasks
The Playbook performs three tasks:
1. **Creating a host group**:
- Creates a host group called `my_hostgroup` and the title `My Hostgroup`.
2. **Creating a service group**:
- Creates a service group called `my_servicegroup` and the title `My Servicegroup`.
3. **Dynamic allocation of hosts to a host group**:
- Calls all hosts with the tag `os: linux` over the lookup plugin `checkmk.general.host`.
- Update the host attributes to assign the hosts to the host group `my_hostgroup`.

### 5. Enable changes
After running the Playbook, the changes in Checkmk must be activated as the allocation of hosts to a host group changes the configuration:
1. Log in to the Checkmk web interface.
Two. Go to **Setup > Activate Changes** and activate the pending changes.
3. Alternatively, activate the changes via the Checkmk API:
♪
curl -X POST "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/activation_run/actions/activate-changes/invoke"
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

### 6. Check the results
After running the Playbook:
1. Log in to the Checkmk web interface and navigate to:
- **Setup > Hosts > Host groups** to check the host group `my_hostgroup`.
- **Setup > Services > Service groups** to check the service group `my_servicegroup`.
Two. Check the host assignment:
- Go to **Monitor > All hosts**, select a host from the list (e.g. by tag `os: linux`) and check under **Properties > Host groups** whether `my_hostgroup` is assigned.
3. Alternatively, check the groups via the Checkmk API:
♪
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_group_config/collections/all"
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

### 7. Error handling
- **Hostgroup/Servicegroup already exists**: If `my_hostgroup` or `my_servicegroup` already exist, the module ignores creation (idempotent behavior). Set `state: absent` to delete existing groups.
- **Hosts not found**: If the query in the lookup plugin does not return hosts (e.g. because no host has the tag `os: linux`), the task will skip the assignment. Check the query (`query`) and host tags in Checkmk.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- ** Network problems**: Check the availability of the checkmk server (`server_url`) and the correct port release (HTTP/HTTPS).
- **TLS certificates**: For HTTPS, make sure the certificate is valid, or setze `validate_certs: false` in the Playbook (only for test environments).
- **Checkmk version**: Make sure the collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).

### 8. Adaptations and extensions
- **Other group names**: Change `name` and `title` for host and service groups to suit your requirements (e.g. `web_servers`, `database_services`).
- **Dynamic queries**: Apply the query in the lookup plugin to use other criteria (e.g. `{"host_labels": {"env": "prod"}` or `{"folder": "/production"}`).
- **Service Group allocation**: To assign services to a service group, you can use the `checkmk.general.checkmk_service` module (not included in the demo playbook, but available in the collection).
- **Remove groups**: Set `state: absent` in the tasks to delete existing host or service groups.
- **Automatization**: Plan the playbook with a scheduler (e.g. Ansible Tower/AWX or Cron) to update groups regularly.

##
- **Safety**: Always use a Vault file for the 'automation_secret' to protect sensitive data.
- **Checkmk version**: Make sure the `checkmk.general` Collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).
- **Document**: For more details on modules and lookup plugins, see the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- **Test environment**: Test the playbook in a non-productive environment to avoid unexpected effects.
- **Examples**: The Playbook uses placeholders (`http://localhost`, `my_hostgroup`). Customize this to your actual environment.
- Change activation**: After assigning hosts to a host group, changes in Checkmk must be activated either manually or via the API.

## Fazite
The Playbook `groups.yml` offers a simple way to create host and service groups in Checkmk and dynamically assign hosts to a host group. With the `checkmk.general` Collection you can efficiently automate group management, which is particularly useful for organizing monitoring objects in large environments. By adjusting the variables and queries, you can adjust the Playbook to your specific requirements.
