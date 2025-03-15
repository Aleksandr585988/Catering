
from datetime import date
from threading import Thread
from time import sleep

from django.db.models import QuerySet
from shared.cache import CacheService
import json

from food.enums import OrderStatus
from food.models import Order
from .constants import EXCLUDE_STATUSES



class Processor:

    cache_service = CacheService()



    def __init__(self) -> None:
        self._thread = Thread(target=self.process, daemon=True)
        print(f"Orders Processor is created")

    @property
    def today(self):
        return date.today()

    def start(self):
        self._thread.start()
        print(f"Orders Processor started processing orders")

    def process(self):
        """The processing of the orders entrypoint."""

        while True:
            self._process()
            sleep(2)  # delay 

    def _process(self):
        
        orders: QuerySet[Order] = Order.objects.exclude(
            status__in=EXCLUDE_STATUSES
        )

        for order in orders:
            match order.status:
                case OrderStatus.NOT_STARTED:
                    self._process_not_started(order)
                    self._update_order_cache(order, self._generate_order_cache(order))
                case OrderStatus.COOKING_REJECTED:
                    self._process_cooking_rejected()
                case _:
                    print(f"Unrecognized order status: {order.status}. passing")

    def _process_not_started(self, order: Order):
        """
        INPUT DATA
        -------------
        TODAY: 03.03.2025
        ETA:   04.03.2025

        CONDITIONS
        --------------
        ETA1:   02.03.2025  -> CANCELLED (because deprecated/outdated)
        ETA2:   03.03.2025  -> do nothing
        ETA3:   04.03.2025  -> COOKING + send API call to restaurants
        """

        if order.eta == self.today:
            order.status = OrderStatus.COOKING
            order.save()

            restaurants = set()
            for item in order.items.all():
                restaurants.add(item.dish.restaurant)

            print(f"Finished preparing order. Restaurants: {restaurants}")
            print(f"Order: {order}")

    def _process_cooking_rejected(self):
        raise NotImplementedError
    
    def _generate_order_cache(self, order: Order) -> dict:
        return {
            "id": order.pk,
            "status": order.status,
            "eta": order.eta,
            "food": [
                {"dish_id": item.dish.pk, "quantity": item.quantity}
                for item in order.items.all()
            ],
        }
    
    def _update_order_cache(self, order: Order, order_cache: dict):
        # We update the cache with the new status of the order
        if order.status == OrderStatus.COOKING:
            self.cache_service.set(f"order:{order.pk}", json.dumps(order_cache), ttl=3600)
            print(f"Order {order.pk} updated in Redis cache")