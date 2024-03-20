import random
from enum import Enum, auto

from models.identity import Identity


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
    It can have a sender, a recipient
    """
    payload: bytearray  # Content of the message
    sender: Identity  # Sender
    recipient: Identity  # Recipient
    ack: bool  # Was it ACK by the server (for sent message)
    message_type: MessageType  # Type
    id: int  # Random int

    def __init__(self, payload: bytearray | str, sender: Identity = None, recipient: Identity = None,
                 ack: bool = True, message_type: MessageType = None):
        """
        Create a message, whome payload can be define by a bytearray or a str (will be cast in ascii bytesarray)
        :param payload: Byte array or string
        :param sender: Sender
        :param recipient: Recipient
        :param ack: ACK by the server (Default is True)
        :param message_type: Type
        """
        if type(payload) is str:
            payload = bytearray(payload.encode())

        self.id = random.getrandbits(10)
        self.payload = payload
        self.sender = sender
        self.recipient = recipient
        self.ack = ack
        self.message_type = message_type

    def __hash__(self):
        return hash(self.id)
