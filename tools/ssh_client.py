import paramiko as p
import threading
import subprocess

# Unsafe - Should change to using private key auth.
def ssh_command(ip, user, passwd, command):
    c = p.SSHClient()
    #c.load_host_keys('/home/hcokbo/.ssh/known_hosts')
    c.set_missing_host_key_policy(p.AutoAddPolicy())
    c.connect(ip, username=user, password=passwd)
    session = c.get_transport().open_session()

    if session.active:
        session.exec_command(command)
        print session.recv(1024)
    return

ssh_command("kevinl.io", '''username''' , '''password''', "ls")
