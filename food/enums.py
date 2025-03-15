from enum import StrEnum, auto


class OrderStatus(StrEnum):
    NOT_STARTED = auto()
    COOKING_REJECTED = auto()
    COOKING = auto()
    COOKED = auto()
    DRIVER_LOOKUP = auto()
    DRIVER_WAITING = auto()
    DELIVERED = auto()
    NOT_DELIVERED = auto()
    CANCELLED = auto()

    @classmethod
    def choices(cls):
        results = []

        for element in cls:
            _element = (element.value, element.name.lower().capitalize())
            results.append(_element)

        return results
