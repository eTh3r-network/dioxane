from misc.hex_enumerator import bytes_to_str, int_to_bytes


class Identity:
    """
    Hold the information about a key pair
    """
    name: str
    key: bytearray
    key_length: int
    key_id: bytearray
    key_id_length: int

    def __init__(self, key_id_length: int, key_id: int | bytearray,
                 key_length: int = None, key: int | bytearray = None,
                 name: str = None):
        if type(key_id) == int:
            key_id = key_id.to_bytes(key_id_length, 'big')
        if type(key) == int:
            key = key.to_bytes(key_length, 'big')

        self.name = name or bytes_to_str(key_id)
        self.key = key
        self.key_length = key_length
        self.key_id = key_id
        self.key_id_length = key_id_length

    def set_key(self, length: int, key: int):
        self.key_length = length
        self.key = key

    def get_key_bytes(self):
        return int_to_bytes(self.key_length).append(self.key)

    def get_key_pair(self) -> list[bytearray]:
        return [int_to_bytes(self.key_length), self.key]

    def get_key_id_bytes(self):
        return int_to_bytes(self.key_id_length).append(self.key_id)

    def get_key_id_pair(self) -> list[bytearray]:
        return [int_to_bytes(self.key_id_length), self.key_id]

    def __repr__(self):
        if self.key is None:
            return f"[{self.name} : {bytes_to_str(self.key_id)} -> ???]"
        else:
            return f"[{self.name} : {bytes_to_str(self.key_id)} -> {bytes_to_str(self.key)}]"

    def __str__(self):
        return self.name

    def __hash__(self):
        return hash(self.key_id)
