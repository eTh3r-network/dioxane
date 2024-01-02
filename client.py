#
# This file is part of the eTh3r project, written, hosted and distributed under MIT License
#  - eTh3r network, 2023-2024
#

import sys
from ether.protocol import Client

def help(code=0):
    print(" - di0xane - A simple ether python client ")
    print("")
    print("Usage: client.py [server ip] [server port (default=2142)] <parameters>")
    print("")
    print("Available parameters:")
    print(" -v  verbose")
    print("")
    sys.exit(code)


if "-h" in sys.argv:
    help()

if len(sys.argv) < 2:
    help(code=1)

ip = sys.argv[1]
port = 2142
verbose = False

try:
    port = int(sys.argv[2])
except:
    pass

if "-v" in sys.argv:
    verbose = True

if verbose:
    print(f"[*] connecting to {ip}:{port}")
