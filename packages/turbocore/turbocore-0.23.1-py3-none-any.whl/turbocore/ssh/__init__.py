import paramiko
import os


def run_password_direct(cmd, user, password, port, host):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, port=int(port), username=user, password=password)
        stdin, stdout, stderr = client.exec_command(cmd)
        print(stdout.read().decode())
    finally:
        client.close()


def main():
    user = os.environ.get("SSH_USER", "admin")
    pw = os.environ.get("SSH_PW", "123") # secure
    port_s = os.environ.get("SSH_PORT", "12002")
    host = os.environ.get("SSH_HOST", "127.0.0.1")
    run_password_direct(cmd="dir", user=user, password=pw, port=port_s, host=host)
