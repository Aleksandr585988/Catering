from django.db import models
from django.conf import settings


class Restaurant(models.Model):
    class Meta:
        db_table = "restaurants"

    name = models.CharField(max_length=100, blank=False)
    address = models.CharField(max_length=100, blank=True)

    def __str__(self) -> str:
        return f"{self.name}, {self.address}"


class Dish(models.Model):
    class Meta:
        db_table = "dishes"
        verbose_name_plural = "dishes"

    name = models.CharField(max_length=50, null=True)
    price = models.IntegerField()
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name} {self.price}  ({self.restaurant})"


class DishesOrder(models.Model):
    """the instance of that class defines the order of dishes from
    external restaurant that is available in the system.

    dishes in plural.
    """

    class Meta:
        db_table = "dishes_orders"
        verbose_name_plural = "dishes orders"

    external_order_id = models.CharField(max_length=255)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return f"Order {self.external_order_id} for {self.user.username}"


class DishOrderItem(models.Model):
    """the instance of that class defines a DISH item that is related
    to an ORDER, that user has made.
    """

    class Meta:
        db_table = "dish_order_items"

    quantity = models.SmallIntegerField()

    order = models.ForeignKey("DishesOrder", on_delete=models.CASCADE)
    dish = models.ForeignKey("Dish", on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"[{self.order.external_order_id}] {self.dish.name}: {self.quantity}"
