from django.db import models


PROVIDERS_CHOICES = (
    ("uklon", "Uklon"),
    ("uber", "Uber"),
)

DELIVERY_STATUSES_CHOICES = (
    ("not started", "Not started"),
    ("ongoing", "Ongoing (in delivery)"),
    ("cancelled user", "Cancelled by User (customer)"),
    ("cancelled system", "Cancelled by System"),
    ("cancelled driver", "Cancelled by Driver (or provider)"),
    ("done", "Successfully finished"),
    ("failed", "Successfully finished"),
    ("stolen", "Stolen by driver"),
)


class DeliveryDishesOrder(models.Model):

    class Meta:
        db_table = "dishes_orders_deliveries"

    provider = models.CharField(max_length=100, choices=PROVIDERS_CHOICES)
    status = models.CharField(max_length=50, choices=DELIVERY_STATUSES_CHOICES)
    addresses = models.TextField()
    external_order_id = models.CharField(max_length=255)

    order = models.ForeignKey("food.DishesOrder", on_delete=models.CASCADE)
