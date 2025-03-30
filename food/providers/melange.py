import enum
from dataclasses import asdict, dataclass
import httpx

class OrderStatus(enum.StrEnum):
    NOT_STARTED = "not_started"
    COOKING = "cooking"
    COOKED = "cooked"
    FINISHED = "finished"

@dataclass
class OrderItem:
    dish: str
    quantity: int

@dataclass
class OrderRequestBody:
    order: list[OrderItem]

@dataclass
class OrderResponse:
    id: str
    status: OrderStatus

class Provider:
    BASE_URL = "http://localhost:8001/api/orders"

    @classmethod
    def create_order(cls, order: OrderRequestBody):
        print("Creating order with payload:", asdict(order))

        try:
            response: httpx.Response = httpx.post(cls.BASE_URL, json=asdict(order))
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
            raise
        return OrderResponse(**response.json())

    @classmethod
    def get_order(cls, order_id: str):
        try:
            response: httpx.Response = httpx.get(f"{cls.BASE_URL}/{order_id}")
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            print(f"Response status code: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
            raise
        return OrderResponse(**response.json())
