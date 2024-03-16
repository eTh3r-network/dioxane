from enum import Enum, auto

from models.identity import Identity
from models.packet import Packet, PacketCode


class MessageType(Enum):
    SENT = auto()
    RECEIVE = auto()
    SUCCESS = auto()
    LOG = auto()
    DEBUG = auto()
    ERROR = auto()


class Message:
    """
    Generic class to define a Message structure
    It must contains a payload
    It can have a sender, a recipient or a room
    """
    payload: bytearray  # Content of the message
    sender: Identity  # Sender
    recipient: Identity  # Recipient
    room: "Room"  # Room where it was sent/recieved
    ack: bool  # Was it ACK by the server (for sent message)
    message_type: MessageType  # Type

    def __init__(self, payload: bytearray | str, sender: Identity = None, recipient: Identity = None,
                 room: "Room" = None, ack: bool = True, message_type: MessageType = None):
        """
        Create a message, whome payload can be define by a bytearray or a str (will be cast in ascii bytesarray)
        :param payload: Byte array or string
        :param sender: Sender
        :param recipient: Recipient
        :param room: Room
        :param ack: ACK by the server (Default is True)
        :param message_type: Type
        """
        if type(payload) is str:
            payload = bytearray(payload.encode())

        self.payload = payload
        self.sender = sender
        self.recipient = recipient
        self.room = room
        self.ack = ack
        self.message_type = message_type

    def get_send_package(self):
        return Packet(PacketCode.MESSAGE_SEND, self.recipient.get_key_id_pair().append(self.payload))
