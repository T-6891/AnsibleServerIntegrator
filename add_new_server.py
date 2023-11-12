#!/usr/bin/env python3

import paramiko
import getpass
import logging
import subprocess
import os
import time

# Configuration variables
LOG_FILE = '/your/path/add_new_server.log'
LOG_LEVEL = logging.INFO  # Set the general logging level
INVENTORY_PATH = '/your/path/ansible-project/inventory/hosts'
PRIVATE_KEY_PATH = '/your/path/ssh/id_ed25519'
PUBLIC_KEY_PATH = '/your/path/ssh/id_ed25519.pub'

# Logging setup
logging.basicConfig(filename=LOG_FILE, level=LOG_LEVEL, format='%(asctime)s %(levelname)s:%(message)s', filemode='w')

# Function to log messages at the set LOG_LEVEL
def log_message(message):
    if LOG_LEVEL == logging.DEBUG:
        logging.debug(message)
    elif LOG_LEVEL == logging.INFO:
        logging.info(message)
    elif LOG_LEVEL == logging.WARNING:
        logging.warning(message)
    elif LOG_LEVEL == logging.ERROR:
        logging.error(message)
    elif LOG_LEVEL == logging.CRITICAL:
        logging.critical(message)
    else:
        logging.info(message)  # Default level

# Function for SSH connection
def ssh_connect(hostname, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, username=username, password=password)
    return client

# Function to execute a command on a remote server with sudo
def execute_ssh_sudo_command(client, command, password):
    channel = client.get_transport().open_session()
    channel.get_pty()
    channel.exec_command(command)
    time.sleep(1)  # Allow some time for the password prompt to appear
    channel.send(password + '\n')
    while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
        if channel.recv_ready():
            print(channel.recv(1024).decode('utf-8'))
        if channel.recv_stderr_ready():
            print(channel.recv_stderr(1024).decode('utf-8'))
        time.sleep(1)
    return channel.recv_exit_status()

# Function to add a server to the Ansible inventory
def add_to_inventory(hostname, inventory_path=INVENTORY_PATH, private_key_path=PRIVATE_KEY_PATH):
    with open(inventory_path, 'a') as file:
        file.write(f"{hostname} ansible_host={hostname} ansible_user=ansible ansible_ssh_private_key_file={private_key_path}\n")
    log_message(f"Added {hostname} to inventory.")

# Function to add a host to known_hosts
def add_host_to_known_hosts(hostname):
    command = f"ssh-keyscan -H {hostname} >> {os.path.expanduser('~')}/.ssh/known_hosts"
    process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if process.returncode != 0:
        error_message = process.stderr.decode('utf-8').strip()
        log_message(f"Error adding {hostname} to known_hosts: {error_message}")
        return f"Error: {error_message}"
    log_message(f"Host {hostname} added to known_hosts.")
    return "Host added to known_hosts."

# Function to check the server using Ansible ping
def ansible_ping_check(hostname, inventory_path=INVENTORY_PATH):
    command = f"ansible {hostname} -i {inventory_path} -m ping"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        error_message = stderr.decode('utf-8').strip()
        log_message(f"Ansible ping error for {hostname}: {error_message}")
        return f"Error: {error_message}"
    log_message(f"Ansible ping successful for {hostname}: {stdout.decode('utf-8')}")
    return stdout.decode('utf-8')

# Main script logic
def main():
    log_message("Starting script")

    hostname = input("Enter server address: ")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    # Connect to the server
    try:
        ssh_client = ssh_connect(hostname, username, password)
        log_message(f"Connected to {hostname}")

        # Create ansible account and add to sudo
        sudo_command = "sudo useradd -m ansible && sudo sh -c 'echo \"ansible ALL=(ALL) NOPASSWD:ALL\" > /etc/sudoers.d/ansible'"
        exit_status = execute_ssh_sudo_command(ssh_client, sudo_command, password)
        if exit_status != 0:
            raise Exception("Error executing sudo command")
        log_message("Created ansible user and added to sudoers")

        # Create .ssh directory for ansible user
        mkdir_command = "sudo -u ansible mkdir -p ~ansible/.ssh"
        exit_status = execute_ssh_sudo_command(ssh_client, mkdir_command, password)
        if exit_status != 0:
            raise Exception("Error creating .ssh directory")
        log_message("Created .ssh directory for ansible user")

        # Add public key
        with open(PUBLIC_KEY_PATH, 'r') as file:
            public_key = file.read().strip()
        key_command = f"echo '{public_key}' | sudo -u ansible tee ~ansible/.ssh/authorized_keys"
        exit_status = execute_ssh_sudo_command(ssh_client, key_command, password)
        if exit_status != 0:
            raise Exception("Error adding public key")
        log_message("Added public key to ansible user")

        ssh_client.close()

        # Add server to Ansible inventory and known_hosts
        add_to_inventory(hostname)
        known_hosts_result = add_host_to_known_hosts(hostname)
        print(known_hosts_result)

        # Check server using Ansible ping
        ping_result = ansible_ping_check(hostname)
        print(ping_result)

    except Exception as e:
        log_message(f"Error: {e}")

if __name__ == "__main__":
    main()
