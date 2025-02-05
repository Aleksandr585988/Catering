
from django.db import models
from orders.models import Order


class DeliveryOrder(models.Model):
    provider = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    addresses = models.TextField()
    external_order_id = models.CharField(max_length=255)

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
