
from django.db import models


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)


class Dish(models.Model):
    name = models.CharField(max_length=50)

    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)