from enum import StrEnum, auto


class Role(StrEnum):
    ADMIN = auto()
    SUPPORT = auto()
    CLIENT = auto()

    @classmethod
    def choices(cls):
        results = []

        for element in cls:
            _element = (element.value, element.name.lower().capitalize())
            results.append(_element)

        return results
