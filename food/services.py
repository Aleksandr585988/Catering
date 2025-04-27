from dataclasses import asdict
from datetime import date, datetime, time
from time import sleep
from typing import Iterable

from celery.result import AsyncResult
from django.core.exceptions import ObjectDoesNotExist

from config import celery_app


from .constants import RESTAURANT_TO_INTERNAL_STATUSES
from .enums import OrderStatus, Restaurant
from .models import Order
from .models import Restaurant as RestaurantModels
from .models import RestaurantOrder
from .providers import bueno, melange, uklon


def normalize_status(status: str) -> str:
    return status.strip().replace(" ", "_").upper()


class OrderInCache:
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
                status=OrderStatus.NOT_STARTED.value,
            )
        self.orders[restaurant.value].save()


def validate_external_orders_ready(order: OrderInCache) -> bool:
    flag = True

    for rest, _order in order.orders.items():
        if rest == Restaurant.MELANGE:
            if _order == Restaurant.MELANGE:
                if _order["status"] not in (
                    melange.OrderStatus.COOKED,
                    melange.OrderStatus.FINISHED,
                ):
                    flag = False
                    break

            elif _order == Restaurant.BUENO:
                if _order["status"] != melange.OrderStatus.COOKED:
                    flag = False
                    break

    # if flag is True:
    #     Order.objects.filter(id=order.internal_order_id).update(
    #         status=OrderStatus.DRIVER_LOOKUP
    #     )

    return flag


# TODO uncomment
@celery_app.task
def melange_order_processing(internal_order_id: int):
    order = Order.objects.get(id=internal_order_id)
    order_in_db = OrderInCache(order, internal_order_id)

    melange_order = order_in_db.orders.get(Restaurant.MELANGE.value)

    if not melange_order:
        raise ValueError("No order found for Melange")

    provider = melange.Provider()

    while True:
        current_status_raw = melange_order.status
        normalized_status = normalize_status(current_status_raw)

        try:
            current_status = OrderStatus[normalized_status]
        except KeyError:
            # Если статус не найден, выводим предупреждение и пропускаем
            print(
                f"WARNING: Status '{normalized_status}' is not a valid OrderStatus. Skipping..."
            )
            continue  # или можно завершить цикл, в зависимости от требований

        if current_status == OrderStatus.DELIVERED:
            break

        if current_status == OrderStatus.NOT_STARTED:
            if not melange_order.external_id:
                order_request_body = melange.OrderRequestBody(
                    order=[
                        melange.OrderItem(dish=item.dish.name, quantity=item.quantity)
                        for item in order.items.all()
                        if item.dish.restaurant.name.lower()
                        == Restaurant.MELANGE.value.lower()
                    ]
                )

                response: melange.OrderResponse = provider.create_order(
                    order_request_body
                )
                melange_order.external_id = response.id
                melange_order.status = normalize_status(response.status)
                Order.update_from_provider_status(
                    id_=internal_order_id, status=response.status
                )

            else:
                external_order_id = melange_order.external_id
                response = provider.get_order(order_id=external_order_id)

                if current_status_raw != response.status:
                    melange_order.status = normalize_status(response.status)
                    Order.update_from_provider_status(
                        id_=internal_order_id, status=response.status
                    )

            print(f"Current status is {melange_order.status}. Waiting 1 second")
            sleep(1)

        elif current_status == OrderStatus.COOKING:
            external_order_id = melange_order.external_id
            response = provider.get_order(order_id=external_order_id)

            if current_status_raw != response.status:
                melange_order.status = normalize_status(response.status)
                Order.update_from_provider_status(
                    id_=internal_order_id, status=response.status
                )

            print(f"Current status is {current_status}. Waiting 3 seconds")
            sleep(3)

        elif current_status == OrderStatus.COOKED:
            print(f"Current status is {current_status}")
            validate_external_orders_ready(order_in_db)
            break

        else:
            # Если статус вообще не поддерживается
            print(f"ERROR: STATUS {current_status} is not supported!")
            break

    melange_order.save()


@celery_app.task
def bueno_order_processing(internal_order_id: int):
    provider = bueno.Provider()

    if not isinstance(internal_order_id, int):
        raise TypeError(
            f"Expected internal_order_id to be int, got {type(internal_order_id)}"
        )

    order = Order.objects.get(id=internal_order_id)

    order_in_db = OrderInCache(order, internal_order_id=internal_order_id)

    bueno_order = order_in_db.orders.get(Restaurant.BUENO.value)
    if not bueno_order:
        raise ValueError("No order found for Bueno")

    response: bueno.OrderResponse = provider.create_order(
        bueno.OrderRequestBody(
            order=[
                bueno.OrderItem(dish=item.dish.name, quantity=item.quantity)
                for item in order.items.all()
                if item.dish.restaurant.name.lower() == Restaurant.BUENO.value.lower()
            ]
        )
    )

    bueno_order.external_id = response.id
    bueno_order.save()

    print("BUENO ORDER PROCESSED")


# import logging
# import traceback

# logger = logging.getLogger(__name__)

# @celery_app.task
# def bueno_order_processing(internal_order_id: int):
#     provider = bueno.Provider()

#     if not isinstance(internal_order_id, int):
#         raise TypeError(f"Expected internal_order_id to be int, got {type(internal_order_id)}")

#     order = Order.objects.get(id=internal_order_id)

#     order_in_db = OrderInCache(order, internal_order_id=internal_order_id)

#     bueno_order = order_in_db.orders.get(Restaurant.BUENO.value)
#     if not bueno_order:
#         raise ValueError("No order found for Bueno")

#     response: bueno.OrderResponse = provider.create_order(
#         bueno.OrderRequestBody(
#             order=[
#                 bueno.OrderItem(dish=item.dish.name, quantity=item.quantity)
#                 for item in order.items.all()
#                 if item.dish.restaurant.name.lower() == Restaurant.BUENO.value.lower()
#             ]
#         )
#     )


#     bueno_order.external_id = response.id
#     bueno_order.save()

#     print("BUENO ORDER PROCESSED")


@celery_app.task
def delivery_order(order: OrderInCache, restaurants: Iterable[RestaurantModels]):
    print("DELIVERY PROCESSING STARTED")

    while True:
        if validate_external_orders_ready(order):
            _delivery_order_task(order, restaurants)
        break

    print("DELIVERED all the orders...")


def _delivery_order_task(order: OrderInCache, restaurants: Iterable[RestaurantModels]):
    provider = uklon.Provider()

    print(f"🚚 DELIVERY PROCESSING STARTED")

    addresses: list[str] = []
    comments: list[str] = []

    for rest in restaurants:
        addresses.append(rest.address)
        external_id: str = order.orders[rest.name.lower()].external_id
        comments.append(f"ORDER: {external_id}")

    order_payload = uklon.OrderRequestBody(addresses=addresses, comments=comments)
    _response: uklon.OrderResponse = provider.create_order(order_payload)

    current_status: uklon.OrderStatus = uklon.OrderStatus.NOT_STARTED

    while current_status != uklon.OrderStatus.DELIVERED:
        try:
            response: uklon.OrderResponse = provider.get_order(_response.id)

            # Проверка изменений статуса
            if current_status == response.status:
                sleep(1)
                continue

            current_status = response.status

            # Обновление статуса в базе
            Order.update_from_provider_status(
                id_=order.internal_order_id, status=current_status, delivery=True
            )

            # Логирование текущего статуса
            print(f"Current status: {current_status}")

            # Проверка на успешное завершение
            if current_status == uklon.OrderStatus.DELIVERED:
                print("Order delivered successfully.")
                break

        except Exception as e:
            print(f"Error while processing delivery: {str(e)}")
            sleep(5)


# TODO uncomment
@celery_app.task
def _schedule_order(order: Order):
    if not order.pk:
        print("Order has not been saved. Saving now...")
        order.save()

    order_in_db = OrderInCache(order, internal_order_id=order.pk)
    delivery_restaurants: set[RestaurantModels] = set()

    for item in order.items.all():
        if (restaurant := Restaurant[item.dish.restaurant.name.upper()]) in [
            Restaurant.MELANGE,
            Restaurant.BUENO,
        ]:
            delivery_restaurants.add(item.dish.restaurant)
            order_in_db.append(restaurant, item)
        else:
            raise ValueError(
                f"Cannot create order for {item.dish.restaurant.name} restaurant"
            )

    melange_order_processing.delay(order_in_db.internal_order_id)
    bueno_order_processing.delay(order_in_db.internal_order_id)
    delivery_order.delay(order_in_db, delivery_restaurants)


def schedule_order(order: Order) -> AsyncResult:
    assert type(order.eta) is date

    print(f"Scheduling order with eta {order.eta}")

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
