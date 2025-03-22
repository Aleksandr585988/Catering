"""
STATUSES: not started, cooking, cooked, finished

BUENO HTTP POST /
```
    order: [
        {
            dish: string
            quantity: number
        }, ...
    ]
```
RESPONSE:
```
    {
        id: string,  // generated by restaurant
        status: string
    }
```


WEBHOOK HTTP POST <SELECT>
```
    {
        id: string,
        status: string
    }
```

=================================================================

STATUS: not started, cooking, cooked, finished

MELANGE HTTP POST /api/orders
```
    order: [
        {
            dish: string
            quantity: number
        }, ...
    ]
```
```
    {
        id: string,
        status: string
    }
```

MELANGE HTTP GET /api/orders/<ID>
```
    {
        status: string
    }
```
"""
from time import sleep
import httpx
from datetime import datetime, time, date
from .models import Order, RestaurantOrder
from .enums import Restaurant, OrderStatus
from celery.result import AsyncResult
from .constants import RESTAURANT_TO_INTERNAL_STATUSES

from .providers import melange, bueno

from config import celery_app
from dataclasses import asdict


class OrderInDB:
    def __init__(self, order: Order, internal_order_id: int) -> None:
        self.order = order 
        self.internal_order_id = internal_order_id
        self.orders = {
            restaurant_order.restaurant: restaurant_order
            for restaurant_order in order.restaurant_orders.all()
        }

    def append(self, restaurant: Restaurant, item):
        if restaurant.value not in self.orders:
            self.orders[restaurant.value] = RestaurantOrder.objects.create(
                order=self.order,
                restaurant=restaurant.value,
                status=OrderStatus.NOT_STARTED.value
            )
        self.orders[restaurant.value].save()


def validate_all_orders_cooked(order: OrderInDB) -> bool:
    flag = True

    for rest, _order in order.orders.items():
        if rest == Restaurant.MELANGE:
            if _order == Restaurant.MELANGE:
                if _order["status"] != melange.OrderStatus.COOKED:
                    flag = False
                    break

            if _order == Restaurant.BUENO:
                if _order["status"] != melange.OrderStatus.COOKED:
                    flag = False
                    break

        elif flag is True:
            Order.objects.filter(id=order.internal_order_id).update(
                status=OrderStatus.DRIVER_LOOKUP
            )

        return flag


# TODO uncomment


@celery_app.task
def melange_order_processing(order: OrderInDB):
    melange_order = order.orders.get(Restaurant.MELANGE.value)
    
    if not melange_order:
        raise ValueError("No order found for Melange")
    
    provider = melange.Provider()

    while (current_status := melange_order.status) != OrderStatus.DELIVERED:
        if current_status == OrderStatus.NOT_STARTED:
            if not melange_order.external_id:
                order_request_body = melange.OrderRequestBody(
                    order=[
                        melange.OrderItem(dish=item.dish.name, quantity=item.quantity)
                        for item in order.order.items.all()
                        if item.dish.restaurant.name.lower() == Restaurant.MELANGE.value.lower()
                    ]
                )

                response: melange.OrderResponse = provider.create_order(order_request_body)
                melange_order.external_id = response.id

            else:
                external_order_id = melange_order.external_id
                response = provider.get_order(order_id=external_order_id)

                if current_status != response.status:
                    melange_order.status = response.status
                    Order.objects.filter(id=order.internal_order_id).update(
                        status=RESTAURANT_TO_INTERNAL_STATUSES[Restaurant.MELANGE][
                            melange_order.status
                        ]
                    )
                print(f"Current status is {melange_order.status}. Waiting 1 second")
                sleep(1)

        elif current_status == melange.OrderStatus.COOKING:
            external_order_id = melange_order.external_id
            response = provider.get_order(order_id=external_order_id)

            if current_status != response.status:
                melange_order.status = response.status
                Order.objects.filter(id=order.internal_order_id).update(
                    status=RESTAURANT_TO_INTERNAL_STATUSES[Restaurant.MELANGE][
                        melange_order.status
                    ]
                )
            print(f"Current status is {current_status}. Waiting 3 seconds")
            sleep(3)

        elif current_status == melange.OrderStatus.COOKED:
            validate_all_orders_cooked(order)
            break

        else:
            raise ValueError(f"STATUS {current_status} is not supported!")

    melange_order.save()




@celery_app.task
def bueno_order_processing(order: OrderInDB):
    print("BUENO")
    print("*" * 30)


# TODO uncomment
@celery_app.task
def _schedule_order(order: Order):
    order_in_db = OrderInDB(order, internal_order_id=order.pk)

    for item in order.items.all():
        if (restaurant := Restaurant[item.dish.restaurant.name.upper()]) in [Restaurant.MELANGE, Restaurant.BUENO]:
            order_in_db.append(restaurant, item)
        else:
            raise ValueError(f"Cannot create order for {item.dish.restaurant.name} restaurant")

    melange_order_processing(order_in_db)
    bueno_order_processing(order_in_db)


def schedule_order(order: Order)  -> AsyncResult:
    assert type(order.eta) is date

    # todo remove
    # _schedule_order(order)
    # return None

    # 2025-03-06  -> 2025-03-06-00:00:00 UTC
    if order.eta == datetime.today():
        print(f"The order will be started processing now")
        return _schedule_order.apply_async(args=(order,))

    else:
        eta = datetime.combine(order.eta, time(hour=3))
        print(f"The order will be started processing {eta}")
        return _schedule_order.apply_async(args=(order,), eta=eta)