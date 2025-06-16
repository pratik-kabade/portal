import paramiko
import time
import re

def run_ssh_commands(hostname, username, password, commands):
    try:
        # Create an SSH client instance
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the SSH server
        client.connect(hostname, username=username, password=password)
        print(f"Connected to {hostname}")

        # Open an interactive shell
        shell = client.invoke_shell()
        print("Interactive shell opened")

        # Send commands and receive output
        for command in commands:
            shell.send(command + "\n")
            time.sleep(2)  # Wait for the command to execute
            output = shell.recv(65535).decode('utf-8') # Receive the output
            clean_output = re.sub(r'\x1B\[[0-?9;]*[mK]', '', output)
            print(clean_output)

        # Close the SSH shell and connection
        shell.close()
        client.close()
        print("SSH connection closed")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    hostname = "10.1.0.9"
    username = "genaidevassetv4"
    password = "Genai@123456"

    commands = [
        "cd ~/qemu_rdk-b_docker/qemu_scripts",
        "./qemu_connect_via_ssh.sh",
        "dmcli eRT getv Device.X_RDK_WanManager.CurrentActiveInterface"
    ]

    run_ssh_commands(hostname, username, password, commands)

