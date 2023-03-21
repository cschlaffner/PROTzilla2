from random import choices
from string import ascii_letters


def random_string():
    return "".join(choices(ascii_letters, k=16))
