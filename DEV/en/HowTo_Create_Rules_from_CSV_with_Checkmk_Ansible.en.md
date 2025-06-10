# How to create rules in CheckMK from a CSV file with the Ansible Collection

> This document was translated by machine and may contain errors. Please read with caution!


This HowTo describes how to `rules.yml` from the repository [Checkmk/Ansible-Collection-Checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/rules.yml) adjust to create rules in CheckMK based on a CSV file. It uses the `checkmk.general` ansible collection to rules (`checkmk.general.rules`) for various ruletets, as well as the module `community.general.read_csv` to read the regular information from a CSV file. In addition, existing rules can be queried and saved dynamically.

## Prerequisites
- **Ansible**: Installed and configured (compatible with the collections).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Community.General Collection**: Installed via `ansible-galaxy collection install community.general`(for the `read_csv`-Modul).
- **Checkmk server**: Access to a CheckMK instance with activated web API.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For the safe storage of the `automation_secret`.
- **Network access**: The Ansible controller must be able to reach the CheckMK server via HTTP/HTTPS.
- **CSV file**: A CSV file with the regular information that is read in the Playbook.

## Prepare CSV file
Create a CSV file (e.g.`rules.csv`) that defines the rules. The file should contain the following columns:
- `ruleset`: Name of the Ruleset (e.g. B.`notification_parameters`,,`host_tags`,,`checkgroup_parameters:filesystem`).
- `folder`: Target folder for the rule (e.g.`/` for root or `/my_folder`).
- `conditions`: JSON format for standard conditions (e.g.`{"host_name": ["web.*"]}`).
- `value`: JSON format for regulations (e.g.`{"method": "email", "contact_all": true}`).
- `description`: Description of the rule (e.g.`Email notifications for web servers`).

 **Example for`rules.csv`**:
```csv
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"}},{"levels": [85, 95]},Filesystem thresholds for critical services
```

Save the file in the same directory as the Playbook or adapt the path in the Playbook.

## Steps

### 1. Create or adapt the Playbook
Create a new playbook (e.g.`create_rules_from_csv.yml`) or fit the original `rules.yml` to read the rules from the CSV file.

 **Playbook:`create_rules_from_csv.yml`**:
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "https://monitoring.example.com" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "{{ vault_automation_secret }}" 
    csv_file: "rules.csv" 
  tasks:
    # CSV-Datei einlesen
    - name: Read rules from CSV file
      community.general.read_csv:
        path: "{{ csv_file }}" 
        key: description
      register: rules_data

    # Regeln erstellen
    - name: Create rules from CSV
      checkmk.general.rules:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        ruleset: "{{ item.ruleset }}" 
        folder: "{{ item.folder }}" 
        conditions: "{{ item.conditions | from_json }}" 
        value: "{{ item.value | from_json }}" 
        description: "{{ item.description }}" 
        state: present
      loop: "{{ rules_data.list }}" 

    # Bestehende Regeln abrufen und speichern
    - name: Get all notification rules
      ansible.builtin.copy:
        content: "{{ query('checkmk.general.rules', 'notification_parameters', server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) | to_nice_yaml }}" 
        dest: "notification_rules.yml" 
```

#### Explanation
- **CSV reading**: The module `community.general.read_csv` reads the file `rules.csv` and stores the data in `rules_data`. The option `key: description` indicates each line after the `description`-Feld.
- **Create rules**: The task created rules for the specified ruletets (`ruleset`), with conditions (`conditions`), Values ​​(`value`), and descriptions (`description`) from the CSV file. The fields `conditions` and `value` are spared from Json.
- **Raise the rules**: The last task remains similar to the original and stores all rules of the rulet set `notification_parameters` in a Yaml file (`notification_rules.yml`).
- **Vault**: The `automation_secret` is saved safely in a vault variable.

### 2. Adjust variables
Adjust the variables in the Playbook to your surroundings:
- **server_url**: Replace with the URL of your CheckMK server (e.g.`https://monitoring.example.com`).
- **site**: Replace with the name of your CheckMk site.
- **Automation_user**: Use the user name for the automation API (e.g.`automation`).
- **Automation_secret**: Use the vault variable (e.g.`{{ vault_automation_secret }}`).
- **csv_file**: Make sure that the path to the CSV file is correct (e.g.`rules.csv` in the same directory as the Playbook).

#### Create the vault file
```bash
ansible-vault create vault.yml
```

Content of the `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

### 3. Provide CSV file
Create the file `rules.csv` in the same directory as the Playbook or fit the path in the variable `csv_file` to. Example content:
```csv
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"}},{"levels": [85, 95]},Filesystem thresholds for critical services
```

### 4. Run Playbook
Perform the Playbook to create the rules:

```bash
ansible-playbook create_rules_from_csv.yml --vault-id vault.yml
```

### 5. Tasks of the playbook
The Playbook carries two main tasks:
1. **Lead the CSV file**:
   - Liest die `rules.csv` file and stores the data in `rules_data`.
2. **Creating rules**:
   - Erstellt Regeln für die angegebenen Rulesets (z. B. `notification_parameters`,,`host_tags`,,`checkgroup_parameters:filesystem`) Based on the CSV entries, with the specified conditions, values ​​and descriptions.
3. **Call up rules**:
   - Ruft alle Regeln für das Ruleset `notification_parameters` off and save it in `notification_rules.yml`.

### 6. Activate changes
After executing the playbook, the changes in Checkmk must be activated, since adding rules changes the configuration:
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
   - **Setup > General > Rule-based notifications**, um die Benachrichtigungsregel zu überprüfen.
   - **Setup > Hosts > Host tags**, um die Host-Tag-Regel zu überprüfen.
   - **Setup > Services > Service monitoring rules**, um die Service-Parameter-Regel zu überprüfen.
2. Überprüfe die Regeln:
   - Wähle das entsprechende Ruleset aus und prüfe, ob die Regel mit der Beschreibung (z. B. `Email notifications for web server`) and the conditions/values ​​were created correctly.
3. Check the stored rules:
   - Öffne die Datei `notification_rules.yml` to see the requested rules.
4. Alternatively, check the rules via the Checkmk API:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/rule/collections/all?ruleset_name=notification_parameters" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```

### 8. Error treatment
- **CSV file not found**: Make sure that `rules.csv` existed and the path in `csv_file` correct.
- **Invalid CSV format**: Check whether the CSV file the required columns (`ruleset`,,`folder`,,`conditions`,,`value`,,`description`) contains and correctly formatted. JSON data in `conditions` and `value` must be valid.
- **Usually there is already**: If a rule already exists with the same properties, the module ignores the creation (idempotent behavior). Setting `state: absent`, to delete existing rules.
- - **Invalid ruleset**: Make sure that `ruleset` in the CSV file there is a valid CheckMK ruleset (e.g.`notification_parameters`). Consult the [CheckMK documentation](https://docs.checkmk.com/latest/en/rest_api.html) for valid ruletets.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- **Network problems**: Check the accessibility of the CheckMK server (`server_url`) and the correct port sharing (HTTP/HTTPS).
- **TLS certificates**: At https, make sure that the certificate is valid, or set `validate_certs: false` in the Playbook (only for test environments).
- **Checkmk version**: Make sure that the collection is compatible with your CheckMK version (see `SUPPORT.md` in the repository).

### 9. Adjustments and extensions
- **Extended CSV attributes**: Add further columns to the CSV file (e.g.`properties` for regular properties like `disabled`) if future checkmk versions support them.
- **Complex conditions**: Expand the `conditions`-Spalte, um komplexere Bedingungen wie mehrere Host- oder Service-Muster zu definieren.
- **Rule deletion**: Set `state: absent` in the regular task to remove existing rules.
- **Other ruletets**: Adapt the CSV file to rules for other ruletets (e.g.`active_checks:http`,,`inventory_df_rules`) to create.
- **automation**: Plan the Playbook with a Scheduler (e.g. Ansible Tower/AWX or Cron) to update rules regularly.
- **Rule backup**: Extend the last task to query and save rules for other ruletetts.

## References
- **Security**: Always use a vault file for that `automation_secret` to protect sensitive data.
- **Checkmk version**: Make sure that `checkmk.general` collection is compatible with your CheckMK version (see `SUPPORT.md` in the repository).
- - **documentation**: Further details about modules and Lookup plugins can be found in the [Github documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or on Ansible Galaxy.
- **Test environment**: Test the Playbook in a non-productive environment to avoid unexpected effects.
- **CSV format**: Make sure that the CSV file is correctly formatted (e.g. no missing columns or invalid JSON data in `conditions` or `value`).
- **Change activation**: After adding rules, changes must be activated in Checkmk, either manually or via the API.

## Conclusion
The adapted playbook `create_rules_from_csv.yml` allows rules in CheckMK to be created based on a CSV file and dynamically query existing rules. With the `checkmk.general` collection and the `community.general.read_csv` you can automate the control management flexibly and scalable, which is particularly useful for the configuration of notifications, tags and service parameters in large environments. By adapting the CSV file, you can adapt the Playbook to your specific requirements.