import asyncio
import random
import uuid

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel, Field

STORAGE: dict[str, dict] = {}
ORDER_STATUSES = ("not started", "delivery", "delivered")


app = FastAPI()


class OrderRequestBody(BaseModel):
    addresses: list[str] = Field(min_length=1)
    comments: list[str] = Field(min_length=1)
    

async def delivery(order_id: str):
    for address in STORAGE[order_id]["addresses"]:
        await asyncio.sleep(1)
        print(f"🏁 DELIVERED TO {address}")


# business model of the application
async def update_order_status(order_id: str):
    for status in ORDER_STATUSES[1:]:
        await asyncio.sleep(random.randint(1, 2))

        # Случайно меняем координаты, как будто курьер движется
        STORAGE[order_id]["location"] = {
            "lat": round(random.uniform(50.40, 50.45), 6),
            "lon": round(random.uniform(30.50, 30.55), 6)
        }

        if status == "delivery":
          await delivery(order_id)

        STORAGE[order_id]["status"] = status
        print(f"UKLON [{order_id}] --> {status}")


@app.post("/drivers/orders")
async def make_order(order: OrderRequestBody, background_tasks: BackgroundTasks):
    print(order)
    order_id = str(uuid.uuid4())
    STORAGE[order_id] = {
        "id": order_id,
        "status": "not started",
        "addresses": order.addresses,
        "comments": order.comments,
        "location": {
            "lat": 50.4501,  # стартовые координаты
            "lon": 30.5234
        }
    }
    background_tasks.add_task(update_order_status, order_id)

    # return {"id": order_id, "status": "not started"}

    return STORAGE.get(order_id, {"error": "No such order"})


@app.get("/drivers/orders/{order_id}")
async def retrieve_order(order_id: str):
    return STORAGE.get(order_id, {"error": "No such order"})