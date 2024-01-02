#
# This file is part of the eTh3r project, written, hosted and distributed under MIT License
#  - eTh3r network, 2023-2024
#

import socket
from stuct import pack

ACK = 0xa0

class Client():
    def __init__(self, ip, port=2142):
        self.dest = ip
        self.port = port

        self.bind = None
        self.vers = 0x0001
        self.pub = None

    def setPub(self, pub):
        if type(pub) != bytes:
            print("FATAL! Pub key must be bytes")
            return 1

        if len(pub) > 65535:
            print("FATAL! Pub key length must be smaller than 65535")
            return 2

        self.pub = pub
        return 0

    def _connect(self):
        try:
            self.bind = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.bind.connect((ip, port))
        except e:
            print("FATAL! Can't connect to server:" + str(e))
            return 1

        return 0 

    def _send_vers(self):
        try:
            self.bind.send((0x0531b00b << 16) + self.vers)

            resp = self.bind.recv(1)

            if resp != ACK:
                print("FATAL! Received " + str(hex(resp)) + " from server")
                return 2
        except e:
            print("FATAL! Can't send version: " + str(e))
            return 1

        return 0

    def _send_key(self):
        try:
            pckt = pack("ii", 0x0e1f, len(self.pub))
            pckt += self.pub

            self.bind.send(pckt)

            resp = self.bind.recv(1)

            if resp != ACK:
                print("FATAL! Received " + str(hex(resp)) + " from server")
                return 2
        except e:
            print("FATAL! Can't send key: " + str(e))
            return 1

        return 0


    def connect(self):
        res = self._connect()

        if res != 0:
            return

        res = self._send_vers()

        if res != 0:
            return

        if self.pub is None:
            print("FATAL! No key provided")
            return

        res = self._send_key()

        if res != 0:
            return
