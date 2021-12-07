class Card:
    name = None

    def __init__(self, idx: int):
        self.idx = idx

    def __str__(self):
        return f"{self.name}-{self.idx}"

    def __repr__(self):
        return f"{self.name}-{self.idx}"


class CardList(list):
    # TODO implement with O(1) access by overloading some list methods
    # For example, every time an item is added to the list, it's name can be added
    def has(self, name: str):
        for x in self:
            if x.name == name:
                return True
        return False

    def get(self, name: str):
        for idx, x in enumerate(self):
            if x.name == name:
                return self.pop(idx)
        raise RuntimeError(f"CardList does not contain {name}")


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
