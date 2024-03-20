import curses

from client.display_client import DisplayClient


class Input:
    client: DisplayClient
    listening: bool
    prompt: str
    prompt_cursor: int

    def __init__(self, client):
        self.valid_char = list('/. ')
        self.client = client
        self._reset_prompt()

    def _reset_prompt(self):
        self.prompt = ""
        self.prompt_cursor = 0
        self.prompt_updated()

    def start_listening(self):
        self.listening = True
        self.prompt = ""
        while self.listening:
            char: int = self.client.display.input_windows.getch()

            if char == -1:
                pass
            else:
                if char == 0xa:  # Enter key
                    try:
                        self.client.command(self.prompt)
                    except Exception as e:
                        self.client.display.display_log(str(e))
                    finally:
                        self._reset_prompt()

                elif char == curses.KEY_LEFT:
                    self.prompt_cursor -= 1
                    if self.prompt_cursor < 0:
                        self.prompt_cursor = 0

                elif char == curses.KEY_RIGHT:
                    self.prompt_cursor += 1
                    if self.prompt_cursor > len(self.prompt):
                        self.prompt_cursor = len(self.prompt)

                elif char == curses.KEY_UP:
                    self.client.display.scroll(-1)

                elif char == curses.KEY_DOWN:
                    self.client.display.scroll(1)

                elif char == curses.KEY_SR:
                    self.client.display.scroll(-1)

                elif char == curses.KEY_SF:
                    self.client.display.scroll(1)

                elif char == 8:  # Del key
                    self.prompt = self.prompt[:self.prompt_cursor-1] + self.prompt[self.prompt_cursor:]
                    self.prompt_cursor -= 1

                elif char == curses.KEY_DC:
                    self.prompt = self.prompt[:self.prompt_cursor] + self.prompt[self.prompt_cursor+1:]

                elif chr(char).isalnum() or chr(char) in self.valid_char:
                    self.prompt = self.prompt[:self.prompt_cursor] + chr(char) + self.prompt[self.prompt_cursor:]
                    self.prompt_cursor += 1

            self.prompt_updated()

    def prompt_updated(self):
        self.client.display.update_prompt(self.prompt, self.prompt_cursor)
