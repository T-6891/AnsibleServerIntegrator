# Ansible Server Integration Script

## Overview
This script facilitates the automatic integration of new servers into an Ansible-managed infrastructure. It streamlines the process of server setup, SSH configuration, and Ansible inventory management, ensuring a seamless and efficient onboarding of servers for IT management and automation.

## Features
- **SSH Connection**: Establish secure SSH connections to new servers using Paramiko.
- **Sudo Command Execution**: Execute necessary commands with sudo privileges on remote servers.
- **Ansible Inventory Management**: Automatically add new servers to the Ansible inventory.
- **Known Hosts Handling**: Manage the known_hosts file for SSH connections.
- **Ansible Ping Check**: Verify server connectivity using Ansible's ping module.

## Prerequisites
- Python 3.x
- Paramiko
- Access to target servers with SSH
- Ansible installed on the control machine

## Installation
1. Clone the repository:
   ```bash
   git clone [repository-url]
   ```
2. Navigate to the script's directory:
   ```bash
   cd [script-directory]
   ```
3. Ensure you have the necessary permissions to execute the script.

## Usage
Run the script using Python and follow the on-screen prompts to enter server details:
```bash
chmod +x add_new_server
./add_new_server.py
```

## Configuration
Configure the script by editing the following variables at the beginning of the script:
- `LOG_FILE`: Path to the log file.
- `INVENTORY_PATH`: Path to the Ansible inventory file.
- `PRIVATE_KEY_PATH`: Path to your SSH private key.
- `PUBLIC_KEY_PATH`: Path to your SSH public key.

## Contributing
Contributions to enhance this script are welcome. Please follow the standard procedure for contributing:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
