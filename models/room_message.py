from models.identity import Identity
from models.message import MessageType, Message
from models.room import Room


class RoomMessage(Message):
    """
    Message that can be in a room
    """
    room: Room  # Room where it was sent/recieved

    def __init__(self, payload: bytearray | str, sender: Identity = None, recipient: Identity = None,
                 room: Room = None, ack: bool = True, message_type: MessageType = None):
        """
        Create a message, whome payload can be define by a bytearray or a str (will be cast in ascii bytesarray)
        :param payload: Byte array or string
        :param sender: Sender
        :param recipient: Recipient
        :param room: Room
        :param ack: ACK by the server (Default is True)
        :param message_type: Type
        """
        super().__init__(payload, sender, recipient, ack, message_type)
        self.room = room
