class Card:
    name = None


class CardList(list):
    def has(self, name):
        for x in self:
            if x.name == name:
                return True
        return False


class Duke(Card):
    name = "Duke"

    def __init__(self, idx: int):
        self.idx = idx


class Assassin(Card):
    name = "Assassin"

    def __init__(self, idx: int):
        self.idx = idx


class Ambassador(Card):
    name = "Ambassador"

    def __init__(self, idx: int):
        self.idx = idx


class Captain(Card):
    name = "Captain"

    def __init__(self, idx: int):
        self.idx = idx


class Contessa(Card):
    name = "Contessa"

    def __init__(self, idx: int):
        self.idx = idx
