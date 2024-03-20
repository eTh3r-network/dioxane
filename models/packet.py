from enum import IntEnum

from exceptions.exceptions import MalformedPacketException, EndOfEnumerator
from misc.hex_enumerator import read_bytes, int_to_bytes, str_to_bytes, bytes_to_str, bytes_to_int


class PacketCode(IntEnum):
    HEY = 0x0531b00b
    ACK = 0xa0
    SEND_KEY = 0x0e1f

    KNOCK_SEND = 0xee
    KNOCK_RECIEVE = 0xae
    KNOCK_RESPONSE = 0xab
    ROOM_NEW = 0xac
    ROOM_CLOSE = 0xaf

    KEY_REQUEST = 0xba
    KEY_RESPONSE = 0xa0ba
    KEY_UNKNOWN = 0xca

    MESSAGE_SEND = 0xda

    ERR_WRONG_PACKET_LENGTH = 0xa1
    ERR_WRONG_PACKET_ID = 0xa2
    ERR_UNSUPPORTED_VERSION = 0xa4
    ERR_INCOMPLETE_KEY = 0xaa
    ERR_KEY_MALFORMED = 0xab
    ERR_KEY_PAYLOAD_MALFORMED = 0xac
    ERR_MALFORMATION = 0xba
    ERR_OUT_OF_PATH = 0xe0
    ERR_UNKNOWN_PACKET_ID = 0xfd
    ERR_NOT_IMPLEMENTED = 0xfe
    ERR_FAULTY_READING = 0xff


class Packet:
    """
    Eth3r Packet
    """
    code: PacketCode
    options: list[bytearray]

    def __init__(self, payload: bytearray | bytes | int | str | PacketCode, options: list[bytearray] = None):

        if options is None:
            options = []
        self.options = options.copy()
        bytesEnumerator: enumerate

        if type(payload) is PacketCode:
            self.code = payload

        if type(payload) is int:
            try:
                payload = int_to_bytes(payload)
            except ValueError:
                raise MalformedPacketException("Non-hexadecimal number in payload")

        if type(payload) is str:
            try:
                payload = str_to_bytes(payload)
            except ValueError:
                raise MalformedPacketException("Non-hexadecimal number in payload")

        if type(payload) is bytearray or type(payload) is bytes:
            bytesEnumerator = enumerate(payload)
            self._set_code_from_enumerator(bytesEnumerator)
            try:
                self._set_options_from_enumerator(bytesEnumerator)
            except EndOfEnumerator:
                raise MalformedPacketException("Packet options doesn't match expected size of "
                                               + self.code.name + " : " + bytes_to_str(payload))

    def _set_code_from_enumerator(self, bytesEnumerator):
        code = bytearray(b'')
        while bytes_to_int(code) not in PacketCode.value2member_map_:
            try:
                code = read_bytes(bytesEnumerator, 1, code)
            except EndOfEnumerator:
                raise MalformedPacketException("PacketCode doesn't correspond to an implemented code : "
                                               + bytes_to_str(code))
        self.code = PacketCode(bytes_to_int(code))

    def _set_options_from_enumerator(self, bytesEnumerator):
        match self.code:
            case PacketCode.HEY:
                self.options += read_bytes(bytesEnumerator, 2)

            case PacketCode.ACK:
                try:
                    nextByte = read_bytes(bytesEnumerator)

                    # An KEY_RESPONSE PacketCode can be confused with an ACK as they both start with 0xa0
                    # Thus ACK followed by 0xba are converted into a simple KEY_RESPONSE
                    if nextByte == int_to_bytes(0xba):
                        self.code = PacketCode.KEY_RESPONSE
                    else:
                        while True:
                            try:
                                nextByte = read_bytes(bytesEnumerator, 1, value=nextByte)
                            except EndOfEnumerator:
                                break
                        self.options.append(nextByte)
                except EndOfEnumerator:
                    pass

            case PacketCode.SEND_KEY | PacketCode.KEY_RESPONSE:
                key_length = read_bytes(bytesEnumerator, 2)
                self.options += [key_length, read_bytes(bytesEnumerator, key_length)]

            case PacketCode.KNOCK_SEND | PacketCode.KNOCK_RECIEVE | PacketCode.ROOM_CLOSE | PacketCode.KEY_REQUEST \
                 | PacketCode.KEY_UNKNOWN:
                key_length = read_bytes(bytesEnumerator, 1)
                self.options += [key_length, read_bytes(bytesEnumerator, key_length)]

            case PacketCode.KNOCK_RESPONSE:
                response = read_bytes(bytesEnumerator, 1)
                key_length = read_bytes(bytesEnumerator, 1)
                self.options += [response, key_length, read_bytes(bytesEnumerator, key_length)]

            case PacketCode.ROOM_NEW:
                room_length = read_bytes(bytesEnumerator, 1)
                room_id = read_bytes(bytesEnumerator, room_length)

                key_length = read_bytes(bytesEnumerator, 1)
                key_id = read_bytes(bytesEnumerator, key_length)

                self.options += [room_length, room_id, key_length, key_id]

            case PacketCode.MESSAGE_SEND:
                room_length = read_bytes(bytesEnumerator, 1)

                room_id = read_bytes(bytesEnumerator, room_length)
                encryption = read_bytes(bytesEnumerator, 1)

                payload = bytearray(b'')
                while True:
                    try:
                        payload = read_bytes(bytesEnumerator, 1, value=payload)
                    except EndOfEnumerator:
                        break

                self.options += [room_length, room_id, encryption, payload]

            # Error
            case PacketCode.ERR_WRONG_PACKET_LENGTH | PacketCode.ERR_WRONG_PACKET_ID | \
                 PacketCode.ERR_UNSUPPORTED_VERSION | PacketCode.ERR_INCOMPLETE_KEY | PacketCode.ERR_KEY_MALFORMED | \
                 PacketCode.ERR_KEY_PAYLOAD_MALFORMED | PacketCode.ERR_MALFORMATION | PacketCode.ERR_OUT_OF_PATH | \
                 PacketCode.ERR_UNKNOWN_PACKET_ID | PacketCode.ERR_NOT_IMPLEMENTED | PacketCode.ERR_FAULTY_READING:
                raise NotImplementedError(f"Reading a packet {self.code.name} is not yet implemented")

    def to_bytes(self):
        return int_to_bytes(self.code) + b"".join(self.options)

    def __str__(self):
        return "<Packet " + self.code.name + " " + " ".join(list(map(hex, self.options))) + ">"
