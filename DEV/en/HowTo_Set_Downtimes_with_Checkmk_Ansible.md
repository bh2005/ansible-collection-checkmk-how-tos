Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

♪ How to set downtimes in Checkmk with the Ansible Collection

This HowTo describes how to use the Playbook `downtimes.yml` from the repository [Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/playbooks/demo/downtimes.yml) to schedule downtimes (Downtimes) for hosts and services. The Playbook uses the `checkmk.general` Ansible Collection to set down down times for individual or multiple hosts as well as specific services.

## Conditions
- **Ansible**: Installed and configured (compatible with the collection).
- **checkmk.general Collection**: Installed via `ansible-galaxy collection install checkmk.general`.
- **Checkmk server**: Access to a checkmk instance with activated web API.
- **API access data**: Username (`automation_user`) and Password/Secret (`automation_secret`) for the automation API.
- **Vault (recommended)**: For safe storage of the `automation_secret`.
- ** Network access**: The Ansible controller must be able to reach the checkmk server via HTTP/HTTPS.
- **Hosts/Services**: The hosts specified in the Playbook (e.g. `example.com`) and services (e.g. `Filesystem /`, `Ping`) must exist in the checkmk instance.

Steps

### 1. Download Playbook
Clone the repository or copy the Playbook `downtimes.yml` on your Ansible controller:

♪
git clone https://github.com/Checkmk/ansible-collection-checkmk.general.git
cd ansible-collection-checkmk.general/playbooks/demo
♪

The Playbook looks as follows (excerpt to overview):
♪
- hosts: localhost
to be:
vars:
server_url: "http://localhost"
site: "mysite"
automation_user: "automation"
automation_secret: "mysecret"
comment: "Ansible Downtime"
Duration: 60
tasks:
- name: Set a downtime for a single host
checkmk.general.downtime:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
hostname: "example.com"
comment: "{ comment }"
Duration: "{ duration }"
state: present
- name: Set a downtime for multiple hosts
checkmk.general.downtime:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
hostname: "{ item }"
comment: "{ comment }"
Duration: "{ duration }"
state: present
loop: "{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret_secret}"
- name: Set a downtime for a service
checkmk.general.downtime:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
hostname: "example.com"
service: "Filesystem /"
comment: "{ comment }"
Duration: "{ duration }"
state: present
- name: Set a downtime for a service on multiple hosts
checkmk.general.downtime:
server_url: "{ server_url }"
site: "{ site }"
automation_user: "{ automation_user }"
automation_secret: "{ automation_secret }"
hostname: "{ item }"
service: "Ping"
comment: "{ comment }"
Duration: "{ duration }"
state: present
loop: "{ query('checkmk.general.host', {'host_tags': {'os': 'linux'}, server_url=server_url, site=site, automation_user=automation_user, automation_secret=automation_secret_secret}"
♪

### 2. Customize variables
Adjust the variables in the Playbook to your environment:
- **server_url**: Replace `http://localhost` by the URL of your checkmk server (e.g. `https://monitoring.example.com`).
- **site**: Replace `mysite` by the name of your checkmk site.
- **automation_user**: Use the username for the automation API (e.g. `automation`).
- **automation_secret**: Replace `mysecret` by the API password or token.
- **hostname**: Make sure the host (e.g. `example.com`) exists in your checkmk instance.
- **service**: Check that the services (e.g. `Filesystem /`, `Ping`) are defined in Checkmk.
- **query**: Customize the query in the lookup plugin to filter the desired hosts (e.g. `{"host_tags": {"os": "linux"}` for Linux hosts).

**Recommendation**: Save the `automation_secret` in an Ansible Vault file to increase security.

#### Create Vault file
♪
ansible-vault create vault.yml
♪

Content of the `vault.yml`:
♪
vault_automation_secret: your_secret_password
♪

Edit the Playbook to use the Vault variable:
♪
automation_secret: "{ vault_automation_secret }"
♪

### 3. Run playbook
Run the Playbook to set the downtime:

♪
ansible-playbook downtimes.yml --vault-id vault.yml
♪

### 4. Playbook tasks
The Playbook performs four tasks:
1. **Downtime for a single host**:
- Sets a 60-minute downtime for the host `example.com` with the comment `Ansible Downtime`.
Two. **Downtime for multiple hosts**:
- Calls all hosts with the tag `os: linux` over the lookup plugin `checkmk.general.host` and sets a 60-minute downtime for everyone.
3. **Downtime for a service**:
- Sets a 60-minute downtime for the service `Filesystem /` on the host `example.com`.
4. **Downtime for a service on multiple hosts**:
- Sets a 60-minute downtime for the service `Ping` on all hosts with the tag `os: linux`.

### 5. Checking down times
After running the Playbook:
1. Log in to the Checkmk web interface and navigate to **Monitor > All hosts** or **Monitor > All services**.
Two. Check the downtimes under **Downtimes** (e.g. in the host or service menu).
3. Alternatively, check the downtime via the Checkmk API:
♪
curl -X GET "https://monitoring.example.com/mysite/check_mk/api/1.0/domain-types/downtime/collections/all" \
-H "Authorization: Bearer automation dein_geheimer_passwort" \
-H "Accept: application/json"
♪

### 6. Error handling
- **Host/Service not found**: If the host (e.g. `example.com`) or the service (e.g. `Filesystem /`) does not exist, the task fails. Check the spelling and existence in Checkmk.
- **Invalid access data**: Make sure that `automation_user` and `automation_secret` are correct.
- ** Network problems**: Check the availability of the checkmk server (`server_url`) and the correct port release (HTTP/HTTPS).
- **TLS certificates**: For HTTPS, make sure the certificate is valid, or setze `validate_certs: false` in the Playbook (only for test environments).
- **Lookup plugin error**: If the query does not return hosts in the lookup plugin, check the `query` attribute (e.g. `{"host_tags": {"os": "linux"}`).

### 7. Adjustments and extensions
- **Dynamic host lists**: Apply the query in the lookup plugin to use other criteria (e.g. `{"host_labels": {"env": "prod"}`).
- **Other downtime parameters**: Add further parameters, such as `start_time` or `end_time`, to define the downtime more accurately (see [Checkmk documentation](https://docs.checkmk.com/latest/en/rest_api.html)).
- **Remove Downtimes**: Set `state: absent` in the tasks to remove existing downtimes.
- **Automatization**: Plan the playbook with a scheduler (e.g. Ansible Tower/AWX or Cron) to set regular downtimes.

##
- **Safety**: Always use a Vault file for the 'automation_secret' to protect sensitive data.
- **Checkmk version**: Make sure the `checkmk.general` Collection is compatible with your checkmk version (see `SUPPORT.md` in the repository).
- **Document**: For more details on modules and lookup plugins, see the [GitHub documentation](https://github.com/Checkmk/ansible-collection-checkmk.general) or Ansible Galaxy.
- **Test environment**: Test the playbook in a non-productive environment to avoid unexpected effects.
- **Examples**: The Playbook uses placeholders (`example.com`, `http://localhost`). Customize this to your actual environment.

## Fazite
The Playbook `downtimes.yml` offers a flexible way to set down times in Checkmk for hosts and services, both for individual and for multiple objects. With the `checkmk.general` Collection you can efficiently automate maintenance windows, which is particularly useful for planned failures or regular maintenance work. By adjusting the variables and queries, you can adjust the Playbook to your specific requirements.
