# Ansible Collection for Checkmk: How-To for English-Speaking Users

Welcome to this repository! Here, I provide English-speaking users with a comprehensive how-to guide for using the `checkmk.general` Ansible Collection for Checkmk. The goal is to simplify the automation of Checkmk tasks such as managing hosts, services, rules, downtimes, and more.

## About this Repository
In this repository ([bh2005/ansible-things/ansible-collection-checkmk-how-tos](https://github.com/bh2005/ansible-collection-checkmk-how-tos)), you will find instructions, examples, and tips on how to effectively use the Checkmk Ansible Collection. The content is specifically prepared for English-speaking users to minimize entry barriers.

## The Checkmk Ansible Collection
The `checkmk.general` Collection is developed and maintained by Checkmk. It enables the automation of monitoring tasks in Checkmk via Ansible, including:
- Creating and managing folders, hosts, rules, and users.
- Scheduling downtimes.
- Managing agents and host groups.
- Dynamic inventory based on Checkmk data.

You can find the official repository of the collection here:  
[https://github.com/Checkmk/ansible-collection-checkmk.general](https://github.com/Checkmk/ansible-collection-checkmk.general)

## Demo Playbooks
The official collection includes a series of demo playbooks that demonstrate various use cases. You can find these in the directory:  
[https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo](https://github.com/Checkmk/ansible-collection-checkmk.general/tree/main/playbooks/demo)

Examples include:
- **downtimes.yml**: Scheduling downtimes for hosts and services.
- Other playbooks for managing hosts, agents, and rules.

These demo playbooks serve as a starting point to understand the functionalities of the collection and to create your own playbooks.

## How to Get Started
1. **Install the Collection**:
   ```bash
   ansible-galaxy collection install checkmk.general
   ```
2. **Prerequisites**:
   - Ansible (compatible version).
   - Access to a Checkmk server with the web API enabled.
   - API credentials (`automation_user` and `automation_secret`).
   - Optional: Ansible Vault for secure storage of credentials.
3. **Use Examples**:
   - Clone the collection repository or this repository to test the demo playbooks.
   - Adjust the variables (e.g., `server_url`, `site`, `automation_user`) to fit your environment.
4. **Read the Documentation**:
   - The official documentation of the collection can be found in the [GitHub repository](https://github.com/Checkmk/ansible-collection-checkmk.general).
   - More details about Checkmk and its API are available in the [Checkmk documentation](https://docs.checkmk.com).

## Contributions
This repository is meant to grow! If you would like to contribute your own guides, playbooks, or tips for English-speaking users, feel free to create a pull request or contact me via [bh2005/ansible-things](https://github.com/bh2005/ansible-collection-checkmk-how-tos).

## License
The contents of this repository are subject to the same license as the `checkmk.general` Collection (see [LICENSE](https://github.com/Checkmk/ansible-collection-checkmk.general/blob/main/LICENSE) in the official repository).

Happy automating with Checkmk and Ansible!