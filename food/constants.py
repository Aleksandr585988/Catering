"""
{
    "melange": {
        "not started": "not_started",
        "cooking": "cooking",
        "cooked": "cooked",
        "finished": "DRIVER_LOOKUP",
    },
    "bueno": {
        "not started": "not_started",
        "cooking": "cooking",
        "cooked": "cooked",
        "finished": "DRIVER_LOOKUP",
    },
}
"""

from .enums import OrderStatus, Restaurant
from .providers import bueno, melange

EXCLUDE_STATUSES = (
    OrderStatus.DELIVERED,
    OrderStatus.NOT_DELIVERED,
    OrderStatus.CANCELLED,
)


RESTAURANT_TO_INTERNAL_STATUSES: dict[Restaurant, dict[str, OrderStatus]] = {
    Restaurant.MELANGE: {
        melange.OrderStatus.NOT_STARTED: OrderStatus.NOT_STARTED,
        melange.OrderStatus.COOKING: OrderStatus.COOKING,
        melange.OrderStatus.COOKED: OrderStatus.COOKED,
    },
    Restaurant.BUENO: {
        bueno.OrderStatus.NOT_STARTED: OrderStatus.NOT_STARTED,
        bueno.OrderStatus.COOKING: OrderStatus.COOKING,
        bueno.OrderStatus.COOKED: OrderStatus.COOKED,
    },
}
