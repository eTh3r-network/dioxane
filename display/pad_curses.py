import curses

from client.client import Client
from display.simple_curses import SimpleCurses, SimpleCursesColor
from models.message import MessageType
from models.room_message import RoomMessage


class PadCurses(SimpleCurses):
    """
    Technical improvement to Simple Curses to use pad.
    This allows scrolling
    """
    message_pad_height: int = 100
    message_pad: "_CursesWindow" = None
    prompt_windows: "_CursesWindow" = None
    header_windows: "_CursesWindow" = None
    windows_scroll: int = 0
    windows_scroll_jump: bool = False

    def __init__(self, client: Client):
        super().__init__(client)
        self.message_pad = curses.newpad(self.message_pad_height, self.width)
        # self.stdscr.border('│', '│', '─', '─', '┌', '┐', '└', '┘')
        self.header_windows = curses.newwin(1, self.width, 0, 0)
        self.prompt_windows = curses.newwin(1, self.width, self.height - 1, 0)
        self.prompt_windows.keypad(True)
        self.prompt_windows.nodelay(True)
        self.input_windows = self.prompt_windows
        self._display_base_gui()

    def _display_all_messages(self):
        self.message_pad.clear()
        i: int = 0
        for message in self.messages:
            self._display_message(message, i)
            i += 1

    def _display(self, text: str, height: int, color: SimpleCursesColor):
        self.message_pad.addstr(height, 0, text, curses.color_pair(color) | self.color_variation[color])
        self._update_cursor()
        self._update_scroll()

    def scroll(self, scroll_delta: int = 0):
        if scroll_delta != 0:
            self.windows_scroll = max(min(0, len(self.messages)), self.windows_scroll + scroll_delta)
        self._update_scroll()

    def _update_scroll(self):
        # noinspection PyArgumentList
        self.message_pad.noutrefresh(self.windows_scroll, 0, 1, 0, self.height - 2, self.width - 1)
        curses.doupdate()

    def _display_base_gui(self):
        """
        Display the client base GUI
        """
        if self.header_windows is None:
            return
        self._display_line(height=0, middle_txt=self.client.name, right_txt=self.client.version,
                           windows=self.header_windows)
        self._display_all_messages()
        self._display_line(height=0, left_txt="> ", fillingchar=" ", windows=self.prompt_windows)

    def update_prompt(self, prompt: str, cursor: int):
        self.prompt_cursor = cursor
        self._display_line(height=0, left_txt="> " + prompt, fillingchar=" ", windows=self.prompt_windows)
        self._update_cursor()

    def display_message(self, message: RoomMessage | str):
        if type(message) is str:
            return self.display_message(RoomMessage(payload=message, message_type=MessageType.LOG))

        self.messages.append(message)
        if self.windows_scroll_jump or self.windows_scroll + 1 == len(self.messages) - (self.height - 2):
            self.windows_scroll = max(0, len(self.messages) - (self.height - 2))

        if len(self.messages) > self.message_pad_height:
            self.messages = self.messages[self.message_pad_height - self.height:self.message_pad_height]
            self.windows_scroll -= self.message_pad_height - self.height
            self._display_all_messages()
        else:
            self._display_message(message, len(self.messages) - 1)

    def _update_cursor(self, y=0, x=None):
        if x is None:
            x = self.prompt_cursor + 2
        self.prompt_windows.move(y, x)
