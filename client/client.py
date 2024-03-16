from abc import ABC, abstractmethod

from models.identity import Identity


class Client(ABC):
    """
    Abstract class to define the basics of a Dioxane Client
    """

    # Client information, doesn't interfer with Eth3r
    name: str
    version: str = "0.1"

    ether_version: int = 0x0001  # Which version of Eth3r it implements
    identity: Identity  # Key used by the client

    def __init__(self, identity: Identity, name: str = "DIOXANE"):
        """
        Instantiate a client
        :param identity: Key and KeyId of the client
        :param name: Name of the client
        """
        self.identity = identity
        self.name = name

    @abstractmethod
    def receive_pck(self, pck: bytearray):
        """
        Process packet recieve from the server
        :param pck: Packet
        """
        pass
    
    @abstractmethod
    def send_pck(self, pck: bytearray):
        """
        Send Packet to server
        :param pck: bytes to send
        """
        pass

    def _exit(self, code: int = 0):
        """
        Close the client
        :param code: error code
        """
        exit(code)
