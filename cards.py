class Card:
    name = None

    def __init__(self, idx: int):
        self.idx = idx


class CardList(list):
    def has(self, name):
        for x in self:
            if x.name == name:
                return True
        return False


class Duke(Card):
    name = "Duke"


class Assassin(Card):
    name = "Assassin"


class Ambassador(Card):
    name = "Ambassador"


class Captain(Card):
    name = "Captain"


class Contessa(Card):
    name = "Contessa"
