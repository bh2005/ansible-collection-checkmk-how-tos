# Ansible collection for CheckMK: Howto for German-speaking users

> This document was translated by machine and may contain errors. Please read with caution!


Welcome to this repository! Here I offer German -speaking users a comprehensive HowTo to use the `checkmk.general` ansible collection for Checkmk. The aim is to simplify the automation of checkmk tasks such as managing hosts, services, rules, downtimes and more.

## About this repository
In this repository ([BH2005/Ansible-Things/Ansible Collection](https://github.com/bh2005/ansible-things/tree/main/ansible-collection)) Find instructions, examples and tips on how to use the CheckMK Ansible Collection effectively. The content is specially prepared for German -speaking users to minimize the entry hurdles.

## The Checkmk Ansible Collection
The `checkmk.general` collection is developed and maintained by CheckMK. It enables the automation of monitoring tasks in Checkmk via Ansible, including:
- Create and manage folders, hosts, rules and users.
- Planning downtime (downtimes).
- Manage agents and host groups.
- Dynamic inventory based on CheckMK data.

You can find the official repository of the collection here:
 [https://github.com/checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general) 

## Demo playbooks
The official collection contains a number of demo playbooks that demonstrate various applications. You can find this in the directory:
 [https://github.com/checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo](https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo) 

Examples include:
- **downtimes.yml**: Planning downtime for hosts and services.
- Other playbooks for the management of hosts, agents and rules.

These demo playbooks serve as a starting point to understand the functionalities of the collection and create their own playbooks.

## How you start
1. **Install the collection**:
```bash
   ansible-galaxy collection install checkmk.general
   ```
2. **Prerequisites**:
   - Ansible (kompatible Version).
   - Zugang zu einem Checkmk-Server mit aktivierter Web-API.
   - API-Zugangsdaten (`automation_user` and `automation_secret`).
   - Optional: Ansible Vault für sichere Speicherung von Zugangsdaten.
3. **Use examples**:
   - Klone das Repository der Collection oder dieses Repository, um die Demo-Playbooks zu testen.
   - Passe die Variablen (z. B. `server_url`,,`site`,,`automation_user`) to your surroundings.
4. **Read documentation**:
   - Die offizielle Dokumentation der Collection findest du im [Github repository](https://github.com/Checkmk/ansible-collection-checkmk.general).
   - Weitere Details zu Checkmk und seiner API sind in der [CheckMK documentation](https://docs.checkmk.com) available.

## Contributions
This repository should grow! If you would like to contribute your own instructions, playbooks or tips for German -speaking users, please create a pull request or contact me [BH2005/Ansible-Things](https://github.com/bh2005/ansible-things).

## License
The content of this repositorie is subject to the same license as the `checkmk.general` collection (see [License](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/LICENSE) in the official repository).

Have fun automating with CheckMK and Ansible!