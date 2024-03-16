import curses
from enum import IntEnum, auto

from client.client import Client
from display.display import Display
from models.message import Message, MessageType


class SimpleCursesColor(IntEnum):
    CLASSIC = auto()
    MESSAGE_SEND = auto()
    MESSAGE_RECIEVE = auto()
    SUCCESS = auto()
    ERROR = auto()
    DEBUG = auto()
    LOG = auto()


class SimpleCurses(Display):
    """
    
    """
    width: int
    height: int
    message_count: int = 1
    prompt_cursor: int = 0

    color_variation: dict[SimpleCursesColor]

    def __init__(self, client: Client):
        super().__init__(client)

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        if curses.has_colors():
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(SimpleCursesColor.CLASSIC, curses.COLOR_WHITE, -1)
            curses.init_pair(SimpleCursesColor.MESSAGE_SEND, curses.COLOR_BLUE, -1)
            curses.init_pair(SimpleCursesColor.MESSAGE_RECIEVE, curses.COLOR_CYAN, -1)
            curses.init_pair(SimpleCursesColor.SUCCESS, curses.COLOR_GREEN, -1)
            curses.init_pair(SimpleCursesColor.ERROR, curses.COLOR_RED, -1)
            curses.init_pair(SimpleCursesColor.DEBUG, curses.COLOR_YELLOW, -1)
            curses.init_pair(SimpleCursesColor.LOG, curses.COLOR_WHITE, -1)
        self.color_variation = {SimpleCursesColor.CLASSIC: 0, SimpleCursesColor.MESSAGE_SEND: 0,
                                SimpleCursesColor.MESSAGE_RECIEVE: 0, SimpleCursesColor.SUCCESS: curses.A_BOLD,
                                SimpleCursesColor.DEBUG: 0, SimpleCursesColor.ERROR: curses.A_BOLD,
                                SimpleCursesColor.LOG: curses.A_ITALIC}

        self.stdscr.keypad(True)
        # self.stdscr.leaveok(True)
        self.width = curses.COLS
        self.height = curses.LINES

        self._display_box()

    def _display_line(self, height: int = 0, left_txt: str = "", middle_txt: str = "", right_txt: str = "",
                      space_between: bool = True, fillingchar: str = "="):
        first_half: int = int(self.width / 2) - int(len(middle_txt) / 2) - len(left_txt) - (2 if space_between else 0)
        second_half: int = self.width - len(left_txt + middle_txt + right_txt) - (4 if space_between else 0) \
                           - first_half - 1

        self.stdscr.addstr(height, 0, left_txt + (" " if space_between else "")
                           + fillingchar * first_half + (" " if space_between else "")
                           + middle_txt + (" " if space_between else "")
                           + fillingchar * second_half + (" " if space_between else "")
                           + right_txt)
        self._update_cursor()
        self.stdscr.refresh()


    def _display_box(self):
        self._display_line(height=0, middle_txt=self.client.name, right_txt=self.client.version)
        self._display_line(height=self.height - 1, left_txt="> ", fillingchar=" ")

    def update_prompt(self, prompt: str, cursor: int):
        self.prompt_cursor = cursor
        self._display_line(height=self.height - 1, left_txt="> " + prompt, fillingchar=" ")
        self._update_cursor()

    def _display(self, text: str, color: SimpleCursesColor):
        self.stdscr.addstr(self.message_count, 0, text, curses.color_pair(color) | self.color_variation[color])
        self.message_count += 1
        self._update_cursor()
        self.stdscr.refresh()

    def display_message(self, message: Message | str):
        if type(message) is str:
            return self.display_message(Message(payload=message, message_type=MessageType.LOG))

        header = ""
        color = SimpleCursesColor.CLASSIC

        if message.message_type == MessageType.ERROR:
            header = f"/!\\ "
            color = SimpleCursesColor.ERROR

        if message.message_type == MessageType.LOG:
            header = f"- "
            color = SimpleCursesColor.LOG

        if message.message_type == MessageType.DEBUG:
            header = f"~ "
            color = SimpleCursesColor.DEBUG

        if message.message_type == MessageType.SUCCESS:
            header = f"[✔] "
            color = SimpleCursesColor.SUCCESS

        if message.message_type == MessageType.SENT:
            header = f"[{message.recipient}] "
            color = SimpleCursesColor.MESSAGE_SEND

        if message.message_type == MessageType.RECEIVE:
            if message.sender:
                header = f"[{message.sender}] "
            elif message.room:
                header = f"[{message.room}]"
            color = SimpleCursesColor.MESSAGE_RECIEVE

        self._display(header + bytes.fromhex(hex(message.payload)[2:]).decode('utf-8'), color)

    def display_error(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.ERROR))

    def display_log(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.LOG))

    def display_debug(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.DEBUG))

    def display_success(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.SUCCESS))

    def _update_cursor(self, y=None, x=None):
        if y is None:
            y = self.height - 1
        if x is None:
            x = self.prompt_cursor + 2
        self.stdscr.move(y, x)

    def exit(self):
        curses.nocbreak()
        curses.echo()
        self.stdscr.keypad(False)
        curses.endwin()
