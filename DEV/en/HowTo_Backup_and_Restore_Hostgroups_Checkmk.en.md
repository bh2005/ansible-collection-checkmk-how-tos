# How to secure CheckMK host groups into a GIT repository and copy into a new instance

> This document was translated by machine and may contain errors. Please read with caution!


This HowTo describes how host groups from a CheckMK instance (instance1) with the `checkmk.general` secure the ANSIL Collection into a GIT repository and then copied to a new CheckMK instance (instance2). It uses the Lookup plugin `checkmk.general.hostgroups`, to access host group data, save it in a Yaml file and use the module `checkmk.general.checkmk_hostgroup`, to create the host groups in the new instance. The data is used with the module `ansible.builtin.git` secured in a git repository.

## Prerequisites
- **Ansible**: Installed and configured (compatible with the collection).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk instances**: Access to both CheckMK instances (instance1 for backup, instance2 for recovery) with API access.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the automation API of both instances.
- **Git**: Installed on the Ansible controller and a configured git repository (local or remote, e.g. on Github, Gitlab).
- **Vault (recommended)**: For the safe storage of the access data (`automation_secret`).
- - **Dependencies**: Python module `netaddr` on the controller (required for some CheckMK modules, see [Ansible-Collection-Checkmk.General/Roles/Agent/Readme.md](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/roles/agent/README.md)).
- - **SSH key**: For access to a remote git repository (optional, see [Ansible documentary to Known_Hosts](https://docs.ansible.com/ansible/latest/collections/ansible/builtin/known_hosts_module.html)).

## Steps

### 1. Prepare git repository
Set up a GIT repository in which the host group configuration is saved.

#### Local
Create a local repository:
```bash
mkdir checkmk-hostgroups-backup
cd checkmk-hostgroups-backup
git init
```

#### Remote (optional)
If you use a remote repository (e.g. on Github), clone it or add it:
```bash
git clone git@github.com:dein-benutzer/checkmk-hostgroups-backup.git
```
Make sure that the SSH key of the Ansible controller is registered in the repository. Alternatively, you can use HTTPS with username/password or personal access token.

### 2. Secure host groups from instance1
Create a playbook to call up all host groups from instance1 and save it in a Yaml file, which is then taken over to the Git repository.

#### Playbook:`backup_hostgroups.yml` 
```yaml
- name: Backup Checkmk-Hostgruppen in Git
  hosts: localhost
  tasks:
    # Hostgruppen abrufen
    - name: Abrufen aller Hostgruppen aus Instanz1
      ansible.builtin.set_fact:
        hostgroups: "{{ lookup('checkmk.general.hostgroups', server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret) }}" 
      vars:
        instance1_url: "https://monitoring1.example.com" 
        instance1_site: "mysite1" 
        instance1_user: "automation" 
        instance1_secret: "{{ vault_instance1_secret }}" 

    # Hostgruppen in Datei speichern
    - name: Speichere Hostgruppen in Datei
      ansible.builtin.copy:
        content: "{{ hostgroups | to_nice_yaml }}" 
        dest: "{{ backup_dir }}/hostgroups.yml" 
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 

    # Git-Operationen
    - name: Git-Status prüfen
      ansible.builtin.git:
        repo: "{{ git_repo }}" 
        dest: "{{ backup_dir }}" 
        accept_hostkey: true
        version: main
      register: git_status
      vars:
        git_repo: "git@github.com:dein-benutzer/checkmk-hostgroups-backup.git" 
        backup_dir: "./checkmk-hostgroups-backup" 

    - name: Änderungen committen
      ansible.builtin.command:
        cmd: git commit -m "Backup der Checkmk-Hostgruppen vom {{ ansible_date_time.iso8601 }}" 
        chdir: "{{ backup_dir }}" 
      when: git_status.changed
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 

    - name: Änderungen pushen
      ansible.builtin.command:
        cmd: git push origin main
        chdir: "{{ backup_dir }}" 
      when: git_status.changed
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 
```

#### Explanation
- **Lookup plugin**:`checkmk.general.hostgroups` call up all host groups from instance1, including their attributes (e.g.`name`,,`title`).
- **Save**: The host groups are in a Yaml file (`hostgroups.yml`) in the directory `checkmk-hostgroups-backup` saved.
- **Git operations**: The module `ansible.builtin.git` synchronizes the repository and the `ansible.builtin.command`-Tasks führen `git commit` and `git push` from when there are changes.
- **Vault**: The `automation_secret` for instance1, a vault variables (`vault_instance1_secret`) saved.
- **Sample edition**: The file `hostgroups.yml` could look like this:
```yaml
  - name: web_servers
    title: Web Servers
  - name: db_servers
    title: Database Servers
  ```

#### Carry out
```bash
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
```

#### Result
The host groups are in `hostgroups.yml` stored and put into the GIT repository and pushed.

### 3. Restore host groups in instance2
Create a playbook to import the secured host groups from the Yaml file in instance2.

#### Playbook:`restore_hostgroups.yml` 
```yaml
- name: Hostgruppen aus Git in Instanz2 wiederherstellen
  hosts: localhost
  tasks:
    # Repository klonen oder aktualisieren
    - name: Git-Repository klonen oder aktualisieren
      ansible.builtin.git:
        repo: "{{ git_repo }}" 
        dest: "{{ backup_dir }}" 
        accept_hostkey: true
        version: main
      vars:
        git_repo: "git@github.com:dein-benutzer/checkmk-hostgroups-backup.git" 
        backup_dir: "./checkmk-hostgroups-backup" 

    # Hostgruppen aus Datei laden
    - name: Lade Hostgruppen aus YAML-Datei
      ansible.builtin.set_fact:
        hostgroups: "{{ lookup('file', backup_dir + '/hostgroups.yml') | from_yaml }}" 
      vars:
        backup_dir: "./checkmk-hostgroups-backup" 

    # Hostgruppen in Instanz2 erstellen
    - name: Erstelle Hostgruppen in Instanz2
      checkmk.general.checkmk_hostgroup:
        server_url: "{{ instance2_url }}" 
        site: "{{ instance2_site }}" 
        automation_user: "{{ instance2_user }}" 
        automation_secret: "{{ vault_instance2_secret }}" 
        name: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ hostgroups }}" 
      vars:
        instance2_url: "https://monitoring2.example.com" 
        instance2_site: "mysite2" 
        instance2_user: "automation" 
        instance2_secret: "{{ vault_instance2_secret }}" 
```

#### Explanation
- **Git repository**: The module `ansible.builtin.git` clone or updates the repository to `hostgroups.yml`-Datei verfügbar zu machen.
- **Load file**: The Lookup plugin `file` reads the `hostgroups.yml`-Datei und wandelt sie mit `from_yaml` convert to a list of host group dictionaries.
- **Create host groups**: The module `checkmk.general.checkmk_hostgroup` creates each host group in instance2 with the attributes `name` and `title`.
- **Vault**: The `automation_secret` for instance2, a vault variable (`vault_instance2_secret`) saved.

#### Carry out
```bash
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
```

#### Result
The host groups `hostgroups.yml`(e.g.`web_servers`,,`db_servers`) are created in instance2.

### 4. Vault for secure access data
Save the access data safely in a Vault file for both instances:

```bash
ansible-vault create vault.yml
```

Content of the `vault.yml`:
```yaml
vault_instance1_secret: dein_geheimes_passwort_instanz1
vault_instance2_secret: dein_geheimes_passwort_instanz2
```

Perform the playbooks with the Vault file:
```bash
ansible-playbook backup_hostgroups.yml --vault-id vault.yml
ansible-playbook restore_hostgroups.yml --vault-id vault.yml
```

### 5. Error treatment
- **No host groups**: If instance1 does not have any host groups, it is `hostgroups.yml`-Datei leer. Überprüfe die Konfiguration in Instanz1.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct for both instances.
- **Git access**: Check SSH key or HTTPS access data (e.g. Personal Access Token) for GIT errors.
- **File not found**: Make sure that `hostgroups.yml` in the `backup_dir` exists before you perform the restore playbook.
- **TLS certificates**: If HTTPS is used, check the certificates or set `validate_certs: false`(only for test environments).
- **Checkmk version**: Make sure that the collection is compatible with the CheckMK versions of both instances (see `SUPPORT.md`).

## References
- **automation**: Plan the playbooks with a scheduler (e.g. Ansible Tower/AWX or Cron) to carry out regular backups.
- **Expansion**: To secure further configurations (e.g. folders, rules), you can use the Playbook with additional lookup plugins like `checkmk.general.folder` or `checkmk.general.rules` expand.
- **Git repository**: Use a dedicated repository for backups to avoid conflicts. For large files (e.g. for additional backups such as `omd backup`) Check the use of Git LFS.
- - **documentation**: Further details about modules and Lookup plugins can be found in the [Github documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or on Ansible Galaxy.
- **Host group attributes**: The collection currently supports `name` and `title` for host groups. Checkmk-API documentation check for custom attributes.

## Conclusion
With the `checkmk.general` you can efficiently back up host groups from a CheckMK instance and copy them to another instance. This Howto shows how you export host groups to a Yaml file, version it in a GIT repository and restore in a new instance, which is useful for the migration or synchronization of monitoring configurations.