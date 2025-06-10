# How to display all attributes of a folder in Checkmk with Ansible

> This document was translated by machine and may contain errors. Please read with caution!


This HowTo describes how to use the `checkmk.general` ansible collection The attributes of a folder in Checkmk queried and displayed. The guide uses the Lookup plugin `checkmk.general.folder` to the details of a folder, such as B. to maintain criticism or network segments.

## Prerequisites
- **Ansible**: Installed and configured (version compatible with the collection).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to an ongoing CheckMK server with API access.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the CheckMK automation API.
- **Folder**: The folder to be requested (e.g.`/production_servers`) must exist in Checkmk.
- **Vault (optional)**: For the safe storage of the `automation_secret`.

## Steps

### 1. Create the Ansible Playbook
Create a Yaml file (e.g.`show_folder_attributes.yml`) to query the attributes of a folder.

```yaml
- name: Zeige alle Attribute eines Ordners an
  hosts: localhost
  tasks:
    - name: Abfrage der Ordnerattribute
      ansible.builtin.debug:
        msg: "{{ lookup('checkmk.general.folder', folder_path, server_url='https://monitoring.example.com', site='mysite', automation_user='automation', automation_secret=automation_secret) }}" 
      vars:
        folder_path: "/production_servers" 
        automation_secret: "{{ vault_automation_secret }}" 
```

 **Explanation of the parameters**:
- `folder_path`: The path of the folder in Checkmk (e.g.`/production_servers`).
- `server_url`: The URL of the CheckMK server (e.g.`https://monitoring.example.com`).
- `site`: The name of the CheckMK site (e.g.`mysite`).
- `automation_user`: The username for the automation API (e.g.`automation`).
- `automation_secret`: The password or api token (safe saved in an Ansible Vault variables, e.g.`vault_automation_secret`).

### 2. Vault for secure access data (optional)
If you do that `automation_secret` want to save safely, create an encrypted Vault file:

```bash
ansible-vault create vault.yml
```

Add the access data, e.g. B.:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

Perform the Playbook with the Vault file:
```bash
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
```

### 3. Run Playbook
Perform the Playbook to display the attributes of the folder:
```bash
ansible-playbook show_folder_attributes.yml
```

### 4. Interpret the edition
The Lookup plugin returns a JSON-like dictionary that contains the attributes of the folder. Typical attributes can be:
- `criticality`: Criticality level of the folder (e.g.`prod`).
- `network_segment`: Network segment (e.g.`dmz`).
- User-defined tags or other metadata, depending on the CheckMK configuration.

Example issue:
```json
{
   "title": "production_servers",
   "attributes": {
     "criticality": "prod",
     "network_segment": "dmz" 
  }
}
```

### 5. Error treatment
- **Folders do not exist**: The plugin returns an error message if the specified folder does not exist.
- **Invalid access data**: Check `automation_user` and `automation_secret`.
- **Network problems**: Make sure that `server_url` is correct and the server is accessible.

## Alternative: direct API query
If you want to use the API directly (without Ansible), you can use the Checkmk Web API:
```bash
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/objects/folder_config/production_servers" \
  -H "Authorization: Bearer automation dein_geheimes_passwort" \
  -H "Accept: application/json" 
```

This returns the folder details directly in the JSON format.

## References
- The available attributes depend on the CheckMK version and the configurations set. Check the CheckMK documentary for details.
- - Für weitere Informationen zum Lookup-Plugin siehe die Dokumentation der `checkmk.general` collection on [Github](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- Make sure that the TLS certificate test is configured correctly if your server uses HTTPS.

## Conclusion
With the `checkmk.general.folder` lookup plugin can be easily and efficiently called up all the attributes of a folder in Checkmk. This is particularly useful for the automation of monitoring configurations and the documentation of the folder structure.