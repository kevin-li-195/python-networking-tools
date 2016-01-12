Python Networking Tools
=====

Some tools and samples I made to learn more about networking protocols and the intricacies therein.

Implemented primarily with the Python socket library.

Completed
-----

- net.py : Basic netcat tool for dropping shells, automatically executing commands, and uploading files.
- tcp_proxy.py : Basic TCP proxy server script.
- ssh_client.py : Basic SSH client, currently good for sending just one command. Implemented with the Python paramiko module.
- rssh_client.py : Reverse SSH client. Connects to listening server and provides server with a shell on the client side.
- udp_sniffer.py : UDP packet sniffer.
- mail_sniffer.py : Clear-text mail credential packet sniffer.
- arp_poison.py : ARP poison script.

- Miscellaneous TCP and UDP servers/clients.

Acknowledgement
-----

Tools based on reading material: Black Hat Python.
