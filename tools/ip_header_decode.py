import sys
import socket
import os
import struct
from ctypes import *

#host = socket.gethostbyname(socket.gethostname())
host = "192.168.0.108"

class IP(Structure):
    ''' Defines a class to encapsulate IP headers.'''

    _fields_ = [ ("ihl", c_ubyte, 4)        # Specifies a 4 bit Internet Header Length in 32-bit words.
                                            # Usually Internet Headers are 20 octets,
                                            # or 5 32-bit words long but can be 60 octets, or 15 32-bit words long.

               , ("version", c_ubyte, 4)    # Specifies a 4 bit IP version.
                                            # (usually 4 or 6, but can use AF_UNSPEC to be IP-version-agnostic.  '''

               , ("tos", c_ubyte)           # Specifies a 8 bit Type of Service,
                                            # (determines level of tradeoff between low delay, high reliability, and high throughput.
                                            # Bits 0-2 : Precedence over other packets.
                                            # Bit 3    : 0 = Normal Delay, 1 = Low Delay
                                            # Bit 4    : 0 = Normal Throughput, 1 = High Throughput
                                            # Bit 5    : 0 = Normal Reliability, 1 = High Reliability
                                            # Bits 6-7 : Reserved for future use.
                                             
                                            # Oftentimes when we set one of the DTR bits to 1, we couple
                                            # it with a tradeoff on the other aspects because it's quite
                                            # expensive for the network. Rarely do we set 2 or 3 bits.

                                            # Precendence designation: 
                                            # 111 - Network : Used only within a network. Actual implementation of intranetwork
                                            #       services that use this designation is up to the network.
                                            # 110 - Internetwork Control : Intended for use by gateway control originators only.
                                            # 101 - CRITIC/ECP
                                            # 100 - Flash Override
                                            # 011 - Flash
                                            # 010 - Immediate
                                            # 001 - Priority
                                            # 000 - Routine

                                            # -- [Prec|eden|ce..| De | Th | Re | FU | FU ] --

               , ("len", c_ushort)          # Specifies total length of the datagram measured in octets, including INHDR and data.
                                            # The size of c_ushort (16 bits) allows for specification of datagram up to 65535 octets
                                            # (8 bits, just in case definition of byte is ambiguous).
                                            # 
                                            # Such sized datagrams are impractical because their arrival at their destination
                                            # and acceptance by the host is uncertain due to their size.

                                            # A datagram of size 576 octets is generally recommended (512 octet data, 64 octet header)
                                            # because all hosts are prepared to accept datagrams of up to 576 octets.

                                            # Maximum header size in octets is 60, and generally the header size is 20, allowing for
                                            # some margin of header size.

               , ("id", c_ushort)           # 16 bits of identification. This is used to help
                                            # piece together the fragmented datagram if the packets arrive
                                            # out of order.

               , ("offset", c_ushort)       # 3 bits of control flags, then 13 bits of fragment offset.
                                            # The 13 bits are used to determine where in the datagram this particular
                                            # fragment, measured in units of 8 octets, or 64 bits.

               , ("ttl", c_ubyte)           # Time to Live. 8 bits indicating the maximum amount of time in seconds
                                            # that the datagram can exist. Every module that processes a datagram
                                            # must decrease the TTL by at least 1 second, however; thus Time to Live is
                                            # really a cap on the amount of time that a datagram can exist in the network.
                                            # This is mainly to ensure that datagrams that can't be delivered are destroyed.

               , ("protocol_num", c_ubyte)  # Protocol number (8 bits) to indicate the protocol of
                                            # the data encapsulated in this IP packet.
                                            # Typically the ones used are 1 for ICMP, 6 for TCP, and 17 for UDP.

               , ("sum", c_ushort)          # Header checksum : 16 bits. Checksum on header. Recomputed each time a packet
                                            # is processed because fields with often changes (e.g. TTL).
                                            # Algorithm:
                                            #   16 bit one's complement of all the 16 bit words in the header.
                                            #   For the purpose of calculating the checksum, the 16 bit header checksum
                                            #   field is considered to be zero.

               , ("src", c_uint32)          # 32-bit source IP address. Originator of the IP packet. Can be edited in transit
                                            # if desired. Using 32bit int for portability between 32bit and 64bit processors.

               , ("dst", c_uint32)          # 32-bit destination IP address. Determined at IP packet creation (or can be
                                            # edited in transit).
                                            # Using 32bit int for portability between 32bit and 64bit processors.
               ]

    def __new__(self, socket_buffer=None):
        return self.from_buffer_copy(socket_buffer)

    def __init__(self, socket_buffer=None):
        # Protocol map = byte
        self.protocol_map = {1:"ICMP", 6:"TCP", 17:"UDP"}

        # Source address = unsigned long.
        # This will turn the packed binary address to a human readable address. (into unsigned int native order)
        self.src_address = socket.inet_ntoa(struct.pack("@I", self.src))

        # Destination address = unsigned long
        # This will turn the packed binary address to a human readable address. (into unsigned int native order)
        self.dst_address = socket.inet_ntoa(struct.pack("@I", self.dst))

        # Transform protocol number to readable protocol (ICMP, TCP, UDP)
        try:
            self.protocol = self.protocol_map[self.protocol_num]
        except:
            self.protocol = str(self.protocol_num)

#if __name__ == "__main__":

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

try:
    while True:
        print("Sniffing for packet...")
        raw_buffer = sniffer.recvfrom(1024)[0]
        ip_header = IP(raw_buffer[0:20]) # Assuming the header will be 20 bytes long.

        print("Protocol: %s %s -> %s" % (ip_header.protocol, ip_header.src_address, ip_header.dst_address))


except KeyboardInterrupt:
    if os.name == "nt":
        sniffer.setsockopt(socket.SIO_RCVALL, socket.RCVALL_OFF)
    sys.exit(0)
