import socket
import sys
import threading

# Number of seconds before timeout.
timeout_seconds = 2

'''====================================```
EDIT FUNCTIONS BELOW TO MANIPULATE BUFFERS
BEFORE SENDING TO LOCAL/REMOTE SOCKETS.
==========================================

==========================================
    Use request_handler function to 
    edit data received from local socket
    before sending to remote socket
======================================='''
def request_handler(b):
    # Put okay things here.
    return b

''' ===================================== ```
    Use response_handler function to
    edit data received from remote socket
    before sending to local socket'''
''' ===================================== '''
def response_handler(b):
    # Put cool things here!
    return b

''' ===================================== '''
''' DO NOT EDIT ANYTHING BELOW THIS POINT '''
''' ===================================== '''

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print("[!!] Failed to listen on [%s]:[%d]" % (local_host, int(local_port)))
        print("[!!] Check for other listening sockets or correct permissions.")
        print("Error: %s" % str(e))
        sys.exit(0)

    print("[*] Listening on port [%s]:[%d]" % (local_host, local_port))

    server.listen(5)

    while True:
        client, addr = server.accept()
        print("[==>] Received connection from [%s]:[%d]" % (addr[0], addr[1]))
        t = threading.Thread(target=proxy_handler, args=(client, remote_host, remote_port, receive_first))
        t.start()

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    print("[*] Connected to remote host at: %s" % remote_host)

    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        remote_buffer = response_handler(remote_buffer)

        if len(remote_buffer):
            print("[<==] Sending %d bytes to localhost" % len(remote_buffer))
            client_socket.send(remote_buffer)

    while True:
        local_buffer = receive_from(client_socket)
        if len(local_buffer):
            print("Received %d bytes from client." % len(local_buffer))
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)

            remote_socket.send(local_buffer)
            print("Sent %d bytes to remote." % len(local_buffer))

        remote_buffer = receive_from(remote_socket)
        if len(remote_buffer):
            print("Received %d bytes from remote." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("Send %d bytes to client." % len(remote_buffer))

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            break

def hexdump(bs, length=16):
    result = []
    digits = 4 if isinstance(bs, unicode) else 2
    for i in xrange(0,len(bs), length):
        a = bs[i:i+length]
        hexa = b" ".join(["%0*X" % (digits, ord(x)) for x in a])
        text = b"".join([x if 0x20 <= ord(x) < 0x7F else b"." for x in a])
        result.append(b"%04X %-*s %s" % (i, length*(digits + 1), hexa, text))

        print b'\n'.join(result)

def receive_from(connection):
    buff = ""
    connection.settimeout(timeout_seconds)

    try:
        while True:
            data = connection.recv(4096)
            if len(data) < 4096:
                buff += data
                break
            buff += data
    except:
        pass
    
    return buff
            
def main():
    if len(sys.argv[1:]) < 5:
        print("Usage: ./tcp_proxy.py [localhost] [localport] [remotehost] [remoteport] [receivefirst]")
        print("Example: ./tcp_proxy.py 123.456.789.111 8080 206.206.206.206 4444 True")
        sys.exit(0)

    print("[*] Running TCP Proxy...")

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5]

    if "True" in receive_first or "true" in receive_first or "1" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

main()
