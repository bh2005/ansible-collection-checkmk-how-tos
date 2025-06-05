Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to display all attributes of a folder in Checkmk with Ansible

This HowTo describes how to query and display the attributes of a folder in Checkmk with the `checkmk.general` Ansible Collection. The guide uses the lookup plugin `checkmk.general.folder` to get the details of a folder, e.g. critique or network segments.

## Conditions
- **Ansible**: Installed and configured (version compatible with the Collection).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to a running checkmk server with API access.
- **API access data**: username (`automation_user`) and password/secret (`automation_secret`) for the checkmk automation API.
- **Ordner**: The folder to be queried (e.g. `/production_servers`) must exist in Checkmk.
- **Vault (optional)**: For safe storage of the `automation_secret`.

Steps

### 1. Create ansible playbook
Create a YAML file (e.g. `show_folder_attributes.yml`) to query the attributes of a folder.

♪
- name: Show all attributes of a folder
hosts: localhost
tasks:
- name: Request of folder attributes
ansible.builtin.debug:
msg: "{ lookup('checkmk.general.folder', folder_path, server_url='https://monitoring.example.com', site='mysite', automation_user='automation', automation_secret=automation_secret}"
vars:
folder_path: "/production_servers"
automation_secret: "{ vault_automation_secret }"
♪

**Declaration of parameters**:
- `folder_path`: The path of the folder in Checkmk (e.g. `/production_servers`).
- `server_url`: The URL of the checkmk server (e.g. `https://monitoring.example.com`).
- `site`: The name of the checkmk site (e.g. `mysite`).
- `automation_user`: The username for the automation API (e.g. `automation`).

- `automation_secret`: The password or API token (safely stored in an Ansible Vault variable, e.g. `vault_automation_secret`).

### 2. Vault for secure access data (optional)
If you want to save the `automation_secret` securely, create an encrypted Vault file:

♪
ansible-vault create vault.yml
♪

Add the access data, e.g. B.:
♪
vault_automation_secret: your_secret_password
♪

Run the Playbook with the Vault file:
♪
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
♪

### 3. Run playbook
Run the Playbook to display the attributes of the folder:
♪
ansible-playbook show_folder_attributes.yml
♪

### 4th edition interpret
The Lookup plugin returns a JSON-like dictionary that contains the attributes of the folder. Typical attributes can be:
- `criticality`: Criticality level of the folder (e.g. `prod`).
- `network_segment`: network segment (e.g. `dmz`).
- Custom tags or other metadata, depending on the checkmk configuration.

Example output:
♪
♪
"title": "production_servers",
"attributes":
"criticality": "prod",
"network_segment": "dmz"
}
}
♪

### 5. Error treatment
**Order does not exist**: The plugin returns an error message if the specified folder does not exist.
- **Invalid access data**: Check `automation_user` and `automation_secret`.
- ** Network problems**: Make sure the `server_url` is correct and the server is accessible.

## Alternative: Direct API query
If you want to use the API directly (without Ansible), you can use the Checkmk Web API:
♪
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/objects/folder_config/production_servers"
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

This returns the folder details directly in JSON format.

##

- The available attributes depend on the Checkmk version and the set configurations. Check the checkmk documentation for details.
- For more information on the lookup plugin see the documentation of the `checkmk.general` Collection on [GitHub](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- Ensure that the TLS certificate check is correctly configured if your server uses HTTPS.

## Fazite
With the `checkmk.general.folder` lookup plugin you can easily and efficiently retrieve all attributes of a folder in Checkmk. This is particularly useful for the automation of monitoring configurations and the documentation of the folder structure.