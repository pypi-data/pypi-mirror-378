"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
import builtins
import sys
from ...utils.imports import _is_package_available
from . import cursor, input
from .helpers import Direction, clear_line, forceWrite, linebreak, move_cursor, reset_cursor, writeColor
from .keymap import KEYMAP
in_colab = False
try: in_colab = _is_package_available("google.colab")
except ModuleNotFoundError: pass
@input.register
class BulletMenu:
    def __init__(self, prompt: str = None, choices: list = []):
        self.position = 0
        self.choices = choices
        self.prompt = prompt
        if sys.platform == "win32": self.arrow_char = "*"
        else: self.arrow_char = "➔ "
    def write_choice(self, index, end: str = ""):
        if sys.platform != "win32": writeColor(self.choices[index], 32, end)
        else: forceWrite(self.choices[index], end)
    def print_choice(self, index: int):
        "Prints the choice at the given index"
        if index == self.position:
            forceWrite(f" {self.arrow_char} ")
            self.write_choice(index)
        else: forceWrite(f"    {self.choices[index]}")
        reset_cursor()
    def move_direction(self, direction: Direction, num_spaces: int = 1):
        old_position = self.position
        if direction == Direction.DOWN:
            if self.position + 1 >= len(self.choices): return
            self.position += num_spaces
        else:
            if self.position - 1 < 0: return
            self.position -= num_spaces
        clear_line()
        self.print_choice(old_position)
        move_cursor(num_spaces, direction.name)
        self.print_choice(self.position)
    @input.mark(KEYMAP["up"])
    def move_up(self): self.move_direction(Direction.UP)
    @input.mark(KEYMAP["down"])
    def move_down(self): self.move_direction(Direction.DOWN)
    @input.mark(KEYMAP["newline"])
    def select(self):
        move_cursor(len(self.choices) - self.position, "DOWN")
        return self.position
    @input.mark(KEYMAP["interrupt"])
    def interrupt(self):
        move_cursor(len(self.choices) - self.position, "DOWN")
        raise KeyboardInterrupt
    @input.mark_multiple(*[KEYMAP[str(number)] for number in range(10)])
    def select_row(self):
        index = int(chr(self.current_selection))
        movement = index - self.position
        if index == self.position: return
        if index < len(self.choices):
            if self.position > index: self.move_direction(Direction.UP, -movement)
            elif self.position < index: self.move_direction(Direction.DOWN, movement)
            else: return
        else: return
    def run(self, default_choice: int = 0):
        if self.prompt:
            linebreak()
            forceWrite(self.prompt, "\n")
            if in_colab: forceWrite("Please input a choice index (starting from 0), and press enter", "\n")
            else: forceWrite("Please select a choice using the arrow or number keys, and selecting with enter", "\n")
        self.position = default_choice
        for i in range(len(self.choices)):
            self.print_choice(i)
            forceWrite("\n")
        move_cursor(len(self.choices) - self.position, "UP")
        with cursor.hide():
            while True:
                if in_colab:
                    try: choice = int(builtins.input())
                    except ValueError: choice = default_choice
                else: choice = self.handle_input()
                if choice is not None:
                    reset_cursor()
                    for _ in range(len(self.choices) + 1):
                        move_cursor(1, "UP")
                        clear_line()
                    self.write_choice(choice, "\n")
                    return choice
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
