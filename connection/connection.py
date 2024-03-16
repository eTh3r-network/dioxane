from abc import ABC, abstractmethod

from client.client import Client


class Connection(ABC):
    """
    Abstract class that represent a way to connect to a server, send and receive packets.
    It implements the Observer / Observable pattern
    """
    """
    Remark: this class is a bit overkill, since we probably won't have multiple client listening to the same connection
    """
    _observers: list[Client]

    def __init__(self):
        self._observers = []

    def attach(self, observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, pck: bytearray):
        for observer in self._observers:
            observer.receive_pck(pck)

    @abstractmethod
    def start_listening(self):
        """
        Activate the connection and listen for incomming packet
        """
        raise NotImplementedError

    @abstractmethod
    def send(self, pck: bytearray):
        """
        Send packet over the connection
        :param pck: bytes to send
        :return:
        """
        raise NotImplementedError
