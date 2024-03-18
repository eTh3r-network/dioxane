from exceptions.exceptions import UnknownRecipient
from misc.hex_enumerator import bytes_to_int, bytes_to_str
from models.identity import Identity


class IdentityManager:

    contactsByName: dict[str, str]  # Map contacts name to their key_id
    contactsByKey: dict[str, Identity]  # Map key_id to Identity

    def __init__(self):
        self.contactsByName = {}
        self.contactsByKey = {}

    def getIdentity(self, identity: str | bytearray) -> Identity:
        """
        Fetch the contact list for an Identity
        :param identity: Name or key_id of the identity
        :return: Identity
        """
        key_id: str = ""

        if type(identity) is str:
            # Trying by name
            for name in self.contactsByName.keys():
                if identity in name:
                    return self.contactsByKey[self.contactsByName[name]]

            if identity[0:2] == "0x":
                key_id = identity[2:]

        if type(identity) is bytearray:
            key_id = bytes_to_str(identity)[2:]

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
        key_id: str = bytes_to_str(identity.key_id)[2:]
        self.contactsByKey[key_id] = identity
        self.contactsByName[identity.name] = key_id
