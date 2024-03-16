from exceptions.exceptions import EndOfEnumerator


def int_to_bytes(value: int) -> bytearray:
    """
    Cast an int into a bytearray
    :param value:
    :return:
    """
    hexstr = hex(value)
    if len(hexstr) % 2 == 1:
        hexstr = "0x0" + hexstr[2:]
    return str_to_bytes(hexstr)


def bytes_to_int(value: bytearray) -> int:
    """
    Cast a byte array into int
    :param value: Byte array
    :return: Int
    """
    return int.from_bytes(value, 'big')


def str_to_bytes(value: str) -> bytearray:
    """
    Cast a hex string into a bytearray
    :param value: String containing hex digits, starting with "0x" or not
    :return: Byte array
    """
    if value[0:2] == '0x':
        return bytearray.fromhex(value[2:])
    else:
        return bytearray.fromhex(value)


def bytes_to_str(value: bytearray) -> str:
    """
    Cast a bytearray into a hex string
    :param value: Byte array
    :return: String formated as 0x....
    """
    return hex(int.from_bytes(value, 'big'))


def _read_bytes(bytesEnumerator: enumerate, size: int | bytearray = 1, value: bytearray = bytearray(0)) -> bytearray:
    """
    Read bytes from an enumerator and return them as a bytearray
    :param bytesEnumerator: enumerator
    :param size: how many bytes to read from
    :param value: precedent bytes to add in the bytearray returned (before the read bytes)
    :return: Byte array
    """
    if type(size) == bytearray:
        size = bytes_to_int(size)

    _value = value.copy()

    for i in range(size):

        pos, nextByte = next(bytesEnumerator, (None, None))

        if nextByte is None:
            raise EndOfEnumerator

        _value.append(nextByte)

    return _value
