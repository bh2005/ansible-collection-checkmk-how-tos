# How to create folders and hosts in Checkmk from a CSV file with the Ansible Collection

> This document was translated by machine and may contain errors. Please read with caution!


This HowTo describes how to `hosts-and-folders.yml` from the repository [Checkmk/Ansible-Collection-Checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/hosts-and-folders.yml) adjust to create folders and hosts in Checkmk based on a CSV file. It uses the `checkmk.general` ansible collection to folder (`checkmk.general.folder`) and hosts (`checkmk.general.checkmk_host`) to create, as well as the module `community.general.read_csv` to read the information from a CSV file. In addition, hosts can be created dynamically based on a query.

## Prerequisites
- **Ansible**: Installed and configured (compatible with the collections).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Community.General Collection**: Installed via `ansible-galaxy collection install community.general`(for the `read_csv`-Modul).
- **Checkmk server**: Access to a CheckMK instance with activated web API.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For the safe storage of the `automation_secret`.
- **Network access**: The Ansible controller must be able to reach the CheckMK server via HTTP/HTTPS.
- **CSV file**: A CSV file with the folder and host information that is read in the Playbook.

## Prepare CSV file
Create a CSV file (e.g.`hosts_and_folders.csv`) that defines the folders and hosts. The file should contain the following columns:
- `type`: Type of entry (`folder` or `host`).
- `name`: Name of the folder (e.g.`/my_folder`) or hosts (e.g. B.`myhost1.local`).
- `title`: Advertisements of the folder (e.g.`My Folder`) or alias of the host (e.g.`My Host 1`).
- `folder`(only for hosts): folder path in which the host is created (e.g.`/my_folder` or `/` for root).
- `ipaddress`(Optional, only for hosts): IP address of the host (e.g.`192.168.1.100`).
- `tag_os`(Optional, only for hosts): Host day for the operating system (e.g.`linux`).
- `labels`(Optional, only for hosts): JSON format for labels (e.g.`{"env": "prod"}`).

 **Example for`hosts_and_folders.csv`**:
```csv
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,,
folder,/prod_servers,Production Servers,,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
```

Save the file in the same directory as the Playbook or adapt the path in the Playbook.

## Steps

### 1. Create or adapt the Playbook
Create a new playbook (e.g.`create_hosts_and_folders_from_csv.yml`) or fit the original `hosts-and-folders.yml` to read the folders and hosts from the CSV file.

 **Playbook:`create_hosts_and_folders_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "{{ vault_automation_secret }}" 
    csv_file: "hosts_and_folders.csv" 
  tasks:
    # CSV-Datei einlesen
    - name: Read folders and hosts from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}" 
        key: name
      register: csv_data

    # Ordner erstellen
    - name: Create folders from CSV
      checkmk.general.folder:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        path: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ csv_data.list | selectattr('type', 'equalto', 'folder') | list }}" 

    # Hosts erstellen
    - name: Create hosts from CSV
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item.name }}" 
        folder: "{{ item.folder | default('/') }}" 
        attributes:
          alias: "{{ item.title }}" 
          ipaddress: "{{ item.ipaddress | default(omit) }}" 
          tag_os: "{{ item.tag_os | default(omit) }}" 
          labels: "{{ item.labels | default({}) | from_json }}" 
        state: present
      loop: "{{ csv_data.list | selectattr('type', 'equalto', 'host') | list }}" 

    # Dynamische Hosts erstellen (Beispiel)
    - name: Create dynamic hosts from query
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "ansible-{{ item }}-{{ 1000 | random }}" 
        folder: "/my_folder" 
        attributes:
          tag_os: linux
          labels:
            source: ansible
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
```

#### Explanation
- **CSV reading**: The module `community.general.read_csv` reads the file `hosts_and_folders.csv` and stores the data in `csv_data`. The option `key: name` indicates each line after the `name`-Feld.
- **Create folder**: The task filters entries with `type: folder` and create folders with the specified `path` and `title` values.
- **Create hosts**: The task filters entries with `type: host` and creates hosts with the specified attributes (`alias`,,`ipaddress`,,`tag_os`,,`labels`). The `folder`-Wert bestimmt den Zielordner, standardmäßig `/`(Root).
- **Dynamic host creation**: The last task remains similar to the original, but creates hosts based on a query (e.g.`os: linux`) with a random suffix in the name.
- **Vault**: The `automation_secret` is saved safely in a vault variable.

### 2. Adjust variables
Adjust the variables in the Playbook to your surroundings:
- **server_url**: Replace with the URL of your CheckMK server (e.g.`https://monitoring.example.com`).
- **site**: Replace with the name of your CheckMk site.
- **Automation_user**: Use the user name for the automation API (e.g.`automation`).
- **Automation_secret**: Use the vault variable (e.g.`{{ vault_automation_secret }}`).
- **csv_file**: Make sure that the path to the CSV file is correct (e.g.`hosts_and_folders.csv` in the same directory as the Playbook).
- **query**: Adjust the query in the Lookup plugin to filter the desired hosts (e.g.`{"host_labels": {"env": "prod"}}`).

#### Create the vault file
```bash
ansible-vault create vault.yml
```

Content of the `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

### 3. Provide CSV file
Create the file `hosts_and_folders.csv` in the same directory as the Playbook or fit the path in the variable `csv_file` to. Example content:
```csv
type,name,title,folder,ipaddress,tag_os,labels
folder,/my_folder,My Folder,,,
folder,/prod_servers,Production Servers,,,
host,myhost1.local,My Host 1,/my_folder,192.168.1.100,linux,{"env": "prod"}
host,myhost2.local,My Host 2,/,192.168.1.101,windows,{"env": "test"}
```

### 4. Run Playbook
Perform the Playbook to create the folders and hosts:

```bash
ansible-playbook create_hosts_and_folders_from_csv.yml --vault-id vault.yml
```

### 5. Tasks of the playbook
The Playbook carries three main tasks:
1. **Lead the CSV file**:
   -Reads the `hosts_and_folders.csv` file and stores the data in `csv_data`.
2. **Create folders**:
   - Erstellt Ordner (z. B. `/my_folder`,,`/prod_servers`) based on the CSV entries with `type: folder`.
3. **Creation of hosts**:
   - Erstellt Hosts (z. B. `myhost1.local`,,`myhost2.local`) based on the CSV entries with `type: host`, with the specified attributes and folder assignments.
4. **Dynamic host creation**:
   - Erstellt Hosts basierend auf einer Abfrage (z. B. `os: linux`) With a random suffix and shows the folder `/my_folder` to.

### 6. Activate changes
After executing the playbook, the changes in CheckMK must be activated, since adding folders and hosts change the configuration:
1. Register in the Checkmk web area.
2. Go to **Setup> Activate Changes** and activate the outstanding changes.
3. Alternatively, activate the changes via the CheckMK API:
```bash
Curl -X Post "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/activation_run/actions/activate-changes/invoke"\
     -H "Authorization: Bearer automation dein_geheimes_passwort"\
     -H "Accept: application/json" 
```

### 7. Überprüfen der Ergebnisse
Nach der Ausführung des Playbooks:
1. Melde dich in der Checkmk-Weboberfläche an und navigiere zu:
   - **Setup > Hosts > Folders**, um die erstellten Ordner (z. B. `/My_folder`, `/Prod_servers`) zu überprüfen.
   - **Monitor > All hosts**, um die erstellten Hosts (z. B. `myhost1.local`, `myhost2.local`) zu überprüfen.
2. Überprüfe die Host-Details:
   - Wähle einen Host aus und prüfe unter **Properties**, ob die Attribute (`alias`, `ipaddress`, `tag_os`, `labels`) are set correctly.
   -Check the folder under **Host> Folder**.
3. Alternatively, check folders and hosts about the CheckMK-API:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/folder_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```
```bash
curl -x get "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_config/collections/all"\
     -H "Authorization: Bearer automation dein_geheimes_passwort"\
     -H "Accept: application/json" 
```

### 8. Fehlerbehandlung
- **CSV-Datei nicht gefunden**: Stelle sicher, dass `hosts_and_forders.csv` existiert und der Pfad in `csv_file` korrekt ist.
- **Ungültiges CSV-Format**: Überprüfe, ob die CSV-Datei die erforderlichen Spalten (`type`, `name`, `title`) enthält und korrekt formatiert ist. JSON-Daten in `labels` müssen gültig sein.
- **Ordner/Host existiert bereits**: Wenn ein Ordner oder Host bereits existiert, ignoriert das Modul die Erstellung (idempotentes Verhalten). Setze `State: Absent`, to delete existing objects.
- **Hosts not found**: If the query in the Lookup plugin does not return hosts (e.g. because no host the day `os: linux` has), the task skipped the creation. Check the query (`query`) and the host tags in Checkmk.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- **Network problems**: Check the accessibility of the CheckMK server (`server_url`) and the correct port sharing (HTTP/HTTPS).
- **TLS certificates**: At https, make sure that the certificate is valid, or set `validate_certs: false` in the Playbook (only for test environments).
- **Checkmk version**: Make sure that the collection is compatible with your CheckMK version (see `SUPPORT.md` in the repository).

### 9. Adjustments and extensions
- **Extended CSV attributes**: Add other columns to the CSV file (e.g. further tags or custom attributes) if future CheckMK versions support them.
- **Dynamic queries**: Adjust the query in the Lookup plugin to use other criteria (e.g.`{"host_labels": {"env": "prod"}}` or `{"folder": "/production"}`).
- **Host deletion**: Set `state: absent` in the host tasks to remove existing hosts.
- **Folder hierarchies**: Create nest folders by making paths like `/parent/child` defines in the CSV file.
- **automation**: Plan the Playbook with a Scheduler (e.g. Ansible Tower/AWX or Cron) to update folder and hosts regularly.
- **Extended CSV structure**: You can expand the CSV file to define additional configurations such as group assignments or downtimes.

## References
- **Security**: Always use a vault file for that `automation_secret` to protect sensitive data.
- **Checkmk version**: Make sure that `checkmk.general` collection is compatible with your CheckMK version (see `SUPPORT.md` in the repository).
- - **documentation**: Further details about modules and Lookup plugins can be found in the [Github documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or on Ansible Galaxy.
- **Test environment**: Test the Playbook in a non-productive environment to avoid unexpected effects.
- **CSV format**: Make sure that the CSV file is correctly formatted (e.g. no missing columns or invalid JSON data in `labels`).
- **Change activation**: After adding folders and hosts, changes must be activated in CheckMK, either manually or via the API.

## Conclusion
The adapted playbook `create_hosts_and_folders_from_csv.yml` allows folders and hosts to be created in Checkmk based on a CSV file and dynamically configured hosts. With the `checkmk.general` collection and the `community.general.read_csv` module can automate the management of monitoring hierarchies flexibly and scalable, which is particularly useful for the organization of hosts in large environments. By adapting the CSV file and the queries, you can adapt the Playbook to your specific requirements.