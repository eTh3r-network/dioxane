from threading import Thread

from client.client import Client
from client.simple_client.PacketGenerator import PacketGenerator
from client.simple_client.identity_manager import IdentityManager
from client.simple_client.simple_client_connection_state import Server, ConnectionState
from display.pad_curses import PadCurses
from misc.hex_enumerator import bytes_to_str, bytes_to_int, str_to_bytes
from models.identity import Identity
from models.message import Message, MessageType
from models.packet import Packet, PacketCode

from connection.fake_server import FakeConnection

from display.display import Display

from client.simple_client.input import Input
from exceptions.exceptions import MalformedPacketException, UnknownRecipient
from models.room import RoomState, Room


class SimpleClient(Client, IdentityManager):
    """
    SimpleClient is a basic implementation of Eth3r.
    It works with a Display to output message and input prompt
    It works along a Server, which handle a connection and the state of Eth3r's connection
    """
    display: Display  # TOREWORK : SimpleClient require at least Simple Curses but
    server: Server
    input: Input

    # Mapping Id to Room (/!\ this is a weird way to handle room and may lead to many confusions. Will be improved as
    # eth3r improves its room system)
    rooms: dict[Identity, Room]
    roomRecipients: dict[Identity, Identity] # Map Room id to their Recipient

    serverThread: Thread
    intputThread: Thread

    packetGenerator: PacketGenerator

    auto_connect: bool = False

    def __init__(self, identity: Identity, name: str = "DIOXANE"):
        super().__init__(identity, name)

        self.display = PadCurses(self)
        self.packetGenerator = PacketGenerator(self)

        # Start the server
        self.server = Server(FakeConnection(), self)
        self.server.connection.attach(self)
        self.serverThread = Thread(target=self.server.connection.start_listening, daemon=True)
        self.serverThread.start()

        # Start the input thread
        self.input = Input(self)
        self.intputThread = Thread(target=self.input.start_listening)
        self.intputThread.start()

        self.rooms = {}
        self.roomRecipients = {}
        self.contactsByName = {}
        self.contactsByKey = {}

        if self.auto_connect:
            self.connect()

    def send_pck(self, pck: bytearray | Packet):
        if type(pck) is Packet:
            pck = pck.to_bytes()
        self.display.display_debug("Sent " + bytes_to_str(pck))
        self.server.connection.send(pck)

    def receive_pck(self, pck: bytearray):
        self.display.display_debug("Received " + bytes_to_str(pck))
        try:
            if bytes_to_int(pck) == 0x0:
                self._exit(0)

            self.interpret(Packet(pck))
        except MalformedPacketException as e:
            self.display.display_error(str(e))
        except NotImplementedError as e:
            self.display.display_error(str(e))
        except BaseException as e:
            self.display.display_error(f"Unexpected error while reading {bytes_to_str(pck)} : {type(e)} {e}")

    def interpret(self, packet: Packet):
        match packet.code:
            case PacketCode.ACK:
                self._match_ack_to_something(packet)

            case PacketCode.KNOCK_RECIEVE:
                key_id_length, key_id = packet.options
                try:
                    recipient = self.getIdentity(key_id)

                    self.display.display_log(
                        f"Recieved a knock request from {recipient}.")
                except UnknownRecipient:
                    recipient = Identity(key_id=key_id, key_id_length=key_id_length)
                    self.registerIdentity(recipient)
                    self.display.display_log(
                        f"Recieved a knock request from {recipient} but we don't know who it is.")
                    self.display.display_debug(f"We can use /rename {recipient} <name> to set their name")

                self.rooms[recipient] = Room(recipient)
                self.rooms[recipient].state = RoomState.KNOCKING_ACK

            case PacketCode.KNOCK_RESPONSE:
                accepted = packet.options[0] == b'\x01'
                key_id_length, key_id = packet.options[1], packet.options[2]
                try:
                    recipient = self.getIdentity(key_id)
                except UnknownRecipient:
                    self.display.display_error(f"Recieved a knock response from {bytes_to_str(key_id)} but we don't know who it is.")
                    return self.display.display_debug(f"Have we ever ask them in the first place ?")

                if recipient not in self.rooms:
                    return self.display.display_error(f"Recieving a {'positive' if accepted else 'negative'}"
                                                      f" knocking response from {recipient}"
                                                      f" but never asked them in the first place")

                if self.rooms[recipient].state == RoomState.KNOCKING:
                    self.display.display_debug(f'Server forwarded {recipient}\'s response to our knock but we never'
                                               f'recieved ACK from the server itself. We won\'t mind and pretend it did')
                    self.rooms[recipient].state = RoomState.KNOCKING_ACK

                if self.rooms[recipient].state == RoomState.KNOCKING_ACK:
                    if accepted:
                        self.rooms[recipient].state = RoomState.KNOCK_ACCEPTED
                        return self.display.display_success(f"{recipient} accepted our knock")
                    else:
                        self.rooms[recipient].state = RoomState.KNOCK_REFUSED
                        return self.display.display_error(f"{recipient} refused our knock")
                else:
                    return self.display.display_error(f"Recieving a {'positive' if accepted else 'negative'}"
                                                      f" knocking response from {recipient}"
                                                      f" but we were {self.rooms[recipient].state}")
            case PacketCode.ROOM_NEW:
                room_key_length, room_key, key_id_length, key_id = packet.options
                try:
                    recipient = self.getIdentity(key_id)
                except UnknownRecipient:
                    self.display.display_error(
                        f"Recieved a room with {bytes_to_str(key_id)} but we don't know who it is.")
                    return self.display.display_debug(f"Have we ever ask them in the first place ?")

                if recipient not in self.rooms:
                    self.display.display_error(f"Recieving a room with {recipient}"
                                                      f" but never asked them in the first place")
                    self.display.display_log(f"Room with {recipient} joined anyway")
                    self.rooms[recipient] = Room(recipient)
                    self._join_room(recipient, room_key)
                    return

                match self.rooms[recipient].state:
                    case RoomState.KNOCK_REFUSED:
                        self.display.display_error(f"Server created a room with {recipient} despite we/they refused.")
                        self.display.display_log(f"Joining room with {recipient} anyway")
                    case RoomState.KNOCK_ACCEPTED:
                        self.display.display_log(f"Room with {recipient} successfully joined")
                    case _:
                        self.display.display_error(f"Server created a room with {recipient}"
                                                   f"but we were {self.rooms[recipient].state}")
                        self.display.display_log(f"Joining room with {recipient} anyway")

                self._join_room(recipient, room_key)

            case PacketCode.MESSAGE_SEND:
                room_key_length, room_key, encryption, payload = packet.options
                room_id = Identity(key_id = room_key, key_id_length=room_key_length)
                if room_id not in self.roomRecipients:
                    return self.display.display_error(f"Recieved a message in room {room_id} despite we are not in it :"
                                               f" {payload.decode('ascii')}")
                
                recipient = self.roomRecipients[room_id]
                if self.rooms[recipient].state != RoomState.IN_ROOM:
                    self.display.display_error(f"We recieved a message in room with {recipient} "
                                               f"but it was {self.rooms[recipient].state}")

                message: Message = Message(room=self.rooms[recipient],
                                           message_type=MessageType.RECEIVE,
                                           payload=payload, ack=True)
                self._display_message(message)

            case PacketCode.ROOM_CLOSE:
                room_key_length, room_key = packet.options
                room_id = Identity(key_id=room_key, key_id_length=room_key_length)
                if room_id not in self.roomRecipients:
                    return self.display.display_error(f"Server tells us it is closing room {room_id} "
                                                      f"despite we are not in it")
                recipient: Identity = self.roomRecipients[room_id]
                if self.rooms[recipient].state != RoomState.IN_ROOM:
                    self.display.display_error(f"Server tells us it is closing room with {recipient} "
                                                      f"despite the room being {self.rooms[recipient].state}")
                self.rooms[recipient].state = RoomState.ROOM_CLOSED

            case _:
                self.display.display_error(f"This version of client yet not know how to interpret {packet.code.name}")

    def _join_room(self, recipient: Identity, room_id: bytearray):
        room_id = Identity(name=f"Room with {recipient.name}", key_id=room_id)
        self.roomRecipients[room_id] = recipient
        self.rooms[recipient].state = RoomState.IN_ROOM
        self.rooms[recipient].id = room_id

    def _match_ack_to_something(self, packet: Packet):
        """
        Find what is acknoledged by an ACK Packet. In fact, it will acknoledge the first task that was waiting for it.
        Missing Packet can led to a missing acknoledgement and further ACK will be missunterpreted.
        To fix in the eth3r protocol
        :param packet: ACK Packet
        """
        if self.server.state == ConnectionState.CONNECTION_INITIALIZED_VERSION:
            return self.send_key()

        if self.server.state == ConnectionState.CONNECTION_INITIALIZED_KEY:
            return self._validate_connection()

        for room in self.rooms.values():
            if room.state == RoomState.KNOCKING:
                room.state = RoomState.KNOCKING_ACK
                return self.display.display_debug("Knock ack by server")

            for message in room.messages:
                if not message.ack:
                    message.ack = True
                    return self.display.update_message(message)

        self.display.display_debug(f"Received unexpected ACK : {packet}")

    def connect(self):
        """
        Send a HEY packet to the server
        """
        try:
            self.display.display_log(f"Connecting as {self.identity}")
            self.send_pck(self.packetGenerator.get_hey_packet())
            self.server.state = ConnectionState.CONNECTION_INITIALIZED_VERSION
        except BaseException as e:
            self.display.display_error(f"Can't connect to server : {str(e)}")

    def send_key(self):
        """
        Send a Key packet to the server
        """
        try:
            self.display.display_debug(f"Send my key : {bytes_to_str(self.identity.key)}")
            self.send_pck(self.packetGenerator.get_send_key_packet())
            self.server.state = ConnectionState.CONNECTION_INITIALIZED_KEY
        except BaseException as e:
            self.display.display_error(f"Can't connect to server : {str(e)}")

    def _validate_connection(self):
        """
        Validate a connection to the server
        """
        self.display.display_success("Connected")
        self.server.state = ConnectionState.CONNECTED

    def knock(self, recipient: Identity):
        """
        Send a Knock to someone
        :param recipient: Recipient to knock
        """
        self.display.display_log(f'Knocking {recipient}')
        self.rooms[recipient] = Room(recipient)
        self.rooms[recipient].state = RoomState.KNOCKING
        self.send_pck(self.packetGenerator.get_knock_packet(recipient))

    def _display_message(self, message: Message):
        """
        Display a message in a room
        :param message: Message to display
        """
        message.room.add_message(message)
        self.display.display_message(message)

    def send_message_to(self, recipient: Identity, payload: bytearray | str):
        """
        Send a message to someone
        :param recipient: Recipient of the message
        :param payload: payload
        """
        if recipient not in self.rooms:
            return self.display.display_error(f"Room with {recipient} doesn't exists")

        if self.rooms[recipient].state != RoomState.IN_ROOM:
            return self.display.display_error(f"Room with {recipient} isn't ready : {self.rooms[recipient].state}")

        message: Message = Message(sender=self.identity, room=self.rooms[recipient], message_type=MessageType.SENT,
                                   payload=payload, ack=False)
        self._display_message(message)
        self.send_pck(self.packetGenerator.get_send_message_packet(message))

    def command(self, text: str):
        """
        Execute a command
        :param text: Command
        """
        options = text.split(" ")
        command = options.pop(0)
        self._command(command, options)

    def _command(self, command: str, options: list[str]):
        """
        Execute a command
        :param command: Command name
        :param options: Options list
        :return:
        """
        match command:
            case 'knock':
                try:
                    self.knock(self.getIdentity(options[0]))
                except UnknownRecipient as e:
                    self.display.display_error("Unknown recipient : " + str(e))
                except BaseException as e:
                    self.display.display_error(e)

            case 'echo':
                if len(options) < 1:
                    return self.display.display_error("echo require a text to display")
                self.display.display_message(' '.join(options))

            case 'send':
                if len(options) < 2:
                    return self.display.display_error("send require two arguments : <recipient> and a message")
                try:
                    room_id = self.getIdentity(options.pop(0))
                except UnknownRecipient as e:
                    return self.display.display_error("Unknown recipient : " + str(e))

                text = " ".join(options)
                self.send_message_to(room_id, text)

            case 'connect':
                self.connect()

            case 'server':
                self.server.connection.receive(b''.join(map(str_to_bytes, options)))

            case 'list':
                if len(options) < 1:
                    options = ['contacts']
                match options[0]:
                    case 'contacts':
                        for contact in self.contactsByKey.values():
                            self.display.display_log(f"{contact} : {bytes_to_str(contact.key_id)}")
                    case 'rooms':
                        for room in self.rooms.values():
                            self.display.display_log(f"{room.name} : {room.state}")
            case 'help':
                self.display.display_debug("connect")
                self.display.display_debug("knock <recipient> <message>")
                self.display.display_debug("send <recipient> <message>")
                self.display.display_debug("list <contacts/rooms>")
                self.display.display_debug("server <pck>")
                self.display.display_debug("echo <message>")
            case _:
                self.display.display_error("Unknown command")
                self.display.display_log(command)

    def _exit(self, code: int = 0):
        self.display.exit()
        super()._exit(code)
