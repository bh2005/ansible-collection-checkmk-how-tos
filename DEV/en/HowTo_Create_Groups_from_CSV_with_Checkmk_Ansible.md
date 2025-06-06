Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to create host and service groups in Checkmk from a CSV file with the Ansible Collection

This HowTo describes how to customize the Playbook `groups.yml` from the repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/groups.yml) to create host and service groups in Checkmk based on a CSV. It uses the `checkmk.general` Ansible Collection to create host groups (`checkmk.general.checkmk_hostgroup`) and service groups (`checkmk.general.checkmk_servicegroup`), as well as the module `community.general.read_csv` to read the group information from a CSV file. In addition, hosts can be dynamically assigned to a host group, based on tags or other criteria.

## Conditions
- **Ansible**: Installed and configured (compatible with the collections).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **community.general Collection**: Installed via `ansible-galaxy install community.general` (for the `read_csv` module).
- **Checkmk server**: Access to a checkmk instance with activated web API.
- **API access data**: Username (`automation_user`) and Password/Secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For safe storage of the `automation_secret`.
- ** Network access**: The Ansible controller must be able to reach the checkmk server via HTTP/HTTPS.
- **Hosts**: The hosts mentioned in the Playbook (e.g. with the tag `os: linux`) must exist in the Checkmk instance.
- **CSV file**: A CSV file with the group information read in the Playbook.

Prepare CSV file
Create a CSV file (e.g. `groups.csv`) that defines the host and service groups. The file should contain at least the following columns:
- `type`: group type (`hostgroup` or `servicegroup`).
- `name`: name of group (e.g. `web_servers`).
- `title`: Display name of the group (e.g. `Web Servers`).

**Example for `groups.cs v`**:
♪
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
♪

Save the file in the same directory as the Playbook or adjust the path in the Playbook.

Steps

### 1. Create or customize Playbook
Create a new playbook (e.g. `create_groups_from_csv.yml`) or customize the original `groups.yml` to read the groups from the CSV file.

**Playbook: `create_groups_from_csv.yml`**:
♪
- hosts: localhost
to be:
vars:
server_url: "https://monitoring.example.com"
site: "mysite"
automation_user: "automation"
automation_secret: "{ vault_automation_secret }"
csv_file: "groups.csv"
tasks:
# Read CSV file
- name: Read groups from CSV file
community.general.read_csv:
path: "{ csv_file }"
key: name
register: groups_data

# Create host groups
- name: Create host groups from CSV
checkmk.general.checkmk_hostgroup:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
name: "{ item.name }"
title: "{ item.title }"
state: present
loop: "{ groups_data.list | selectattr('type', 'equalto', 'hostgroup')

# Create service groups
- name: Create service groups from CSV
checkmk.general.checkmk_servicegroup:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
name: "{ item.name }"
title: "{ item.title }"
state: present
loop: "{ groups_data.list | selectattr('type', 'equalto', 'servicegroup')

# assign hosts to a host group (e.g. web_servers for Linux hosts)
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
- "web_servers"
state: present
loop: "{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret_secret}"
♪

Explanation
- **CSV-read**: The module `community.general.read_csv` reads the file `groups.csv` and stores the data in `groups_data`. The `key: name` option ensures that each line is indexed by the `name` field.
- **Create host groups** The task filters entries with `type: hostgroup` and creates host groups with the specified `name` and `title` values.
- **Create service groups**: The task filters entries with `type: servicegroup` and creates service groups.
- **Hostzuweisung**: hosts with the tag `os: linux` are assigned to the host group `web_servers`. Customize the group name (`web_servers`) or the query (`{'host_tags': {'os': 'linux'}`) to your needs.
- **Vault**: The `automation_secret` is safely stored in a Vault variable.

### 2. Customize variables
Adjust the variables in the Playbook to your environment:
- **server_url**: Replace your checkmk server URL (e.g. `https://monitoring.example.com`).
- **site**: Replace by the name of your checkmk site.
- **automation_user**: Use the username for the automation API (e.g. `automation`).
- **automation_secret**: Use the Vault variable (e.g. `{ vault_automation_secret }`).
- **csv_file**: Make sure the path to the CSV file is correct (e.g. `groups.csv` in the same directory as the Playbook).
- **query**: Customize the query in the lookup plugin to filter the desired hosts (e.g. `{"host_labels": {"env": "prod"}`).

#### Create Vault file
♪
ansible-vault create vault.yml
♪

Content of the `vault.yml`:
♪
vault_automation_secret: your_secret_password
♪

### 3. Provide CSV file
Create the `groups.csv` file in the same directory as the Playbook or adjust the path in the `csv_file` variable. Example content:
♪
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
♪

### 4. Run Playbook
Run the Playbook to create the groups and assign hosts:

♪
ansible-playbook create_groups_from_csv.yml --vault-id vault.yml
♪

### 5. Playbook tasks
The Playbook performs three main tasks:
1. **Read the CSV file**:
- Read the `groups.csv` file and saves the data in `groups_data`.
2. **Creating host groups**:
- Creates host groups (e.g. `web_servers`, `db_servers`) based on the CSV entries with `type: hostgroup`.
3. **Developing service groups**:
- Creates service groups (e.g. `http_services`, `database_services`) based on the CSV entries with `type: servicegroup`.
4. **Dynamic allocation of hosts to a host group**:
- Weist hosts with the tag `os: linux` to the host group `web_servers` (adjustable).

### 6. Enable changes
After running the Playbook, the changes in Checkmk must be activated as the allocation of hosts to a host group changes the configuration:
1. Log in to the Checkmk web interface.
Two. Go to **Setup > Activate Changes** and activate the pending changes.
3. Alternatively, activate the changes via the Checkmk API:
♪
curl -X POST "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/activation_run/actions/activate-changes/invoke"
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

### 7. Check the results
After running the Playbook:
1. Log in to the Checkmk web interface and navigate to:
- **Setup > Hosts > Host groups** to check the created host groups (e.g. `web_servers`, `db_servers`).
- **Setup > Services > Service groups** to check the service groups created (e.g. `http_services`, `database_services`).
Two. Check the host assignment:
- Go to **Monitor > All hosts**, select a host from the list (e.g. by tag `os: linux`) and check under **Properties > Host groups** whether `web_servers` is assigned.
3. Alternatively, check the groups via the Checkmk API:
♪
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_group_config/collections/all"
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

### 8. Error handling
- **CSV file not found**: Make sure that `groups.csv` exists and the path in `csv_file` is correct.
- **Invalid CSV format**: Check if the CSV file contains the required columns (`type`, `name`, `title`) and is formatted correctly.
- **Hostgroup/Servicegroup already exists**: If a group already exists, the module ignores creation (idempotent behavior). Set `state: absent` to delete existing groups.
- **Hosts not found**: If the query in the lookup plugin does not return hosts (e.g. because no host has the tag `os: linux`), the task will skip the assignment. Check the query (`query`) and host tags in Checkmk.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- ** Network problems**: Check the availability of the checkmk server (`server_url`) and the correct port release (HTTP/HTTPS).
- **TLS certificates**: For HTTPS, make sure the certificate is valid, or setze `validate_certs: false` in the Playbook (only for test environments).
- **Checkmk version**: Make sure the collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).

### 9. Adaptations and extensions
- **Advanced CSV attributes**: Add further columns to the CSV file (e.g. `description` or custom attributes), if future checkmk versions support them.
- **Dynamic queries**: Apply the query in the lookup plugin to use other criteria (e.g. `{"host_labels": {"env": "prod"}` or `{"folder": "/production"}`).
- **Service Group allocation**: To assign services to a service group, you can use the `checkmk.general.checkmk_service` module (not included in the demo playbook, but available in the collection).
- **Remove groups**: Set `state: absent` in the tasks to delete existing host or service groups.
- **Automatization**: Plan the playbook with a scheduler (e.g. Ansible Tower/AWX or Cron) to update groups regularly.
- **Advanced CSV structure**: You can extend the CSV file to also define assignment rules (e.g. a column `host_tags` for the dynamic allocation of hosts).

##
- **Safety**: Always use a Vault file for the 'automation_secret' to protect sensitive data.
- **Checkmk version**: Make sure the `checkmk.general` Collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).
- **Document**: For more details on modules and lookup plugins, see the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- **Test environment**: Test the playbook in a non-productive environment to avoid unexpected effects.
- **CSV format**: Ensure that the CSV file is correctly formatted (e.g. no missing columns or invalid characters).
- Change activation**: After assigning hosts to a host group, changes in Checkmk must be activated either manually or via the API.

## Fazite
The customized Playbook `create_groups_from_csv.yml` allows to create host and service groups in Checkmk based on a CSV file and dynamically assign hosts to a host group. With the `checkmk.general` Collection and the `community.general.read_csv` module, you can automate group management flexibly and scalable, which is particularly useful for managing monitoring objects in large environments. By adjusting the CSV file and queries, you can adjust the Playbook to your specific requirements.
