```markdown
# How to Automate Monitoring Configurations with the Checkmk Ansible Collection

This how-to guide describes five concrete examples of how the `checkmk.general` Ansible Collection can be used to automate monitoring configurations in Checkmk. The examples include creating folders, rules, users, host groups, and leveraging the lookup plugin for folder attributes.

---

## Prerequisites

- **Ansible**: Installed and configured (compatible with the collection).
- **Checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk Server**: Access to a running Checkmk server with API access.
- **API Credentials**: Username (`automation_user`) and password/secret (`automation_secret`) for the Checkmk Automation API.
- **Vault (recommended)**: For secure storage of the `automation_secret`.
- **Folders/Hosts**: Some examples assume that certain folders or hosts already exist.

---

## Example 1: Creating a Folder

This example shows how to create a folder in Checkmk to organize hosts.

### Playbook

Create a YAML file (e.g., `create_folder.yml`):

```yaml
- name: Create a folder for production servers
  hosts: localhost
  tasks:
    - name: Create folder
      checkmk.general.checkmk_folder:
        server_url: "[https://monitoring.example.com](https://monitoring.example.com)"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        path: "/production_servers"
        attributes:
          criticality: "prod"
          network_segment: "dmz"
        state: present
```

### Execution

```bash
ansible-playbook create_folder.yml --vault-id vault.yml
```

### Result

A `/production_servers` folder is created with the attributes `criticality: prod` and `network_segment: dmz`.

---

## Example 2: Creating a Monitoring Rule

This example defines a rule for memory monitoring of Linux servers.

### Playbook

Create a YAML file (e.g., `create_rule.yml`):

```yaml
- name: Set memory monitoring rule for Linux servers
  hosts: localhost
  tasks:
    - name: Create rule
      checkmk.general.checkmk_rule:
        server_url: "[https://monitoring.example.com](https://monitoring.example.com)"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        ruleset: "memory"
        folder: "/linux_servers"
        conditions:
          host_tags:
            os: linux
        properties:
          levels:
            warning: 80
            critical: 90
        state: present
```

### Execution

```bash
ansible-playbook create_rule.yml --vault-id vault.yml
```

### Result

A rule is created that triggers warnings at 80% and critical alerts at 90% memory utilization for Linux servers in the `/linux_servers` folder.

---

## Example 3: User Management with Role Assignment

This example creates a new user with administrator rights.

### Playbook

Create a YAML file (e.g., `create_user.yml`):

```yaml
- name: Create a new user with admin rights
  hosts: localhost
  tasks:
    - name: Create user
      checkmk.general.checkmk_user:
        server_url: "[https://monitoring.example.com](https://monitoring.example.com)"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        username: "jdoe"
        fullname: "John Doe"
        password: "{{ vault_user_password }}"
        roles:
          - admin
        contactgroups:
          - "all_admins"
        state: present
```

### Execution

```bash
ansible-playbook create_user.yml --vault-id vault.yml
```

### Result

A user `jdoe` is created with administrator rights and added to the `all_admins` contact group.

---

## Example 4: Creating a Host Group

This example shows how to create a host group to categorize hosts.

### Playbook

Create a YAML file (e.g., `create_hostgroup.yml`):

```yaml
- name: Create a host group for web servers
  hosts: localhost
  tasks:
    - name: Create host group
      checkmk.general.checkmk_hostgroup:
        server_url: "[https://monitoring.example.com](https://monitoring.example.com)"
        site: "mysite"
        automation_user: "automation"
        automation_secret: "{{ vault_automation_secret }}"
        name: "web_servers"
        title: "Web Servers"
        state: present
```

### Execution

```bash
ansible-playbook create_hostgroup.yml --vault-id vault.yml
```

### Result

A host group named `web_servers` is created, which groups hosts with similar characteristics (e.g., web servers).

---

## Example 5: Querying Folder Attributes

This example shows how to query all attributes of a folder using the lookup plugin.

### Playbook

Create a YAML file (e.g., `show_folder_attributes.yml`):

```yaml
- name: Display all attributes of a folder
  hosts: localhost
  tasks:
    - name: Query folder attributes
      ansible.builtin.debug:
        msg: "{{ lookup('checkmk.general.folder', folder_path, server_url='[https://monitoring.example.com](https://monitoring.example.com)', site='mysite', automation_user='automation', automation_secret=automation_secret) }}"
      vars:
        folder_path: "/production_servers"
        automation_secret: "{{ vault_automation_secret }}"
```

### Execution

```bash
ansible-playbook show_folder_attributes.yml --vault-id vault.yml
```

### Result

The attributes of the `/production_servers` folder (e.g., `criticality`, `network_segment`) are output in JSON format.

---

## Vault for Secure Credentials (Optional)

For all examples, you can store sensitive data like `automation_secret` or `vault_user_password` in an Ansible Vault file:

```bash
ansible-vault create vault.yml
```

Content of `vault.yml`:

```yaml
vault_automation_secret: your_secret_password
vault_user_password: user_password
```

Run playbooks with the Vault file:

```bash
ansible-playbook <playbook>.yml --vault-id vault.yml
```

---

## Notes

- **Error Handling**: Ensure the Checkmk server is reachable, credentials are correct, and specified folders/hosts exist.
- **Documentation**: For more details on modules and options, refer to the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- **TLS**: If your server uses HTTPS, verify certificate validation (if no valid certificate is present, consider adding `validate_certs: false` – for test environments only).
- **Checkmk Version**: Ensure the Checkmk version you're using is compatible with the collection (see `SUPPORT.md`).

---

## Conclusion

The `checkmk.general` collection provides powerful tools for automating Checkmk configurations. With these examples, you can efficiently manage and customize folders, rules, users, host groups, and more.
```