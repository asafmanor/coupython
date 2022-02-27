from enum import Enum


class FormattedEnum(Enum):
    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
