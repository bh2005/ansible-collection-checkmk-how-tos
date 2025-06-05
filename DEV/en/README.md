Yo, Maschinenübersetzung! Kann mal danebenliegen, also chillig lesen!

# Ansible Collection for Checkmk: HowTo for German-speaking users

Welcome to this repository! Here I offer German-speaking users a comprehensive HowTo to use the `checkmk.general` Ansible Collection for Checkmk. The aim is to simplify the automation of checkmk tasks such as managing hosts, services, rules, downtime and more.

## About this repository
In this repository ([bh2005/ansible-things/ansible-collection](https://github.com/bh2005/ansible-things/tree/main/ansible-collection), you will find instructions, examples and tips on how to use the Checkmk Ansible Collection effectively. The content is specially prepared for German-speaking users to minimize entry barriers.

## Checkmk Ansible Collection
The `checkmk.general` Collection is developed and maintained by Checkmk. It enables the automation of monitoring tasks in Checkmk via Ansible, including:
- Create and manage folders, hosts, rules and users.
- Planning downtimes.
- Managing agents and host groups.
- Dynamic inventory based on checkmk data.

The official repository of the collection can be found here:
[https://github.com/Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general)

# Demo-Playbooks
The official collection contains a number of demo playbooks that demonstrate various applications. This can be found in the directory:
[https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo](https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo)

Examples include:
- **downtimes.yml**: Planning downtime for hosts and services.
- Other playbooks for managing hosts, agents and rules.

These demo playbooks serve as a starting point to understand the features of the collection and create your own playbooks.

## How you start
1. install **Collection**:
♪
ansible-galaxy collection install checkmk.general
♪
2. **Provisions**:
- Ansible (compatible version).
- Access to a checkmk server with activated web API.
- API access data (`automation_user` and `automation_secret`).
- Optional: Ansible Vault for secure storage of access data.
3. **Examples use**:
- Clone the repository of the collection or this repository to test the demo playbooks.
- Customize the variables (e.g. `server_url`, `site`, `automation_user`) to your environment.
4. **Read documentation**
- The official documentation of the collection can be found in [GitHub-Repository](https://github.com/Checkmk/ansible-collection-checkmk.general).
- Further details on Checkmk and its API are available in the [Checkmk Documentation](https://docs.checkmk.com).

## Posts
This repository should grow! If you want to contribute your own instructions, playbooks or tips for German-speaking users, please create a pull request or contact me via [bh2005/ansible-things](https://github.com/bh2005/ansible-things).

##
The contents of this repositories are subject to the same license as the `checkmk.general` Collection (see [LICENSE](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/LICENSE) in the official repository).

Have fun automating with Checkmk and Ansible!