Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to copy the folder structure from one checkmk instance to another

This HowTo describes how to copy the folder structure from a checkmk instance ( instance 1) to another checkmk instance ( instance 2) by using the `checkmk.general` Ansible Collection. The lookup plugin `checkmk.general.folder` is used to retrieve the folders and their attributes from instance1, and the module `checkmk.general.checkmk_folder` to create these folders in instance2.

## Conditions
- **Ansible**: Installed and configured (compatible with the collection).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk instances**: Access to both checkmk instances (Instanz1 and instance2) with API access.
- **API access data**: username (`automation_user`) and password/secret (`automation_secret`) for the automation API of both instances.
- **Vault (recommended)**: For safe storage of access data (`automation_secret`).
- ** Network access**: Both checkmk servers must be accessible.

Steps

### 1. Retrieve folder structure from instance1
Create a playbook to query the folder structure of instance1. This playbook uses the lookup plugin `checkmk.general.folder` to collect the attributes of all folders.

#### Playbook: `get_folder_structure.yml`
♪
- name: Retrieve the folder structure of instance1
hosts: localhost
tasks:
- name: Sammle all folders of instance1
ansible.builtin.set_fact:
folders: "{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret] }"
loop: "{ instance1_folders }"
vars:
instance1_url: "https://monitoring1.example.com"
instance1_site: "mysite1"
instance1_user: "automation"
instance1_secret: "{ vault_instance1_secret }"
instance1_folders:
- "/"
- "/production_servers"
- "/test_servers"
- "/development"

- name: Show collected folders
ansible.builtin.debug:
msg: "{ folders}"
♪

Explanation
- **Loop**: The list `instance1_folders` contains the paths of the folders to be retrieved (e.g. root folders `/` and subfolders such as `/production_servers`).
- **Lookup plugin**: `checkmk.general.folder` calls the attributes of each folder (e.g. `criticality`, `network_segment`).
- **set_fact** The results are stored in the `folders` variable.
- **Vault**: The `automation_secret` for instance1 is securely stored in a vault variable (`vault_instance1_secret`).

#### Execution
♪
ansible-playbook get_folder_structure.yml --vault-id vault.yml
♪

#### Result
The variable `folders` contains a list of dictionaries with the attributes of all retrieved folders, e.g. B.:
♪
[
{"path": "/", "attributes": {"criticality": "prod"}},
{"path": "/production_servers", "attributes": {"criticality": "prod", "network_segment": "dmz"},
...
]
♪

### 2. Create folder structure in instance2
Create a second playbook to replicate the retrieved folder structure in instance2. The module `checkmk.general.checkmk_folder` is used to create the folders with the same attributes.

#### Playbook: `create_folder_structure.yml`
♪
- name: Create folder structure in instance2
hosts: localhost
tasks:
- name: Create folder in instance2
checkmk.general.checkmk_folder:
server_url: "{{{{2 instance_url }"
site: "{ instance2_site }"
automation_user: "{{{{2 instance_user }"
automation_secret: "{ vault_instance2_secret }"
path: "{ item.path }"
attributes: "{ item.attributes }"
state: present
loop: "{ folders}"
vars:
instance2_url: "https://monitoring2.example.com"
instance2_site: "mysite2"
instance2_user: "automation"
instance2_secret: "{ vault_instance2_secret }"
folders: "{ hostvars['localhost']['folders'] | default([]) }"
♪

Explanation
- **Loop**: Iterated via the list `folders`, which comes from the first playbook.
- **checkmk_folder**: Creates every folder with the path (`path`) and the attributes (`attributes`) from instance1.
- **Vault**: The `automation_secret` for instance2 is securely stored in a vault variable (`vault_instance2_secret`).
- **folders**: The variable `folders` must be available from the first playbook (e.g. by saving in a file or transfer between playbooks).

#### Execution
♪
ansible-playbook create_folder_structure.yml --vault-id vault.yml
♪

#### Result
The folder structure of instance 1 (e.g. `/`, `/production_servers`, `/test_servers`, `/development`) is created in instance 2 with the same attributes.

### 3. Vault for secure access data
Save the access data for both instances securely in a Vault file:

♪
ansible-vault create vault.yml
♪

Content of the `vault.yml`:
♪
vault_instance1_secret: your_geheimer_passwort_instanz1
vault_instance2_secret: your_geheimer_passwort_instanz2
♪

Run the Playbooks with the Vault file:
♪
ansible-playbook get_folder_structure.yml --vault-id vault.yml
ansible-playbook create_folder_structure.yml --vault-id vault.yml
♪

### 4. Combining Playbooks (optional)
To simplify the process, you can combine both steps in a Playbook:

#### Combined playbook: `copy_folder_structure.yml`
♪
- name: Copy the folder structure from instance1 to instance2
hosts: localhost
tasks:
- name: Retrieve the folder structure of instance1
ansible.builtin.set_fact:
folders: "{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret] }"
loop: "{ instance1_folders }"
vars:
instance1_url: "https://monitoring1.example.com"
instance1_site: "mysite1"
instance1_user: "automation"
instance1_secret: "{ vault_instance1_secret }"
instance1_folders:
- "/"
- "/production_servers"
- "/test_servers"
- "/development"

- name: Create folder in instance2
checkmk.general.checkmk_folder:
server_url: "{{{{2 instance_url }"
site: "{ instance2_site }"
automation_user: "{{{{2 instance_user }"
automation_secret: "{ vault_instance2_secret }"
path: "{ item.path }"
attributes: "{ item.attributes }"
state: present
loop: "{ folders}"
vars:
instance2_url: "https://monitoring2.example.com"
instance2_site: "mysite2"
instance2_user: "automation"
instance2_secret: "{ vault_instance2_secret }"
♪

#### Execution
♪
ansible-playbook_folder_structure.yml --vault-id vault.yml
♪

### 5. Error treatment
**Order does not exist**: The lookup plugin gives an error message if a folder in instance1 does not exist. Check the list `instance1_folders`.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct for both instances.
- ** Network problems**: Check whether both servers are accessible and the `server_url` is correct.
- **TLS certificates**: If HTTPS is used, make sure the certificates are valid or setze `validate_certs: false` (only for test environments).

##
- **Ordnerliste**: The list `instance1_folders` must contain the paths of all folders to be copied. You can dynamically expand the list by selecting the Checkmk API directly to find all folders.
- **Attribute**: Not all attributes (e.g. custom tags) are available in each checkmk version. Check the API documentation of your checkmk version.
- **Document**: For more details on modules and plugins, see [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
**Scaling**: For large folder structures, the Playbook can be adjusted to recursively query subfolders (requires additional API queries).

## Fazite
With the `checkmk.general` Ansible Collection you can efficiently copy the folder structure from one checkmk instance to another. This HowTo shows how to replicate folders and their attributes with minimal effort, which is particularly useful for synchronizing monitoring environments.
