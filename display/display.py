from abc import ABC, abstractmethod

from client.client import Client
from models.room_message import RoomMessage


class Display(ABC):
    """
    Abstract class to define the bases of a Display
    It has to be able to display message and error/log/etc
    It has to be able to display the prompt as it is typed
    """
    client: Client

    def __init__(self, client: Client):
        self.client = client

    @abstractmethod
    def update_prompt(self, prompt: str, cursor: int):
        """
        Display the prompt
        :param prompt: prompt
        :param cursor: position of the cursor, from 0 to len(prompt)
        """
        raise NotImplementedError

    @abstractmethod
    def display_message(self, message: RoomMessage | str):
        raise NotImplementedError

    @abstractmethod
    def update_message(self, message: RoomMessage | str):
        raise NotImplementedError

    @abstractmethod
    def display_error(self, text: str):
        raise NotImplementedError

    @abstractmethod
    def display_log(self, text: str):
        raise NotImplementedError

    @abstractmethod
    def display_debug(self, text: str):
        raise NotImplementedError

    @abstractmethod
    def display_success(self, text: str):
        raise NotImplementedError

    @abstractmethod
    def exit(self):
        """
        Close the display
        """
        raise NotImplementedError
