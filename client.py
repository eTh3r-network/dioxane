#
# This file is part of the eTh3r project, written, hosted and distributed under MIT License
#  - eTh3r network, 2023-2024
#

import sys
from ether.protocol import Client
from crypto.gpg import getKey

def help(code=0):
    print(" - di0xane - A simple ether python client ")
    print("")
    print("Usage: client.py [server ip] [server port (default=2142)] <parameters>")
    print("")
    print("Available parameters:")
    print(" -v          verbose")
    print(" -i          interractive, com disabled")
    print(" -k <keyid>  specify key")
    print("")
    sys.exit(code)


ip = sys.argv[1]
port = 2142
verbose = False
local = False
key_id = None
pub_key = None

if len(sys.argv) < 2:
    help(code=1)

try:
    port = int(sys.argv[2])
except:
    pass

skip = 0
for (i, arg) in enumerate(sys.argv):
    while skip > 0:
        skip -= 1

    if arg == "-h":
        help()
    
    if arg == "-v":
        verbose = True

    if arg == "-i":
        local = True

    if arg == "-k":
        try:
            key_id = sys.argv()[i+1]
            skip = 1

            pub_key = getKey(key_id)

            if len(pub_key) == 0:
                print("FATAL! Provided key was not found")
        except:
            help()


if verbose:
    print(f"[*] connecting to {ip}:{port}")

    if key_id is not None:
        print(f"[*] Using key id {key_id}, len={len(pub_key)}")

client = Client(ip, port)

if local:
    client.setPub(pub_key)
else:
    print("FATAL! Com protocol not yet written")
    sys.exit(2)

client.connect()

if local:
    pass
