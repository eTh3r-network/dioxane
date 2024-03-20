from abc import ABC
from threading import Thread

from client.display_client import DisplayClient
from client.simple_client.input import Input
from models.identity import Identity


class IoClient(DisplayClient, ABC):
    input: Input
    intputThread: Thread

    def __init__(self, identity: Identity, name: str = "DIOXANE"):
        super().__init__(identity, name)

        # Start the input thread
        self.input = Input(self)
        self.intputThread = Thread(target=self.input.start_listening)
        self.intputThread.start()
