from client.client import Client
from models.identity import Identity
from models.packet import Packet, PacketCode
from models.room_message import RoomMessage


class PacketGenerator:
    client: Client

    def __init__(self, client: Client):
        self.client = client

    def get_hey_packet(self) -> Packet:
        """
        Build a Hey packet to connect the client to the server
        :return: Hey Packet
        """
        return Packet(PacketCode.HEY, [self.client.ether_version.to_bytes(2, 'big')])

    def get_send_key_packet(self) -> Packet:
        """
        Build a Key Packet
        :return: Key Packet
        """
        return Packet(PacketCode.SEND_KEY, self.client.identity.get_key_pair())

    # noinspection PyMethodMayBeStatic
    def get_send_message_packet(self, message: RoomMessage) -> Packet:
        """
        Build a Message Packet
        :param message: Message to send
        :return: Message Send Packet
        """
        return Packet(PacketCode.MESSAGE_SEND, message.room.room_id.get_key_id_pair().append(message.payload))

    # noinspection PyMethodMayBeStatic
    def get_knock_packet(self, recipient: Identity) -> Packet:
        """
        Build a Kncok Packet
        :param recipient: Client to knock
        :return: Knock Packet
        """
        return Packet(PacketCode.KNOCK_SEND, recipient.get_key_id_pair())
