class Duke:
    name = "Duke"

    def __init__(self, idx: int):
        self.idx = idx


class Assassin:
    name = "Assassin"

    def __init__(self, idx: int):
        self.idx = idx


class Ambassador:
    name = "Ambassador"

    def __init__(self, idx: int):
        self.idx = idx


class Captain:
    name = "Captain"

    def __init__(self, idx: int):
        self.idx = idx


class Contessa:
    name = "Contessa"

    def __init__(self, idx: int):
        self.idx = idx


class CardList(list):
    def has(self, name):
        for x in self:
            if x.name == name:
                return True
        return False
