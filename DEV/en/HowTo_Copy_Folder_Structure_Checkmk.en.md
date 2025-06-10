# How to copy the folder structure from one CheckMK instance into another

> This document was translated by machine and may contain errors. Please read with caution!


This HowTo describes how to copy the folder structure from a CheckMK instance (instance1) into another CheckMK instance (instance2) by `checkmk.general` ansible collection used. It will be the lookup plugin `checkmk.general.folder` used to access the folders and their attributes from instance1, and the module `checkmk.general.checkmk_folder` to create these folders in instance2.

## Prerequisites
- **Ansible**: Installed and configured (compatible with the collection).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk instances**: Access to both CheckMK instances (instance1 and instance2) with API access.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the automation API of both instances.
- **Vault (recommended)**: For the safe storage of the access data (`automation_secret`).
- **Network access**: Both CheckMK servers must be accessible.

## Steps

### 1. Call folder structure from instance1
Create a playbook to query the folder structure of instance1. This playbook uses the Lookup plugin `checkmk.general.folder`, to collect the attributes of all folders.

#### Playbook:`get_folder_structure.yml` 
```yaml
- name: Abrufen der Ordnerstruktur von Instanz1
  hosts: localhost
  tasks:
    - name: Sammle alle Ordner von Instanz1
      ansible.builtin.set_fact:
        folders: "{{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret)] }}" 
      loop: "{{ instance1_folders }}" 
      vars:
        instance1_url: "https://monitoring1.example.com" 
        instance1_site: "mysite1" 
        instance1_user: "automation" 
        instance1_secret: "{{ vault_instance1_secret }}" 
        instance1_folders:
          - "/" 
          - "/production_servers" 
          - "/test_servers" 
          - "/development" 

    - name: Zeige gesammelte Ordner an
      ansible.builtin.debug:
        msg: "{{ folders }}" 
```

#### Explanation
- **Loop**: The list `instance1_folders` contains the paths of the folders that are to be called up (e.g. root folder `/` and subfolders like `/production_servers`).
- **Lookup plugin**:`checkmk.general.folder` call the attributes of each folder (e.g.`criticality`,,`network_segment`) away.
- **set_fact**: The results are in the variable `folders` saved.
- **Vault**: The `automation_secret` for instance1, a vault variables (`vault_instance1_secret`) saved.

#### Carry out
```bash
ansible-playbook get_folder_structure.yml --vault-id vault.yml
```

#### Result
The variable `folders` contains a list of dictionaries with the attributes of all folder called, e.g. B.:
```json
[
  {"path": "/", "attributes": {"criticality": "prod"}},
  {"path": "/production_servers", "attributes": {"criticality": "prod", "network_segment": "dmz"}},
  ...
]
```

### 2. Create folder structure in instance2
Create a second Playbook to replicate the folder structure in instance2. The module `checkmk.general.checkmk_folder` is used to create the folders with the same attributes.

#### Playbook:`create_folder_structure.yml` 
```yaml
- name: Erstellen der Ordnerstruktur in Instanz2
  hosts: localhost
  tasks:
    - name: Erstelle Ordner in Instanz2
      checkmk.general.checkmk_folder:
        server_url: "{{ instance2_url }}" 
        site: "{{ instance2_site }}" 
        automation_user: "{{ instance2_user }}" 
        automation_secret: "{{ vault_instance2_secret }}" 
        path: "{{ item.path }}" 
        attributes: "{{ item.attributes }}" 
        state: present
      loop: "{{ folders }}" 
  vars:
    instance2_url: "https://monitoring2.example.com" 
    instance2_site: "mysite2" 
    instance2_user: "automation" 
    instance2_secret: "{{ vault_instance2_secret }}" 
    folders: "{{ hostvars['localhost']['folders'] | default([]) }}" 
```

#### Explanation
- **Loop**: Iterated via the list `folders` that comes from the first playbook.
- **Checkmk_folder**: Create every folder with the path (`path`) and the attributes (`attributes`) from instance1.
- **Vault**: The `automation_secret` for instance2, a vault variable (`vault_instance2_secret`) saved.
- **folder**: The variable `folders` must be available from the first Playbook (e.g. by saving in a file or handover between playbooks).

#### Carry out
```bash
ansible-playbook create_folder_structure.yml --vault-id vault.yml
```

#### Result
The folder structure of instance1 (e.g.`/`,,`/production_servers`,,`/test_servers`,,`/development`) is created in instance2 with the same attributes.

### 3. Vault for safe access data
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
ansible-playbook get_folder_structure.yml --vault-id vault.yml
ansible-playbook create_folder_structure.yml --vault-id vault.yml
```

### 4. Combine the playbooks (optional)
To simplify the process, you can combine both steps in a Playbook:

#### Combined playbook:`copy_folder_structure.yml` 
```yaml
- name: Kopieren der Ordnerstruktur von Instanz1 nach Instanz2
  hosts: localhost
  tasks:
    - name: Abrufen der Ordnerstruktur von Instanz1
      ansible.builtin.set_fact:
        folders: "{{ folders | default([]) + [lookup('checkmk.general.folder', item, server_url=instance1_url, site=instance1_site, automation_user=instance1_user, automation_secret=instance1_secret)] }}" 
      loop: "{{ instance1_folders }}" 
      vars:
        instance1_url: "https://monitoring1.example.com" 
        instance1_site: "mysite1" 
        instance1_user: "automation" 
        instance1_secret: "{{ vault_instance1_secret }}" 
        instance1_folders:
          - "/" 
          - "/production_servers" 
          - "/test_servers" 
          - "/development" 

    - name: Erstellen der Ordner in Instanz2
      checkmk.general.checkmk_folder:
        server_url: "{{ instance2_url }}" 
        site: "{{ instance2_site }}" 
        automation_user: "{{ instance2_user }}" 
        automation_secret: "{{ vault_instance2_secret }}" 
        path: "{{ item.path }}" 
        attributes: "{{ item.attributes }}" 
        state: present
      loop: "{{ folders }}" 
  vars:
    instance2_url: "https://monitoring2.example.com" 
    instance2_site: "mysite2" 
    instance2_user: "automation" 
    instance2_secret: "{{ vault_instance2_secret }}" 
```

#### Carry out
```bash
ansible-playbook copy_folder_structure.yml --vault-id vault.yml
```

### 5. Error treatment
- **Folders do not exist**: The Lookup plugin gives an error message if a folder does not exist in instance1. Check the list `instance1_folders`.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct for both instances.
- **Network problems**: Check whether both servers are available and the `server_url` correct.
- **TLS certificates**: If HTTPS is used, make sure that the certificates are valid or set `validate_certs: false`(only for test environments).

## References
- **Folder list**: The list `instance1_folders` must contain the paths of all folders that are to be copied. You can dynamically expand the list by asking the CheckMK API directly to find all folders.
- **Attributes**: Not all attributes (e.g. custom tags) are available in every CheckMK version. Check the API documentation of your CheckMK version.
- - **documentation**: Further details about modules and plugins can be found in the [Github documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or on Ansible Galaxy.
- **Scaling**: The Playbook can be adjusted for large folder structures to recursively query subfolders (requires additional API queries).

## Conclusion
With the `checkmk.general` ANSIBLE COLLECTION you can efficiently copy the folder structure from a CheckMK instance to another. This Howto shows how you can replicate folders and their attributes with minimal effort, which is particularly useful for the synchronization of monitoring environments.