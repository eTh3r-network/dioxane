from enum import Enum, auto

from client.client import Client
from connection.fake_server import FakeConnection


class ConnectionState(Enum):
    DISCONNECTED = auto()
    CONNECTION_INITIALIZED_VERSION = auto()
    CONNECTION_INITIALIZED_VERSION_ACK = auto()
    CONNECTION_INITIALIZED_KEY = auto()
    CONNECTION_INITIALIZED_KEY_ACK = auto()
    CONNECTED = auto()


class Server:
    """
    Server is a class that handle both the communication (over internet/other medium) and the state of the connection
    to the Eth3r server (I.E. whereas the client is properly authentificated or waiting for the response)
    """
    connection: FakeConnection  # A connection to operate over
    state: ConnectionState  # The state of the connection with the Eth3r server
    client: Client  # Reference back to the client
    attempt: int  # Connection attempt NOT_YET_IMPLEMENTED
    errors: list[str]  # List of error NOT_YET_IMPLEMENTED

    def __init__(self, client: Client, connection: FakeConnection = None):
        """
        Instantiate the Server, with a Disconnected state
        :param connection: Connection
        :param client: Client
        """
        if connection is None:
            connection = FakeConnection()
        self.connection = connection
        self.client = client
        self.state = ConnectionState.DISCONNECTED
