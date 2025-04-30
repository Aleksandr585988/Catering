from enum import StrEnum, auto

class Restaurant(StrEnum):
    BUENO = auto()
    MELANGE = auto()


class OrderStatus(StrEnum):
    NOT_STARTED = auto()
    COOKING_REJECTED = auto()
    COOKING = auto()
    COOKED = auto()
    FINISHED = auto()
    DRIVER_LOOKUP = auto()
    DELIVERY = auto()
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
