#!/usr/bin/python
import sys
import socket
import threading
import getopt
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_dest = ""
port = 0

# Prints usage of net.py to stdout. Invoked on bad options too.
def usage():
    print "\nNetcat implemented with Python.\n"
    print "Usage: net.py -t target_host -p port"
    print "-l --listen -> listen on [host]:[port]" + \
        " for incoming connections."
    print "-e --execute=file_to_run -> execute the given file" + \
        " upon successful connection."
    print "-c --command -> initialize a command shell."
    print "-u --upload=dest -> upon receiving connection" + \
        " upload a file to dest (destination)."
    print "\n"
    print "Examples\n========"
    print "net.py -t 192.168.0.1 -p 8080 -l -c"
    print "This will listen on 192.168.0.1:8080 for incoming connections" + \
            " and drop a command shell back when it receives one.\n"
    print "net.py -t 192.168.0.1 -p 8080 -l -u=C:\\target.exe"
    print "This will listen on 192.168.0.1:8080 for incoming connections" + \
            " and upload a file to C:\\target.exe\n"
    print "net.py -t 192.168.0.1 -p 8080 -l -e=\"cat /etc/passwd\""
    print "This will listen on 192.168.0.1:8080 for incoming connections" + \
            " and run \"cat /etc/passwd\" when it receives ones.\n"
    print "echo 'ABCDEFGHI' | ./net.py -t 111.111.111.111 -p 1234"
    print "This will send 'ABCDEFGHI' to the listener (assuming there" + \
            " is one) at 111.111.111.111:1234"
    sys.exit(0)

# Helper function to continually send client data from STDIN.
def client_sender(b):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((target, port))
        if len(b):
            client.send(b)
        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break

            sys.stdout.write(response)

            try:
                b = raw_input("")
            except EOFError:
                pass
            b += '\n'
            client.send(b)
    except EOFError:
        pass
    except Exception as e:
        print "[*] Exception: %s. Exiting." % e
        client.close()

# Loop server to handle incoming connections.
def server_loop():
    global target
    
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((target,port))
    server.listen(5)

    while True:
        cl, addr = server.accept()
        thread = threading.Thread(target=client_handler, args=(cl,))
        thread.start()

# Runs accepted command in shell, and returns output. Captures stderr too.
def run_command(cmd):
    cmd = cmd.rstrip()
    try:
        output = subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=True)
    except:
        output = "Failed to execute command.\r\n"
    return output

def client_handler(c):
    global upload
    global execute
    global command

    c.settimeout(2)
    # If upload destination exists,
    # upload data that is put in from sender's STDIN
    # and save in receiver's upload_dest.
    if len(upload_dest):
        file_buff = ""
        while True:
            try:
                data = c.recv(1024)
            except socket.timeout as e:
                print str(e)
                pass
            if len(data) < 1024:
                file_buff += data
                break
            else:
                file_buff += data

        try:
            fp = open(upload_dest, "wb")
            fp.write(file_buff)
            fp.close()
            c.send("Successfully saved file to %s.\r\n" % upload_dest)
        except:
            c.send("Failed to save file to %s.\r\n" % upload_dest)

    # If command is sent, execute command and send back output.
    if len(execute):
        output = run_command(execute)
        c.send(output)

    # If command is set to True, drop back a command shell.
    if command:
        while True:
            c.send("<net.py> $ ")
            cmd = ""
            while True:
                cmd += c.recv(1024)
                if "\n" in cmd:
                    break

            resp = run_command(cmd)

            c.send(resp)

# Main function.
def main():
    global listen
    global port
    global target
    global execute
    global command
    global upload_dest

    if not len(sys.argv[1:]):
        usage()

    try:
        opts, args = getopt.getopt(
                        sys.argv[1:],
                        "hle:t:p:cu:",
                        [ "help"
                        , "listen"
                        , "execute"
                        , "target"
                        , "port"
                        , "command"
                        , "upload"
                        ])

    except getopt.GetoptError as err:
        print str(err)
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        elif o in ("-u", "--upload"):
            upload_dest = a
        else:
            print "Reached else in opts selection"
            assert False,"Unhandled option"

    if not listen and len(target) and port > 0:
        print "======"
        print "If you are trying to get a shell, press CTRL-D."
        print "======"
        print "If you're trying to upload a file, the EOF char"
        print "will end the upload and provide you with a prompt"
        print "indicating success or failure."
        print "======"
        b = sys.stdin.read()
        client_sender(b)

    if listen:
        server_loop()

main()
