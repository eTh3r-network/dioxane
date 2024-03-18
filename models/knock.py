from enum import Enum, auto

from models.identity import Identity
from models.message import Message, MessageType


class KnockState(Enum):
    KNOCKING = auto()
    KNOCKING_ACK = auto()
    KNOCKING_RECEIVED = auto()
    KNOCK_ACCEPTED = auto()
    KNOCK_REFUSED = auto()


class Knock:
    """
    Basic class to keep track of the state of a Knock
    """
    state: KnockState  # State of the room
    # Recipient of the room has to be saved client side so we can know afterward who is talking in the room
    recipient: Identity

    def __init__(self, recipient: Identity):
        self.recipient = recipient
        self.state = KnockState.KNOCKING

