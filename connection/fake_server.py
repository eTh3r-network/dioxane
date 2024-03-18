import time

from connection.connection import Connection
from misc.hex_enumerator import int_to_bytes
from models.packet import Packet, PacketCode


class FakeConnection(Connection):
    """
    FakeConnection is an implementation of Connection intended for debug purposes.
    It won't actually connect to anything, and can be asked to send any packet.
    It has a list of packets to send, and will send them over time (default delay is one every 2 sec)
    It will reply to any packet recieved with an ACK (can be turned off during init)
    """
    _packets: list[bytearray]  # List of packet to send (FIFO)
    _reply_with_ACK: bool = False  # Reply packet recieved with ACK + pck
    _delay: float = 0.1  # Time in second between two packet

    def __init__(self):
        self._packets = []
        super().__init__()

    def start_listening(self):
        while True:
            if len(self._packets) > 0:
                self._notify_observers(self._packets.pop(0))
            time.sleep(self._delay)

    def send(self, pck: bytearray):
        # Supposely send them

        if self._reply_with_ACK:
            self.receive(int_to_bytes(PacketCode.ACK.value) + pck)

    def receive(self, pck: bytearray):
        """
        Ask the FakeConnection to simulate receiving a packet
        :param pck: Packet to receive
        """
        self._packets.append(pck)
