from enum import Enum, auto

from models.identity import Identity
from models.message import Message, MessageType


class Room:
    """
    Basic class to keep track of the state of a Room
    """
    name: str  # Client side name, doesn't interfer with Eth3r
    closed: bool  # State of the room
    # Recipient of the room has to be saved client side so we can know afterward who is talking in the room
    recipient: Identity
    messages: list[Message]  # List of message in the room
    id: Identity  # Id of the room server side

    def __init__(self, recipient: Identity, id: Identity):
        self.recipient = recipient
        self.name = str(recipient)
        self.closed = False
        self.messages = []
        self.id = id

    def add_message(self, message: Message):
        """
        Add message in the room
        :param message: Message
        """
        if message.message_type is None:
            if message.recipient == self.recipient:
                message.message_type = MessageType.SENT
            if message.sender == self.recipient:
                message.message_type = MessageType.RECEIVE

        self.messages.append(message)
