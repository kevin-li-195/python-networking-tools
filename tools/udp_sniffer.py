# UDP packet sniffer: Windows and Linux compatible
import socket
import os

host = "192.168.0.1"
op_sys = os.name

# Windows allows us to leave the protocol as default to sniff anything,
# but Linux forces us to specify that we're looking for ICMP.
if op_sys == "nt":
    protocol = socket.IPPROTO_IP
else:
    protocol = socket.IPPROTO_ICMP

sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, protocol)

sniffer.bind((host, 0))

sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

# If we're running on a Windows machine, turn on promiscuous mode.
if op_sys == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

print(sniffer.recvfrom(65565))

if op_sys == "nt":
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
