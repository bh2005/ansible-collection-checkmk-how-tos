Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to create folders and hosts in Checkmk from a CSV file with the Ansible Collection

This HowTo describes how to customize the Playbook `hosts-and-folders.yml` from the repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/hosts-and-folders.yml) based in checkmk It uses the `checkmk.general` Ansible Collection to create folders (`checkmk.general.folder`) and hosts (`checkmk.general.checkmk_host`), as well as the module `community.general.read_csv` to read the information from a CSV file. Additionally, hosts can be created dynamically based on a query.

## Conditions
- **Ansible**: Installed and configured (compatible with the collections).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **community.general Collection**: Installed via `ansible-galaxy install community.general` (for the `read_csv` module).
- **Checkmk server**: Access to a checkmk instance with activated web API.
- **API access data**: Username (`automation_user`) and Password/Secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For safe storage of the `automation_secret`.
- ** Network access**: The Ansible controller must be able to reach the checkmk server via HTTP/HTTPS.
- **CSV file**: A CSV file with the folder and host information read in the Playbook.

Prepare CSV file
Create a CSV file (e.g. `hosts_and_folders.csv`) that defines the folders and hosts. The file should contain the following columns:
- `type`: type of entry (`folder` or `host`).
- `name`: name of folder (e.g. `/my_folder`) or hosts (e.g. `myhost1.local`).
- `title`: Display name of the folder (e.g. `My Folder`) or alias of the host (e.g. `My Host 1`).

- `folder` (only for hosts): folder path where the host is created (e.g. `/my_folder` or `/` for root).
- `ipaddress` (optional, only for hosts): IP address of the host (e.g. `192.168.1.100`).
- `tag_os` (optional, only for hosts): Host tag for operating system (e.g. `linux`).
- `labels` (optional, only for hosts): JSON format for labels (e.g. `{'env': "prod"}`).

**Example for `hosts_and_folders.cs v`**:
♪
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,
folder,/prod_servers,Production Servers,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
♪

Save the file in the same directory as the Playbook or adjust the path in the Playbook.

Steps

### 1. Create or customize Playbook
Create a new playbook (e.g. `create_hosts_and_folders_from_csv.yml`) or customize the original `hosts-and-folders.yml` to read the folders and hosts from the CSV file.

**Playbook: `create_hosts_and_folders_from_csv.yml`**:
♪
- hosts: localhost
to be:
vars:
server_url: "https://monitoring.example.com"
site: "mysite"
automation_user: "automation"
automation_secret: "{ vault_automation_secret }"
csv_file: "hosts_and_folders.csv"
tasks:
# Read CSV file
- name: Read folders and hosts from CSV file
community.general.read_csv:
path: "{ csv_file }"
key: name
register: csv_data

# Create folder
- name: Create folders from CSV
checkmk.general.folder:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
path: "{ item.name }"
title: "{ item.title }"
state: present
loop: "{ csv_data.list | selectattr('type, 'equalto', 'folder') | list }"

# Create hosts

- name: Create hosts from CSV
checkmk.general.checkmk_host:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
name: "{ item.name }"
folder: "{ item.folder | default('/') }"
attributes:
alias: "{ item.title }"
ipaddress: "{ item.ipaddress | default(omit) }"
tag_os: "{ item.tag_os | default(omit) }"
labels: "{ item.labels | default({}) | from_json }"
state: present
loop: "{ csv_data.list | selectattr('type, 'equalto', 'host') } list }"

# Create Dynamic Hosts (Example)
- name: Create dynamic hosts from query
checkmk.general.checkmk_host:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
name: "ansible-{ item }-{ 1000 | random }"
folder: "/my_folder"
attributes:
tag_os: linux
labels:
source: ansible
state: present
loop: "{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret_secret}"
♪

Explanation
- **CSV-read**: The module `community.general.read_csv` reads the file `hosts_and_folders.csv` and stores the data in `csv_data`. The `key: name` option indicates each line after the `name` field.
**Create folders**: The task filters entries with `type: folder` and creates folders with the specified `path` and `title` values.
- Create **Hosts** The task filters entries with `type: host` and creates hosts with the specified attributes (`alias`, `ipaddress`, `tag_os`, `labels`). The `folder` value determines the target folder, by default `/` (root).

- **Dynamic host creation**: The last task remains similar to the original, but creates hosts based on a query (e.g. `os: linux`) with a random suffix in the name.
- **Vault**: The `automation_secret` is safely stored in a Vault variable.

### 2. Customize variables
Adjust the variables in the Playbook to your environment:
- **server_url**: Replace your checkmk server URL (e.g. `https://monitoring.example.com`).
- **site**: Replace by the name of your checkmk site.
- **automation_user**: Use the username for the automation API (e.g. `automation`).
- **automation_secret**: Use the Vault variable (e.g. `{ vault_automation_secret }`).
- **csv_file**: Make sure the path to the CSV file is correct (e.g. `hosts_and_folders.csv` in the same directory as the Playbook).
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
Create the `hosts_and_folders.csv` file in the same directory as the Playbook or adjust the path in the `csv_file` variable. Example content:
♪
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,
folder,/prod_servers,Production Servers,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
♪

### 4. Run Playbook
Run the Playbook to create folders and hosts:

♪
ansible-playbook create_hosts_and_folders_from_csv.yml --vault-id vault.yml
♪

### 5. Playbook tasks
The Playbook performs three main tasks:
1. **Read the CSV file**:
- Read the `hosts_and_folders.csv` file and saves the data in `csv_data`.

2. **Creating folders**:
- Creates folder (e.g. `/my_folder`, `/prod_servers`) based on the CSV entries with `type: folder`.
3. **Creating Hosts**:
- Creates hosts (e.g. `myhost1.local`, `myhost2.local`) based on the CSV entries with `type: host`, with the specified attributes and folder assignments.
4. **Dynamic host creation**:
- Creates hosts based on a query (e.g. `os: linux`) with a random suffix and assigns them to the folder `/my_folder`.

### 6. Enable changes
After running the Playbook, the changes in Checkmk must be activated as adding folders and hosts changes the configuration:
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
- **Setup > Hosts > Folders** to check the created folders (e.g. `/my_folder`, `/prod_servers`).
- **Monitor > All hosts** to check the created hosts (e.g. `myhost1.local`, `myhost2.local`).
Two. Check the host details:
- Select a host and check **Properties** if the attributes (`alias`, `ipaddress`, `tag_os`, `labels`) are set correctly.
- Check the folder under **Host > Folder**.
3. Alternatively, check folders and hosts using the Checkmk API:
♪
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/folder_config/collections/all"
-H "Authorization: Bearer automation dein_geheimer_passwort" \

-H "Accept: application/json"
♪
♪
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_config/collections/all"
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

### 8. Error handling
- **CSV file not found**: Make sure that `hosts_and_folders.csv` exists and the path in `csv_file` is correct.
- **Invalid CSV format**: Check if the CSV file contains the required columns (`type`, `name`, `title`) and is formatted correctly. JSON data in `labels` must be valid.
- **Ordner/Host already exists**: If a folder or host already exists, the module ignores creation (idempotent behavior). Set `state: absent` to delete existing objects.
- **Hosts not found**: If the query in the lookup plugin does not return hosts (e.g. because no host has the tag `os: linux`), the task skips the creation. Check the query (`query`) and host tags in Checkmk.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- ** Network problems**: Check the availability of the checkmk server (`server_url`) and the correct port release (HTTP/HTTPS).
- **TLS certificates**: For HTTPS, make sure the certificate is valid, or setze `validate_certs: false` in the Playbook (only for test environments).
- **Checkmk version**: Make sure the collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).

### 9. Adaptations and extensions
- **Advanced CSV attributes**: Add more columns to the CSV file (e.g. more tags or custom attributes) if future checkmk versions support them.
- **Dynamic queries**: Apply the query in the lookup plugin to use other criteria (e.g. `{"host_labels": {"env": "prod"}` or `{"folder": "/production"}`).

- **Host deletion**: Set `state: absent` in the host tasks to remove existing hosts.
- **Ordner hierarchies**: Create nested folders by defining paths like `/parent/child` in the CSV file.
- **Automatization**: Plan the playbook with a scheduler (e.g. Ansible Tower/AWX or Cron) to regularly update folders and hosts.
- **Advanced CSV structure**: You can expand the CSV file to define additional configurations such as group assignments or downtimes.

##
- **Safety**: Always use a Vault file for the 'automation_secret' to protect sensitive data.
- **Checkmk version**: Make sure the `checkmk.general` Collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).
- **Document**: For more details on modules and lookup plugins, see the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- **Test environment**: Test the playbook in a non-productive environment to avoid unexpected effects.
- **CSV format**: Make sure that the CSV file is correctly formatted (e.g. no missing columns or invalid JSON data in `labels`).
- Change activation**: After adding folders and hosts, changes in Checkmk must be activated either manually or via the API.

## Fazite
The customised Playbook `create_hosts_and_folders_from_csv.yml` allows to create folders and hosts in Checkmk based on a CSV file and dynamically configure hosts. With the `checkmk.general` Collection and the `community.general.read_csv` module, you can automate the management of monitoring hierarchies flexibly and scalably, which is particularly useful for organizing hosts in large environments. By adjusting the CSV file and queries, you can adjust the Playbook to your specific requirements.