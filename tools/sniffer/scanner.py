import threading
import time
from netaddr import IPNetwork, IPAddress
from classes import *
import sys
import socket
import os
from ctypes import *

# Using gethostbyname(gethostname()) sometimes gets the loopback address; keep this in mind.
# Manually providing the public interface may be necessary for now.
#host = socket.gethostbyname(socket.gethostname())
host = "192.168.0.113"
subnet = "192.168.0.0/24"
message = "Superduperping"

def udp_sender(subnet, message):
    time.sleep(5)
    sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    for ip in IPNetwork(subnet):
        try:
            sender.sendto(message,("%s" % ip, 65212))
        except:
            pass

if __name__ == "__main__":

    # If we're in Windows, set socket protocol to use any protocol.
    # Otherwise we specify ICMP in Linux because Linux is very demanding.
    if os.name == "nt":
        socket_protocol = socket.IPPROTO_IP
    else:
        socket_protocol = socket.IPPROTO_ICMP

    # Now we set up our sniffer socket using the appropriate protocol
    # and a socket type of raw socket.
    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)

    # We bind the socket to the host (the host provided is the loopback address)
    # and listen on the public interface.
    sniffer.bind((host,0))
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # If we're in Windows, turn on promiscuous mode.
    if os.name == "nt":
        sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    t = threading.Thread(target=udp_sender, args=(subnet, message))
    t.start()

    try:
        while True:
            print("Sniffing for packet...")
            raw_buffer = sniffer.recvfrom(1024)[0]
            ip_header = IP(raw_buffer[0:20]) # Assuming the header will be 20 bytes long.

            print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))

            # Now check for ICMP. If it is, we create an ICMP struct.
            if ip_header.protocol == "ICMP":
                # Get desired offset from Internet Header Length in IP header
                offset = ip_header.ihl*4

                # Get entire ICMP header from the start of the offset to the end of offset, defined by sizeof(ICMP)
                socket_buffer = raw_buffer[offset:offset + sizeof(ICMP)]

                # Create ICMP struct.
                icmp_header = ICMP(socket_buffer)

                # Only print ICMP related info if it's actually ICMP.
                print("ICMP -> Type: %d, Code: %d" % (icmp_header.packet_type, icmp_header.code))
                
                if icmp_header.code == 3 and icmp_header.type == 3:
                    if IPAddress(ip_header.src_address) in IPNetwork(subnet):
                        if raw_buffer[len(raw_buffer)-len(message):] == message:
                            print("Host up: %s" % ip_header.src_address)

    except KeyboardInterrupt:
        if os.name == "nt":
            sniffer.setsockopt(socket.SIO_RCVALL, socket.RCVALL_OFF)
        sys.exit(0)
