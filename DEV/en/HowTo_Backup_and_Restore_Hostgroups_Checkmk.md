Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to secure checkmk host groups in a Git repository and copied into a new instance

This HowTo describes how to secure host groups from a checkmk instance ( instance 1) with the `checkmk.general` Ansible Collection into a Git repository and then copied into a new checkmk instance ( instance 2). It uses the lookup plugin `checkmk.general.hostgroups` to retrieve host group data, stores it in a YAML file and uses the module `checkmk.general.checkmk_hostgroup` to create host groups in the new instance. The data is saved with the `ansible.builtin.git` module into a Git repository.

## Conditions
- **Ansible**: Installed and configured (compatible with the collection).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk instances**: Access to both checkmk instances (Instanz1 for backup, instance2 for recovery) with API access.
- **API access data**: username (`automation_user`) and password/secret (`automation_secret`) for the automation API of both instances.
- **Git**: Installed on the Ansible controller and a configured Git repository (local or remote, e.g. on GitHub, GitLab).
- **Vault (recommended)**: For safe storage of access data (`automation_secret`).
- ** Dependencies**: Python module `netaddr` on the controller (for some checkmk modules required, see [ansible-collection-checkmk.general/roles/agent/README.md](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/roles/agent/REd).
- **SSH keys**: For access to a remote git repository (optional, see [Ansible Documentation to known_hosts](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/known_hosts_module.html).

Steps

### 1. Prepare Git repository
Set up a Git repository in which the host group configuration is stored.

#### Local

Create a local repository:
♪
mkdir checkmk-hostgroups-backup
cd checkmk-hostgroups-backup
git init
♪

#### Remote (optional)
If you use a remote repository (e.g. on GitHub), you can or add it:
♪
git clone git@github.com:dein-user/checkmk-hostgroups-backup.git
♪
Make sure the SSH key of the Ansible controller is registered in the repository. Alternatively, you can use HTTPS with username/password or a Personal Access token.

### 2. Secure host groups from instance1
Create a playbook to retrieve all host groups from instance1 and store them in a YAML file, which is then transferred to the Git repository.

#### Playbook: `backup_hostgroups.yml`
♪
- name: Backup Checkmk host groups in Git
hosts: localhost
tasks:
# Call host groups
- name: Retrieve all host groups from instance1
ansible.builtin.set_fact:
hostgroups: "{ lookup('checkmk.general.hostgroups', server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret}"
vars:
instance1_url: "https://monitoring1.example.com"
instance1_site: "mysite1"
instance1_user: "automation"
instance1_secret: "{ vault_instance1_secret }"

# Save host groups to file
- name: Save host groups in file
ansible.builtin.copy:
content: "{ hostgroups | to_nice_yaml }"
dest: "{ backup_dir }/hostgroups.yml"
vars:
backup_dir: "./checkmk-hostgroups-backup"

# Git operations
- name: Git status check
ansible.builtin.git:
repo: "{ git_repo }"
dest: "{ backup_dir }"
accept_hostkey: true
version: main
register: git_status
vars:
git_repo: "git@github.com:dein-user/checkmk-hostgroups-backup.git"
backup_dir: "./checkmk-hostgroups-backup"

- name: Change committen
ansible.builtin.command:

cmd: git commit -m "Backup der Checkmk-Hostgruppen vom {{ ansible_date_time.iso8601 }"
chdir: "{ backup_dir }"
when: git_status.changed
vars:
backup_dir: "./checkmk-hostgroups-backup"

- name: Pressing changes
ansible.builtin.command:
cmd: git push original main
chdir: "{ backup_dir }"
when: git_status.changed
vars:
backup_dir: "./checkmk-hostgroups-backup"
♪

Explanation
- **Lookup plugin**: `checkmk.general.hostgroups` calls all host groups from instance1, including their attributes (e.g. `name`, `title`).
**Save**: The host groups are stored in a YAML file (`hostgroups.yml`) in the directory `checkmk-hostgroups-backup`.
- **Git-Operations**: The module `ansible.builtin.git` synchronizes the repository, and the `ansible.builtin.command`-Tasks perform `git commit` and `git push` when there are changes.
- **Vault**: The `automation_secret` for instance1 is securely stored in a vault variable (`vault_instance1_secret`).
- **Example output**: The file `hostgroups.yml` could look like this:
♪
- name: web_servers
title: Web Servers
- name: db_servers
title: Database Servers
♪

#### Execution
♪
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
♪

#### Result
The host groups are stored in `hostgroups.yml` and merged into the Git repository and flushed.

### 3. Restore host groups in instance2
Create a playbook to import the secured host groups from the YAML file in instance2.

#### Playbook: `restore_hostgroups.yml`
♪
- name: Restore Git host groups in instance2
hosts: localhost
tasks:
# Clon or update repository
- name: Git-Repository clone or update
ansible.builtin.git:
repo: "{ git_repo }"
dest: "{ backup_dir }"
accept_hostkey: true
version: main
vars:

git_repo: "git@github.com:dein-user/checkmk-hostgroups-backup.git"
backup_dir: "./checkmk-hostgroups-backup"

# Load host groups from file
- name: Load host groups from YAML file
ansible.builtin.set_fact:
hostgroups: "{ lookup('file', backup_dir + '/hostgroups.yml') | from_yaml }"
vars:
backup_dir: "./checkmk-hostgroups-backup"

# Create host groups in instance2
- name: Create host groups in instance2
checkmk.general.checkmk_hostgroup:
server_url: "{{{{2 instance_url }"
site: "{ instance2_site }"
automation_user: "{{{{2 instance_user }"
automation_secret: "{ vault_instance2_secret }"
name: "{ item.name }"
title: "{ item.title }"
state: present
loop: "{ hostgroups }"
vars:
instance2_url: "https://monitoring2.example.com"
instance2_site: "mysite2"
instance2_user: "automation"
instance2_secret: "{ vault_instance2_secret }"
♪

Explanation
- **Git-Repository**: The module `ansible.builtin.git` clones or updates the repository to make the `hostgroups.yml` file available.
- **File Load**: The Lookup plugin `file` reads the `hostgroups.yml` file and converts it with `from_yaml` into a list of host group detectionaries.
- **Create host groups**: The module `checkmk.general.checkmk_hostgroup` creates each host group in instance2 with the attributes `name` and `title`.
- **Vault**: The `automation_secret` for instance2 is securely stored in a vault variable (`vault_instance2_secret`).

#### Execution
♪
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
♪

#### Result
The host groups from `hostgroups.yml` (e.g. `web_servers`, `db_servers`) are created in instance2.

### 4. Vault for secure access data
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
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
♪

### 5. Error treatment
- **No host groups**: If instance1 has no host groups, the `hostgroups.yml` file is empty. Check the configuration in instance1.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct for both instances.
- **Git access**: Check SSH keys or HTTPS access data (e.g. Personal Access Tokens) for Git errors.
- **File not found**: Make sure that `hostgroups.yml` exists in `backup_dir` before you execute the Restore Playbook.
- **TLS certificates**: If HTTPS is used, check the certificates or setze `validate_certs: false` (only for test environments).
- **Checkmk version**: Make sure the collection is compatible with the checkmk versions of both instances (see `SUPPORT.md`).

##
- **Automatization**: Plan the playbooks with a scheduler (e.g. Ansible Tower/AWX or Cron) to perform regular backups.
- **Extension**: To secure further configurations (e.g. folders, rules), you can extend the Playbook with additional lookup plugins such as `checkmk.general.folder` or `checkmk.general.rules`.
- **Git-Repository**: Use a dedicated repository for backups to avoid conflicts. For large files (e.g. for additional backups such as `omd backup`) check the use of Git LFS.
- **Document**: For more details on modules and lookup plugins, see the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.

**Host group attributes**: The collection currently supports `name` and `title` for host groups. For custom attributes check the checkmk API documentation.

## Fazite
With the `checkmk.general` Ansible Collection you can efficiently secure host groups from a checkmk instance and copy them to another instance. This HowTo shows how to export host groups to a YAML file, to a Git repository version and to a new instance, which is useful for migration or synchronization of monitoring configurations.