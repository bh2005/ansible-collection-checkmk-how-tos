Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to create rules in Checkmk from a CSV file with the Ansible Collection

This HowTo describes how to customize the Playbook `rules.yml` from the repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/rules.yml) to create rules in Checkmk based on a CSV file. It uses the `checkmk.general` Ansible Collection to create rules (`checkmk.general.rules`) for different rulesets, as well as the module `community.general.read_csv` to read the rule information from a CSV file. In addition, existing rules can be dynamically queried and stored.

## Conditions
- **Ansible**: Installed and configured (compatible with the collections).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **community.general Collection**: Installed via `ansible-galaxy install community.general` (for the `read_csv` module).
- **Checkmk server**: Access to a checkmk instance with activated web API.
- **API access data**: Username (`automation_user`) and Password/Secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For safe storage of the `automation_secret`.
- ** Network access**: The Ansible controller must be able to reach the checkmk server via HTTP/HTTPS.
- **CSV file**: A CSV file with the control information read in the Playbook.

Prepare CSV file
Create a CSV file (e.g. `rules.csv`) that defines the rules. The file should contain the following columns:
- `ruleset`: Name of the Ruleset (e.g. `notification_parameters`, `host_tags`, `checkgroup_parameters:filesystem`).
- `folder`: target folder for the rule (e.g. `/` for root or `/my_folder`).
- `conditions`: JSON format for terms and conditions (e.g. `{'host_name': ["web.*"]}').
- `value`: JSON format for control values (e.g. `{"method": "email", "contact_all": true}`).
- `description`: Description of the rule (e.g. `Email notifications for web servers`).

**Example for `rules.cs v`**:
♪
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"},{"levels": [85, 95]},Filesystem thresholds for critical services
♪

Save the file in the same directory as the Playbook or adjust the path in the Playbook.

Steps

### 1. Create or customize Playbook
Create a new playbook (e.g. `create_rules_from_csv.yml`) or customize the original `rules.yml` to read the rules from the CSV file.

**Playbook: `create_rules_from_csv.yml`**:
♪
- hosts: localhost
to be:
vars:
server_url: "https://monitoring.example.com"
site: "mysite"
automation_user: "automation"
automation_secret: "{ vault_automation_secret }"
csv_file: "rules.csv"
tasks:
# Read CSV file
- name: Read rules from CSV file
community.general.read_csv:
path: "{ csv_file }"
key: description
register: rules_data

# Create rules
- name: Create rules from CSV
checkmk.general.rules:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
ruleset: "{ item.ruleset }"
folder: "{ item.folder }"
conditions: "{ item.conditions | from_json }"
value: "{ item.value | from_json }"
description: "{ item.description }"
state: present
loop: "{ rules_data.list }"

# Retrieve and save existing rules
- name: Get all notification rules
ansible.builtin.copy:
content: "{ query('checkmk.general.rules', 'notification_parameters', server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret" | to_nice_yaml }"
dest: "notification_rules.yml"
♪

Explanation
- **CSV-read**: The module `community.general.read_csv` reads the file `rules.csv` and stores the data in `rules_data`. The `key: description` option indicates each line after the `description` field.
- **Create rules**: The task creates rules for the specified Rulesets (`ruleset`), with terms (`conditions`), values (`value`), and descriptions (`description`) from the CSV file. The fields `conditions` and `value` are separated from JSON.
**Retrieval rules**: The last task remains similar to the original and stores all rules of the Rulesets `notification_parameter` in a YAML file (`notification_rules.yml`).
- **Vault**: The `automation_secret` is safely stored in a Vault variable.

### 2. Customize variables
Adjust the variables in the Playbook to your environment:
- **server_url**: Replace your checkmk server URL (e.g. `https://monitoring.example.com`).
- **site**: Replace by the name of your checkmk site.
- **automation_user**: Use the username for the automation API (e.g. `automation`).
- **automation_secret**: Use the Vault variable (e.g. `{ vault_automation_secret }`).
- **csv_file**: Make sure the path to the CSV file is correct (e.g. `rules.csv` in the same directory as the Playbook).

#### Create Vault file
♪
ansible-vault create vault.yml
♪

Content of the `vault.yml`:
♪
vault_automation_secret: your_secret_password
♪

### 3. Provide CSV file
Create the `rules.csv` file in the same directory as the Playbook or adjust the path in the `csv_file` variable. Example content:
♪
ruleset,folder,conditions,value,description
notification_parameters,/,{"host_name": ["web.*"]},{"method": "email", "contact_all": true},Email notifications for web servers
host_tags,/,{"host_name": ["db.*"]},{"tag_id": "db_role", "tag_value": "primary"},Tag primary for database servers
checkgroup_parameters:filesystem,/my_folder,{"service_labels": {"type": "critical"},{"levels": [85, 95]},Filesystem thresholds for critical services
♪

### 4. Run Playbook
Run the Playbook to create the rules:

♪
ansible-playbook create_rules_from_csv.yml --vault-id vault.yml
♪

### 5. Playbook tasks
The Playbook performs two main tasks:
1. **Read the CSV file**:
- Read the `rules.csv` file and saves the data in `rules_data`.
2. **Creating rules**:
- Creates rules for the specified rulesets (e.g. `notification_parameters`, `host_tags`, `checkgroup_parameters:filesystem`) based on the CSV entries, with the specified conditions, values and descriptions.
3. **Retrieving rules**:
- Calls all rules for the Ruleset `notification_parameters` and saves them in `notification_rules.yml`.

### 6. Enable changes
After running the Playbook, the changes in Checkmk must be activated as adding rules changes the configuration:
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
- **Setup > General > Rule-based notifications** to check the notification rule.
- **Setup > Hosts > Host tags** to check host tag rule.
- **Setup > Services > Service monitoring rules** to check the service parameter rule.
Two. Check the rules:
- Select the appropriate ruleset and check whether the rule has been correctly created with the description (e.g. `Email notifications for web servers`) and the terms/values.
3. Check the saved rules:
- Open the `notification_rules.yml file to see the requested rules.
4. Alternatively, check the checkmk API rules:
♪
"https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/rule/collections/all?ruleset_name=notification_parameters"
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

### 8. Error handling
- **CSV file not found**: Make sure that `rules.csv` exists and the path in `csv_file` is correct.
- **Invalid CSV format**: Check if the CSV file contains the required columns (`ruleset`, `folder`, `conditions`, `value`, `description`) and is formatted correctly. JSON data in `conditions` and `value` must be valid.
- **Rule already exists**: If a rule already exists with the same properties, the module ignores the creation (idempotent behavior). Set `state: absent` to delete existing rules.
- **Invalid Ruleset**: Make sure that the `ruleset` in the CSV file is a valid checkmk readout (e.g. `notification_parameters`). Consulate the [Checkmk Documentation](https://docs.checkmk.com/latest/en/rest_api.html) for valid Rulesets.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- ** Network problems**: Check the availability of the checkmk server (`server_url`) and the correct port release (HTTP/HTTPS).
- **TLS certificates**: For HTTPS, make sure the certificate is valid, or setze `validate_certs: false` in the Playbook (only for test environments).
- **Checkmk version**: Make sure the collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).

### 9. Adaptations and extensions
- **Advanced CSV attributes**: Add further columns to the CSV file (e.g. `properties` for rule properties like `disabled`) if future checkmk versions support them.
- **Complex conditions**: Extend the `conditions` column to define more complex conditions such as multiple host or service patterns.
- **Rule deletion**: Set `state: absent` in the rule task to remove existing rules.
- **Other Rulesets**: Customize the CSV file to create rules for other Rulesets (e.g. `active_checks:http`, `inventory_df_rules`).
- **Automatization**: Plan the playbook with a scheduler (e.g. Ansible Tower/AWX or Cron) to regularly update rules.
- **Regulation backup**: Expand the last task to query and save rules for other rulesets.

##
- **Safety**: Always use a Vault file for the 'automation_secret' to protect sensitive data.
- **Checkmk version**: Make sure the `checkmk.general` Collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).
- **Document**: For more details on modules and lookup plugins, see the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- **Test environment**: Test the playbook in a non-productive environment to avoid unexpected effects.
- **CSV format**: Make sure that the CSV file is correctly formatted (e.g. no missing columns or invalid JSON data in `conditions` or `value`).
- Change activation**: After adding rules, changes in Checkmk must be activated either manually or via the API.

## Fazite
The customized Playbook `create_rules_from_csv.yml` allows to create rules in Checkmk based on a CSV file and dynamically query existing rules. With the `checkmk.general` Collection and the `community.general.read_csv` module, you can automate the rule management flexibly and scalable, which is particularly useful for configuring notifications, tags and service parameters in large environments. By adjusting the CSV file, you can adjust the Playbook to your specific requirements.
