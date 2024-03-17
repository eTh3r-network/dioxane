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

    messages: list[Message]
    input_windows: "_CursesWindow"

    def __init__(self, client: Client):
        super().__init__(client)

        self.stdscr = curses.initscr()
        self.input_windows = self.stdscr
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
        self.messages = []
        self.message_pad = curses.newpad(self.width, 100)

        self._display_base_gui()

    def _display(self, text: str, height: int, color: SimpleCursesColor):
        self.stdscr.addstr(height, 0, text, curses.color_pair(color) | self.color_variation[color])
        self._update_cursor()
        self.stdscr.refresh()

    def _get_line(self, left_txt: str = "", middle_txt: str = "", right_txt: str = "",
                  space_between: bool = True, fillingchar: str = "=") -> str:

        first_half: int = int(self.width / 2) - int(len(middle_txt) / 2) - len(left_txt) - (2 if space_between else 0)
        second_half: int = self.width - len(left_txt + middle_txt + right_txt) - (4 if space_between else 0) \
                           - first_half - 1
        return left_txt + (" " if space_between else "") \
               + fillingchar * first_half + (" " if space_between else "") \
               + middle_txt + (" " if space_between else "") \
               + fillingchar * second_half + (" " if space_between else "") \
               + right_txt

    def _display_line(self, height: int = 0, left_txt: str = "", middle_txt: str = "", right_txt: str = "",
                      space_between: bool = True, fillingchar: str = "=", windows=None):
        """
        Display a full line
        :param height: Position of the line
        :param left_txt: Text on the left
        :param middle_txt: Text in the middle
        :param right_txt: Text on the right
        :param space_between: Whether or not to add space around text (default is true)
        :param fillingchar: Char used to fill the line (default is =)
        """
        text: str = self._get_line(left_txt, middle_txt, right_txt, space_between, fillingchar)
        windows.addstr(height, 0, text)
        self._update_cursor()
        windows.refresh()

    def _display_all_messages(self):
        i: int = 1
        for message in self.messages:
            self._display_message(message, i)
            i += 1

    def _display_message(self, message: Message, height: int):

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

        self._display(header + message.payload.decode(), height, color)

    def _display_base_gui(self):
        """
        Display the client base GUI
        """
        self._display_line(height=0, middle_txt=self.client.name, right_txt=self.client.version, windows=self.stdscr)
        self._display_all_messages()
        self._display_line(height=self.height - 1, left_txt="> ", fillingchar=" ", windows=self.stdscr)

    def update_prompt(self, prompt: str, cursor: int):
        self.prompt_cursor = cursor
        self._display_line(height=self.height - 1, left_txt="> " + prompt, fillingchar=" ", windows=self.stdscr)
        self._update_cursor()

    def display_message(self, message: Message | str):
        if type(message) is str:
            return self.display_message(Message(payload=message, message_type=MessageType.LOG))

        self.messages.append(message)
        if len(self.messages) > self.height - 2:
            self.messages.pop(0)
            self._display_all_messages()
        else:
            self._display_message(message, len(self.messages))

    def display_error(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.ERROR))

    def display_log(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.LOG))

    def display_debug(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.DEBUG))

    def display_success(self, text: str):
        return self.display_message(Message(payload=text, message_type=MessageType.SUCCESS))

    def _update_cursor(self, y=0, x=None):
        if x is None:
            x = self.prompt_cursor + 2
        self.stdscr.move(y, x)

    def exit(self):
        curses.nocbreak()
        curses.echo()
        self.stdscr.keypad(False)
        curses.endwin()
