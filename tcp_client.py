import socket

# Note: Using Baidu and not Google because I was in China while developing this.
target_host = ""
target_port = 9999
target = (target_host, target_port)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(target)
client.send("Hello")

response = client.recv(4096)

print response
