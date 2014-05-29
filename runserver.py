#!/usr/bin/env python
from payme import app

import socket
import fcntl
import struct

# # # # 
# This file is required when running the (flask) app test server locally
# # # # 

# The raspberry pi has several ip addresses (internal, eth0, wlan0, etc). 
# To get the 'eth0' one we need to use a different method
multiple_ips = False

# extra function to get all ip addresses
def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

# get the ip address
ip_address = socket.gethostbyname(socket.gethostname())
if multiple_ips:
    ip_address = get_ip_address('eth0')

# Run the app
app.run(debug=True, host=ip_address)
