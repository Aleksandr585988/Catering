from typing import Literal

from django.conf import settings
from django.db import models

from .constants import RESTAURANT_TO_INTERNAL_STATUSES
from .enums import OrderStatus
from .enums import Restaurant as RestaurantEnum


def normalize_status(status: str) -> str:
    return status.strip().replace(" ", "_").lower()


class Restaurant(models.Model):
    class Meta:
        db_table = "restaurants"

    name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"[{self.pk}] {self.name}"


class Dish(models.Model):
    class Meta:
        db_table = "dishes"
        verbose_name_plural = "dishes"

    name = models.CharField(max_length=50, null=True)
    price = models.IntegerField()
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} {self.price}  ({self.restaurant})"


class Order(models.Model):
    """the instance of that class defines the order of dishes from
    external restaurant that is available in the system.

    dishes in plural.
    """

    class Meta:
        db_table = "orders"

    status = models.CharField(max_length=20)
    provider = models.CharField(max_length=20, null=True, blank=True)
    eta = models.DateField()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"{self.pk} {self.status} for {self.user.email}"

    def __repr__(self) -> str:
        return super().__str__()

    @classmethod
    def update_from_provider_status(cls, id_: int, status: str, delivery=False) -> None:
        normalized_status = normalize_status(status)

        if delivery is False:
            if normalized_status == "finished":
                cls.objects.filter(id=id_).update(status=OrderStatus.DRIVER_LOOKUP)
            else:
                try:
                    cls.objects.filter(id=id_).update(
                        status=RESTAURANT_TO_INTERNAL_STATUSES[RestaurantEnum.MELANGE][
                            normalized_status
                        ]
                    )
                except KeyError:
                    raise ValueError(f"Unknown status received: {status}")

        else:
            if normalized_status == "delivered":
                cls.objects.filter(id=id_).update(status=OrderStatus.DELIVERED)
            elif normalized_status == "delivery":
                cls.objects.filter(id=id_).update(status=OrderStatus.DELIVERY)
            else:
                raise ValueError(f"Status {status} is not supported")


class RestaurantOrder(models.Model):
    class Meta:
        db_table = "restaurant_order"

    external_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    restaurant = models.CharField(max_length=20)
    status = models.CharField(max_length=20)
    order = models.ForeignKey(
        "Order", on_delete=models.CASCADE, related_name="restaurant_orders"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"[{self.restaurant}] Order {self.external_id or 'pending'} - {self.status}"
        )


class DishOrderItem(models.Model):
    """the instance of that class defines a DISH item that is related
    to an ORDER, that user has made.


    NOTES
    --------

    do we need user in relations?
    NOT! because we have it in the ``Order``
    """

    class Meta:
        db_table = "dish_order_items"

    quantity = models.SmallIntegerField()

    dish = models.ForeignKey("Dish", on_delete=models.CASCADE)
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="items")

    def __str__(self) -> str:
        return f"[{self.order.pk}] {self.dish.name}: {self.quantity}"
