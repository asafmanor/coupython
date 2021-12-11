import inspect
import sys


class Card:
    name = None

    def __str__(self):
        return f"{self.name}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return type(self) == type(other)

    def __ne__(self, other):
        return not self == other


class Ambassador(Card):
    name = "Ambassador"


class Assassin(Card):
    name = "Assassin"


class Captain(Card):
    name = "Captain"


class Contessa(Card):
    name = "Contessa"


class Duke(Card):
    name = "Duke"


CARDS = {
    name: obj for name, obj in inspect.getmembers(sys.modules[__name__], inspect.isclass)
    if obj.__module__ is __name__ and name != 'Card'
}