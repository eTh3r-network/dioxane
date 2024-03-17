from threading import Thread

from client.client import Client
from client.simple_client.simple_client_connection_state import Server, ConnectionState
from display.pad_curses import PadCurses
from misc.hex_enumerator import bytes_to_str, bytes_to_int, str_to_bytes
from models.identity import Identity
from models.message import Message
from models.packet import Packet, PacketCode

from connection.fake_server import FakeConnection

from display.display import Display
from display.simple_curses import SimpleCurses

from client.simple_client.input import Input
from exceptions.exceptions import MalformedPacketException, UnknownRecipient
from models.room import RoomState, Room


class SimpleClient(Client):
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

    contactsByName: dict[str, int]  # Map contacts name to their key_id
    contactsByKey: dict[int, Identity]  # Map key_id to Identity

    serverThread: Thread
    intputThread: Thread

    def __init__(self, identity: Identity, name: str = "DIOXANE"):
        super().__init__(identity, name)

        self.display = PadCurses(self)

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
        self.room_ids = {}
        self.contactsByName = {}
        self.contactsByKey = {}

    def send_pck(self, pck: bytearray):
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
            self.display.display_error(f"Unexpected error while reading {bytes_to_str(pck)} : {e}")

    def interpret(self, packet: Packet):
        match packet.code:
            case PacketCode.ACK:
                self._match_ack_to_something(packet)
            case PacketCode.KNOCK_RESPONSE:
                accepted = packet.options[0] == b'1'
                key_id_length, key_id = packet.options[1][0], packet.options[1][1:]
                recipient = self.getIdentity(key_id)
                if recipient not in self.rooms:
                    return self.display.display_error(f"Recieving a {'positive' if accepted else 'negative'}"
                                                      f" knocking response from {recipient}"
                                                      f" but never asked them in the first place")

                if self.rooms[recipient].state == RoomState.KNOCKING:
                    self.display.display_debug(f'Server forwarded {recipient}\'s response to our knock but we never'
                                               f'recieved ACK from the server itself. We won\'t mind and pretend it did')
                    self.rooms[recipient].state = RoomState.KNOCKING_ACK

                if self.rooms[recipient].state == RoomState.KNOCKING_ACK:
                    self.rooms[recipient].state = RoomState.KNOCK_ACCEPTED if accepted else RoomState.KNOCK_REFUSED
                else:
                    return self.display.display_error(f"Recieving a {'positive' if accepted else 'negative'}"
                                                      f" knocking response from {recipient}"
                                                      f" but we were {self.rooms[recipient].state}")

            case _:
                self.display.display_error(f"{hex(packet.code)} reception not yet implemented")

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

        self.display.display_debug(f"Received unexpected ACK : {packet}")

    def connect(self):
        """
        Send a HEY package to the server
        """
        try:
            self.display.display_log(f"Connecting as {self.identity}")
            self.send_pck(self.server.get_hey_packet())
            self.server.state = ConnectionState.CONNECTION_INITIALIZED_VERSION
        except BaseException as e:
            self.display.display_error(f"Can't connect to server : {str(e)}")

    def send_key(self):
        """
        Send a Key package to the server
        """
        self.display.display_debug(f"Send my key : {bytes_to_str(self.identity.key)}")
        self.send_pck(self.server.get_send_key_packet())
        self.server.state = ConnectionState.CONNECTION_INITIALIZED_KEY

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
        self.send_pck(Packet(PacketCode.KNOCK_SEND, recipient.get_key_id_pair()))

    def add_message_in_room(self, room_id: int, message: Message):
        """
        Display a message in a room
        :param room_id: Room id
        :param message: Message to display
        """
        """
        NOT_TESTED
        """
        self.rooms[room_id].add_message(message)
        self.display.display_message(message)

    def send_message_in(self, room_id: int, payload: bytearray):
        """
        Send a message in a room
        :param room_id: Room id
        :param payload: payload
        :return:
        """
        """
        NOT_TESTED
        """
        if room_id not in self.rooms or self.rooms[room_id].state != RoomState.IN_ROOM:
            self.display.display_error("Room isn't ready " + room_id)
        else:
            message: Message = Message(sender=self.identity, room=self.rooms[room_id], payload=payload, ack=False)
            self.add_message_in_room(room_id, message)
            self.server.connection.send(message.get_send_package())

    def getIdentity(self, identity: str | bytearray) -> Identity:
        """
        Fetch the contact list for an Identity
        :param identity: Name or key_id of the identity
        :return: Identity
        """
        key_id: int = -1

        if type(identity) is str:
            # Trying by name
            for name in self.contactsByName.keys():
                if identity in name:
                    return self.contactsByKey[self.contactsByName[name]]

            if identity[0:2] == "0x":
                key_id = int(identity[2:], 16)
            else:
                key_id = int(identity, 16)

        if type(identity) is bytearray:
            key_id = bytes_to_int(identity)

        # Trying by key_id
        try:
            if key_id in self.contactsByKey:
                return self.contactsByKey[key_id]
        except ValueError as e:
            pass

        raise UnknownRecipient(identity)

    def registerIdentity(self, identity: Identity):
        """
        Insert an Identity in the contact list
        :param identity: Identity to register
        """
        self.contactsByKey[identity.key_id] = identity
        self.contactsByName[identity.name] = identity.key_id

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
                self.display.display_message(' '.join(options))

            case 'server':
                self.server.connection.receive(b''.join(map(str_to_bytes, options)))

            case _:
                self.display.display_error("Unknown command")
                self.display.display_log(command)

    def _exit(self, code: int = 0):
        self.display.exit()
        super()._exit(code)
