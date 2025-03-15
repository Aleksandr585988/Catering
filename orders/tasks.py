from datetime import date
from django.db.models import QuerySet
from config import celery_app
from food.enums import OrderStatus
from food.models import Order

from .constants import EXCLUDE_STATUSES

@celery_app.task
def order_validation():
    orders: QuerySet[Order] = Order.objects.exclude(
        status__in=EXCLUDE_STATUSES,
        )

    for order in orders:
        if order.eta < date.today():
            order.status = OrderStatus.CANCELLED
            order.save()
            print("Concelleed order {order}")
