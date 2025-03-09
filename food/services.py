from datetime import datetime, date, time
from .models import Order
from config import celery_app


@celery_app.task
def schedule_order_task(order: Order):
    print(f"Order started processing...{order}")


class OrdersService:
    def schedule_order(self, order: Order):
        """Add the task to the queue for the future processing."""

        assert type(order.eta) is date

        # 2025-03-06  -> 2025-03-06-00:00:00 UTC
        if order.eta == date.today():
            print(f"The order will be started processing now")
            return schedule_order_task.delay(order)
        else:
            eta = datetime.combine(order.eta, time(hour=3))
            print(f"The order will be started processing {eta}")
            return schedule_order_task.delay(order, eta=eta)