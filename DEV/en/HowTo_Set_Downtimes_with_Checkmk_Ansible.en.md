# How to set downtimes in Checkmk with the Ansible Collection

> This document was translated by machine and may contain errors. Please read with caution!


This HowTo describes how to `downtimes.yml` from the repository [Checkmk/Ansible-Collection-Checkmk. General](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/downtimes.yml) used to plan downtime (downtimes) for hosts and services in CheckMK. The Playbook uses the `checkmk.general` ansible collection to set down times for individual or several hosts as well as specific services.

## Prerequisites
- **Ansible**: Installed and configured (compatible with the collection).
- **Checkmk.General Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to a CheckMK instance with activated web API.
- **API access data**: Username (`automation_user`) and password/secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For the safe storage of the `automation_secret`.
- **Network access**: The Ansible controller must be able to reach the CheckMK server via HTTP/HTTPS.
- **Hosts/services**: The hosts given in the Playbook (e.g.`example.com`) and services (e.g. B.`Filesystem /`,,`Ping`) must exist in the CheckMK instance.

## Steps

### 1. Download Playbook
Clone the repository or copy the Playbook `downtimes.yml` on your Ansible controller:

```bash
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
cd ansible-collection-checkmk.general/playbooks/demo
```

The Playbook looks like this (extract for overview):
```yaml
- hosts: localhost
  become: false
  vars:
    server_url: "http://localhost" 
    site: "mysite" 
    automation_user: "automation" 
    automation_secret: "mysecret" 
    comment: "Ansible Downtime" 
    duration: 60
  tasks:
    - name: Set a downtime for a single host
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "example.com" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
    - name: Set a downtime for multiple hosts
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "{{ item }}" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
    - name: Set a downtime for a service
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "example.com" 
        service: "Filesystem /" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
    - name: Set a downtime for a service on multiple hosts
      checkmk.general.downtime:
        server_url: "{{ server_url }}" 
        site: "{{ site }}" 
        automation_user: "{{ automation_user }}" 
        automation_secret: "{{ automation_secret }}" 
        hostname: "{{ item }}" 
        service: "Ping" 
        comment: "{{ comment }}" 
        duration: "{{ duration }}" 
        state: present
      loop: "{{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret) }}" 
```

### 2. Adjust variables
Adjust the variables in the Playbook to your surroundings:
- **server_url**: Replace `http://localhost` through the URL of your CheckMK server (e.g.`https://monitoring.example.com`).
- **site**: Replace `mysite` by the name of your CheckMk site.
- **Automation_user**: Use the user name for the automation API (e.g.`automation`).
- **Automation_secret**: Replace `mysecret` through the API password or token.
- **host name**: Make sure that the host (e.g.`example.com`) exists in your CheckMK instance.
- **service**: Check that the services (e.g.`Filesystem /`,,`Ping`) are defined in CheckMK.
- **query**: Adjust the query in the Lookup plugin to filter the desired hosts (e.g.`{"host_tags": {"os": "linux"}}` for Linux hosts).

 **Recommendation**: Save that `automation_secret` in an Ansible Vault file to increase security.

#### Create the vault file
```bash
ansible-vault create vault.yml
```

Content of the `vault.yml`:
```yaml
vault_automation_secret: dein_geheimes_passwort
```

Edit the Playbook to use the Vault variable:
```yaml
automation_secret: "{{ vault_automation_secret }}" 
```

### 3. Run Playbook
Perform the Playbook to set down times:

```bash
ansible-playbook downtimes.yml --vault-id vault.yml
```

### 4. Tasks of the playbook
The Playbook performs four tasks:
1. **Downtime for a single host**:
   - Setzt eine 60-minütige Ausfallzeit für den Host `example.com` with the comment `Ansible Downtime`.
2. **Downtime for several hosts**:
   - Ruft alle Hosts mit dem Tag `os: linux` about the Lookup plugin `checkmk.general.host` and sets a 60-minute downtime for everyone.
3. **Downtime for a service**:
   - Setzt eine 60-minütige Ausfallzeit für den Service `Filesystem /` on the host `example.com`.
4. **Downtime for a service on several hosts**:
   - Setzt eine 60-minütige Ausfallzeit für den Service `Ping` on all hosts with the day `os: linux`.

### 5. Check downtime
After executing the Playbook:
1. Register in the CheckMK web area and navigate **Monitor> All hosts** or **Monitor> All Services**.
2. Check the downtime under **Downtimes**(e.g. in the host or service menu).
3. Alternatively, check the downtimes via the Checkmk API:
```bash
   curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/downtime/collections/all" \
     -H "Authorization: Bearer automation dein_geheimes_passwort" \
     -H "Accept: application/json" 
   ```

### 6. Error treatment
- **Host/service not found**: If the host (e.g.`example.com`) or the service (e.g.`Filesystem /`) does not exist, the task fails. Check the spelling and existence in Checkmk.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- **Network problems**: Check the accessibility of the CheckMK server (`server_url`) and the correct port sharing (HTTP/HTTPS).
- **TLS certificates**: At https, make sure that the certificate is valid, or set `validate_certs: false` in the Playbook (only for test environments).
- **Lookup plugin error**: If the query in the Lookup plugin does not return hosts, check that `query`-Attribut (z. B. `{"host_tags": {"os": "linux"}}`).

### 7. Adjustments and extensions
- **Dynamic host lists**: Adjust the query in the Lookup plugin to use other criteria (e.g.`{"host_labels": {"env": "prod"}}`).
- - **Other downtime parameters**: Add other parameters, how `start_time` or `end_time` to define the downtime more precisely (see [CheckMK documentation](https://docs.checkmk.com/latest/en/rest_api.html)).
- **Removing downtimes**: Set `state: absent` in the tasks to remove existing downtime.
- **automation**: Plan the Playbook with a Scheduler (e.g. Ansible Tower/AWX or Cron) to set regular downtime.

## References
- **Security**: Always use a vault file for that `automation_secret` to protect sensitive data.
- **Checkmk version**: Make sure that `checkmk.general` collection is compatible with your CheckMK version (see `SUPPORT.md` in the repository).
- - **documentation**: Further details about modules and Lookup plugins can be found in the [Github documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or on Ansible Galaxy.
- **Test environment**: Test the Playbook in a non-productive environment to avoid unexpected effects.
- **Sample values**: The Playbook uses placeholder (`example.com`,,`http://localhost`). Adapt it to your actual environment.

## Conclusion
The playbook `downtimes.yml` offers a flexible way to set downtime in CheckMK for hosts and services, both for individual and for several objects. With the `checkmk.general` collection can efficiently automate maintenance windows, which is particularly useful for planned failures or regular maintenance work. By adapting the variables and queries, you can adapt the Playbook to your specific requirements.