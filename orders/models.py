
from django.db import models
from users.models import User
from restaurants.models import Dish


class Order(models.Model):
    external_order_id = models.CharField(max_length=255)

    user = models.ForeignKey(User, on_delete=models.CASCADE)


class DishOrder(models.Model):
    quantity = models.SmallIntegerField()

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)