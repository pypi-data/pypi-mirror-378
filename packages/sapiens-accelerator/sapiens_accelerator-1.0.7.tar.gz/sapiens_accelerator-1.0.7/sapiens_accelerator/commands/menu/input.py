"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
from typing import List
from .keymap import KEYMAP, get_character
def mark(key: str):
    def decorator(func):
        handle = getattr(func, "handle_key", [])
        handle += [key]
        func.handle_key = handle
        return func
    return decorator
def mark_multiple(*keys: List[str]):
    def decorator(func):
        handle = getattr(func, "handle_key", [])
        handle += keys
        func.handle_key = handle
        return func
    return decorator
class KeyHandler(type):
    def __new__(cls, name, bases, attrs):
        new_cls = super().__new__(cls, name, bases, attrs)
        if not hasattr(new_cls, "key_handler"): new_cls.key_handler = {}
        new_cls.handle_input = KeyHandler.handle_input
        for value in attrs.values():
            handled_keys = getattr(value, "handle_key", [])
            for key in handled_keys: new_cls.key_handler[key] = value
        return new_cls
    @staticmethod
    def handle_input(cls):
        char = get_character()
        if char != KEYMAP["undefined"]: char = ord(char)
        handler = cls.key_handler.get(char)
        if handler:
            cls.current_selection = char
            return handler(cls)
        else: return None
def register(cls): return KeyHandler(cls.__name__, cls.__bases__, cls.__dict__.copy())
"""
    ########################################################################################################################################################
    # This algorithm is part of a code library to accelerate Sapiens Technology® Artificial Intelligence models, and its disclosure, distribution,         #
    # or reverse engineering without the company's prior consent will be subject to legal proceedings and actions pursued by our legal department.         #
    ########################################################################################################################################################
"""
