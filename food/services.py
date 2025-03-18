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
import time
import httpx
from datetime import datetime, date
from .models import Order, RestaurantOrder
from .enums import Restaurant, OrderStatus
from celery.result import AsyncResult


class OrderInDB:
    def __init__(self, order: Order) -> None:
        self.order = order
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

# TODO uncomment
# @celery_app.task
def melange_order_processing(order: OrderInDB):
    melange_order = order.orders.get(Restaurant.MELANGE.value)
    if not melange_order:
        raise ValueError("No order found for Melange")

    while (current_status := melange_order.status) != OrderStatus.DELIVERED.value:
        if current_status == OrderStatus.NOT_STARTED.value:
            if not melange_order.external_id:
                payload = {"order": [
                    {"dish": item.dish.name, "quantity": item.quantity}
                    for item in order.order.items.all() if item.dish.restaurant.name == Restaurant.MELANGE.value
                ]}
                response = httpx.post("http://localhost:8001/api/orders", json=payload)
                response.raise_for_status()
                melange_order.external_id = response.json()["id"]
                melange_order.save()
            else:
                response = httpx.get(f"http://localhost:8001/api/orders/{melange_order.external_id}")
                response.raise_for_status()
                melange_order.status = response.json()["status"]
                melange_order.save()
                print(f"Current status is {melange_order.status}. Waiting 1 second")
                time.sleep(1)

        elif current_status == OrderStatus.COOKING.value:
            response = httpx.get(f"http://localhost:8001/api/orders/{melange_order.external_id}")
            response.raise_for_status()
            melange_order.status = response.json()["status"]
            melange_order.save()
            print(f"Current status is {melange_order.status}. Waiting 3 seconds")
            time.sleep(3)

        elif current_status == OrderStatus.COOKED.value:
            print("CALLING DELIVERY SERVICE TO PASS THE FOOD ORDER")
            break

        else:
            raise ValueError(f"STATUS {current_status} is not supported!")

    melange_order.save()

        

def bueno_order_processing(order: OrderInDB):
    restaurant_order = order.orders.get(Restaurant.BUENO.value)
    print(f"Processing Bueno order: {restaurant_order}")

# TODO uncomment
# @celery_app.task
def _schedule_order(order: Order):
    order_in_db = OrderInDB(order)

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
    _schedule_order(order)
    return None

    # 2025-03-06  -> 2025-03-06-00:00:00 UTC
    if order.eta == datetime.today():
        print(f"The order will be started processing now")
        return schedule_order_task.apply_async(args=(order,))

    else:
        eta = datetime.combine(order.eta, time(hour=3))
        print(f"The order will be started processing {eta}")
        return schedule_order_task.apply_async(args=(order,), eta=eta)