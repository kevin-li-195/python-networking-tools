import socket

# Note: Using Baidu and not Google because I was in China while developing this.
target_host = "www.baidu.com"
target_port = 80
target = (target_host, target_port)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client.connect(target)
client.send("GET / HTTP/1.1\r\nHost: baidu.com\r\n\r\n")

response = client.recv(4096)

print response
