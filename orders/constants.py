from food.enums import OrderStatus

EXCLUDE_STATUSES = (
        OrderStatus.DELIVERED,
        OrderStatus.NOT_DELIVERED,
        OrderStatus.CANCELLED,
    )