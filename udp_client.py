import socket

target_host = "127.0.0.1"
target_port = 80
target = (target_host, target_port)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.sendto("AAABBBCCC",target)

resp = client.recvfrom(4096)

print resp
