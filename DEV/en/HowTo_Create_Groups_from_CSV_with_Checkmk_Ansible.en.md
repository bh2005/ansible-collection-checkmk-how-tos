# How to create host and service groups in CheckMK from a CSV file with the Ansible Collection

> This document was translated by machine and may contain errors. Please read with caution!


This HowTo describes how to `groups.yml` from the repository [Checkmk/Ansible-Collection-Checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/groups.yml) adjusted to create host and service groups in Checkmk based on a CSV file. It uses the `checkmk.general` ansible collection to host groups (`checkmk.general.checkmk_hostgroup`) and service groups (`checkmk.general.checkmk_servicegroup`) to create, as well as the module `community.general.read_csv` to read the group information from a CSV file. In addition, hosts can be assigned to a host group dynamically based on tags or other criteria.

## Prerequisites
- **Ansible**: Installed and configured (compatible with the collections).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Community.General Collection**: Installed via `ansible-galaxy collection install community.general`(for the `read_csv`-Modul).
- **Checkmk server**: Access to a CheckMK instance with activated web API.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For the safe storage of the `automation_secret`.
- **Network access**: The Ansible controller must be able to reach the CheckMK server via HTTP/HTTPS.
- **Host**: The hosts mentioned in the Playbook (e.g. with the day `os: linux`) must exist in the CheckMK instance.
- **CSV file**: A CSV file with the group information that is read in the Playbook.

## Prepare CSV file
Create a CSV file (e.g.`groups.csv`) that defines the host and service groups. The file should contain at least the following columns:
- `type`: Type of the group (`hostgroup` or `servicegroup`).
- `name`: Name of the group (e.g.`web_servers`).
- `title`: Advertisements of the group (e.g.`Web Servers`).

 **Example for`groups.csv`**:
```csv
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
```

Save the file in the same directory as the Playbook or adapt the path in the Playbook.

## Steps

### 1. Create or adapt the Playbook
Create a new playbook (e.g.`create_groups_from_csv.yml`) or fit the original `groups.yml` to read the groups from the CSV file.

 **Playbook:`create_groups_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "{{ vault_automation_secret }}" 
    csv_file: "groups.csv" 
  tasks:
    # CSV-Datei einlesen
    - name: Read groups from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}" 
        key: name
      register: groups_data

    # Hostgruppen erstellen
    - name: Create host groups from CSV
      checkmk.general.checkmk_hostgroup:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ groups_data.list | selectattr('type', 'equalto', 'hostgroup') | list }}" 

    # Servicegruppen erstellen
    - name: Create service groups from CSV
      checkmk.general.checkmk_servicegroup:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item.name }}" 
        title: "{{ item.title }}" 
        state: present
      loop: "{{ groups_data.list | selectattr('type', 'equalto', 'servicegroup') | list }}" 

    # Hosts einer Hostgruppe zuweisen (z. B. web_servers für Linux-Hosts)
    - name: Add hosts to a host group
      checkmk.general.checkmk_host:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        name: "{{ item }}" 
        attributes:
          groups:
            host:
              - "web_servers" 
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
```

#### Explanation
- **CSV reading**: The module `community.general.read_csv` reads the file `groups.csv` and stores the data in `groups_data`. The option `key: name` make sure that each line after the `name`-Feld indiziert wird.
- **Create host groups**: The task filters entries with `type: hostgroup` and creates host groups with the specified `name` and `title` values.
- **Create service groups**: The task filters entries with `type: servicegroup` and creates service groups.
- **Host**: Hosts with the day `os: linux` become the host group `web_servers` assigned. Fit the group name (`web_servers`) or the query (`{'host_tags': {'os': 'linux'}}`) to your needs.
- **Vault**: The `automation_secret` is saved safely in a vault variable.

### 2. Adjust variables
Adjust the variables in the Playbook to your surroundings:
- **server_url**: Replace with the URL of your CheckMK server (e.g.`https://monitoring.example.com`).
- **site**: Replace with the name of your CheckMk site.
- **Automation_user**: Use the user name for the automation API (e.g.`automation`).
- **Automation_secret**: Use the vault variable (e.g.`{{ vault_automation_secret }}`).
- **csv_file**: Make sure that the path to the CSV file is correct (e.g.`groups.csv` in the same directory as the Playbook).
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
Create the file `groups.csv` in the same directory as the Playbook or fit the path in the variable `csv_file` to. Example content:
```csv
type,name,title
hostgroup,web_servers,Web Servers
hostgroup,db_servers,Database Servers
servicegroup,http_services,HTTP Services
servicegroup,database_services,Database Services
```

### 4. Run Playbook
Perform the Playbook to create the groups and assign hosts:

```bash
ansible-playbook create_groups_from_csv.yml --vault-id vault.yml
```

### 5. Tasks of the playbook
The Playbook carries three main tasks:
1. **Lead the CSV file**:
   - Liest die `groups.csv` file and stores the data in `groups_data`.
2. **Creation of host groups**:
   - Erstellt Hostgruppen (z. B. `web_servers`,,`db_servers`) based on the CSV entries with `type: hostgroup`.
3. **Creation of service groups**:
   - Erstellt Servicegruppen (z. B. `http_services`,,`database_services`) based on the CSV entries with `type: servicegroup`.
4. **Dynamic assignment of hosts to a host group**:
   -Hosts with the day `os: linux` the host group `web_servers` too (adaptable).

### 6. Activate changes
After executing the playbook, the changes in CheckMK must be activated, since the assignment of hosts to a host group changes configuration:
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
   - **Setup > Hosts > Host groups**, um die erstellten Hostgruppen (z. B. `web_servers`, `db_servers`) zu überprüfen.
   - **Setup > Services > Service groups**, um die erstellten Servicegruppen (z. B. `http_services`, `database_Services`) to check.
2. Check the host allocation:
   -Go to **Monitor> All hosts**, choose a host out of the list (e.g. with the day `os: linux`) and check under **Properties> Host Groups** whether `web_servers` is assigned.
3. Alternatively, check the groups via the Checkmk API:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/host_group_config/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```

### 8. Error treatment
- **CSV file not found**: Make sure that `groups.csv` existed and the path in `csv_file` correct.
- **Invalid CSV format**: Check whether the CSV file the required columns (`type`,,`name`,,`title`) contains and correctly formatted.
- **Host group/service group already exists**: If a group already exists, the module ignores the creation (idempotent behavior). Setting `state: absent`, to delete existing groups.
- **Hosts not found**: If the query in the Lookup plugin does not return hosts (e.g. because no host the day `os: linux` has), the task skipped the assignment. Check the query (`query`) and the host tags in Checkmk.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- **Network problems**: Check the accessibility of the CheckMK server (`server_url`) and the correct port sharing (HTTP/HTTPS).
- **TLS certificates**: At https, make sure that the certificate is valid, or set `validate_certs: false` in the Playbook (only for test environments).
- **Checkmk version**: Make sure that the collection is compatible with your CheckMK version (see `SUPPORT.md` in the repository).

### 9. Adjustments and extensions
- **Extended CSV attributes**: Add further columns to the CSV file (e.g.`description` or user-defined attributes) if future CheckMK versions support them.
- **Dynamic queries**: Adjust the query in the Lookup plugin to use other criteria (e.g.`{"host_labels": {"env": "prod"}}` or `{"folder": "/production"}`).
- **Service group assignment**: To assign services of a service group, you can `checkmk.general.checkmk_service` use (not included in the demo playbook, but available in the collection).
- **Removing groups**: Set `state: absent` in the tasks to delete existing host or service groups.
- **automation**: Plan the Playbook with a Scheduler (e.g. Ansible Tower/AWX or Cron) to update groups regularly.
- **Extended CSV structure**: You can expand the CSV file to also define allocation rules (e.g. a column `host_tags` for the dynamic assignment of hosts).

## References
- **Security**: Always use a vault file for that `automation_secret` to protect sensitive data.
- **Checkmk version**: Make sure that `checkmk.general` collection is compatible with your CheckMK version (see `SUPPORT.md` in the repository).
- - **documentation**: Further details about modules and Lookup plugins can be found in the [Github documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or on Ansible Galaxy.
- **Test environment**: Test the Playbook in a non-productive environment to avoid unexpected effects.
- **CSV format**: Make sure that the CSV file is correctly formatted (e.g. no missing columns or invalid characters).
- **Change activation**: After assigning hosts to a host group, changes in CheckMK must be activated, either manually or via the API.

## Conclusion
The adapted playbook `create_groups_from_csv.yml` allows you to create host and service groups in Checkmk based on a CSV file and to assign hosts to a host group dynamically. With the `checkmk.general` collection and the `community.general.read_csv` module can automate the group management flexibly and scalable, which is particularly useful for the management of monitoring objects in large environments. By adapting the CSV file and the queries, you can adapt the Playbook to your specific requirements.