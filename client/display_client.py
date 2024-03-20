from abc import ABC

from client.client import Client
from display.pad_curses import PadCurses
from display.simple_curses import SimpleCurses
from models.identity import Identity


class DisplayClient(Client, ABC):
    display: SimpleCurses

    def __init__(self, identity: Identity, name: str = "DIOXANE"):
        super().__init__(identity, name)

        self.display = PadCurses(self)

    def _exit(self, code: int = 0):
        self.display.exit()
        super()._exit(code)
