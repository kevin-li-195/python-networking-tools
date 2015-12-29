import sys
import socket
import threading

ip = "0.0.0.0"
port = 9999
host = (ip, port)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(host)

server.listen(5)

print "[*] Listening on %s:%d" % (ip, port)

# Implement function that will run in separate thread to handle clients.
def handle_client(client):
    request = client.recv(1024)
    print "[*] Received: %s" % request 
    client.send("ACK!")
    client.close()

while True:
    try:
        client, addr = server.accept()
        print "[*] Accepted connection from %s:%d" % (addr[0], addr[1])
        client_handler = threading.Thread(target=handle_client,args=(client,))
        client_handler.start()
    except KeyboardInterrupt:
        sys.exit(1)
