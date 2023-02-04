import time
from typing import Any
import uvicorn
from fastapi import FastAPI
from RestAPI.RemonlineAPI import *
from fastapi.middleware.cors import CORSMiddleware
from config import *
from pydantic import BaseModel, PositiveInt
from DB import DBConnection
import threading

CRM = RemonlineAPI(REMONLINE_API_KEY_PROD)
warehouse = CRM.get_main_warehouse_id()

app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

good = None


@app.get("/api/v1/allgoods")
def get_all_goods():
    run = True
    goods = []
    page = 1
    while run:
        response = CRM.get_goods(warehouse, page=page)
        page += 1
        if len(response["data"]) < 50:
            run = False

        if len(response["data"]):
            goods += response["data"]
    global good
    good = {"data": goods}
    print(good)
    time.sleep(20)
    get_all_goods()


t = threading.Thread(target=get_all_goods).start()


@app.get("/api/v1/goods")
def get_goods():
    return good


@app.get("/api/v1/shoppingcart/{id}")
def get_shopping_cart(id: int):
    # with open("data/shopping_cart.json") as file:
    #     return [obj for obj in json.load(file) if obj['telegram_id'] == id]
    db = DBConnection("info.db")
    data = db.list_shopping_cart(id)
    db.connection.close()
    return data


@app.delete("/api/v1/shoppingcart/{id}")
def delete_shopping_cart(id: PositiveInt):
    # with open("data/shopping_cart.json", 'r+') as file:
    #     new_data = [obj for obj in json.load(file) if obj["id"] != id]
    #     json.dump(new_data, file, indent=4)
    db = DBConnection("info.db")
    db.delete_shopping_cart(id)
    db.connection.close()


class CartModel(BaseModel):
    telegram_id: int
    good_id: int


@app.post("/api/v1/shoppingcart/")
def post_shopping_cart(Cart: CartModel):
    new_cart = {
        "telegram_id": int(Cart.telegram_id),
        "good_id": int(Cart.good_id),
        "count": 1
    }
    db = DBConnection("info.db")
    db.post_shopping_cart(new_cart["telegram_id"], new_cart["good_id"])
    db.connection.close()


class UpdateCountModel(BaseModel):
    count: int


@app.patch("/api/v1/shoppingcart/{id}")
def update_shopping_cart_count(id: int, CountModel: UpdateCountModel):
    db = DBConnection("info.db")
    db.update_shopping_cart_count(id, CountModel.count)
    db.connection.close()


class OrderModel(BaseModel):
    telegram_id: int
    goods_list: Any
    name: str
    last_name: str
    prepayment: bool
    phone: str
    nova_post_address: str
    is_paid: bool = False
    description: str = None
    ttn: str = None


@app.post("/api/v1/order")
def post_order(order: OrderModel):
    db = DBConnection("info.db")
    db.post_orders(order.telegram_id,
                   str(order.goods_list),
                   order.name,
                   order.last_name,
                   order.prepayment,
                   order.phone,
                   order.nova_post_address,
                   order.is_paid,
                   order.description,
                   order.ttn)
    db.connection.close()


@app.get("/api/v1/getorder/{telegram_id}")
def get_order_by_id(telegram_id: int):
    db = DBConnection("info.db")
    orders = db.get_all_orders(telegram_id)
    db.connection.close()
    return orders


@app.get("/api/v1/orders")
def get_orders():
    db = DBConnection("info.db")
    orders = db.get_all_orders()
    db.connection.close()
    return orders


# @app.post("/api/v1/shoppingcart/")
# def post_shopping_cart(Cart: CartModel):
#
#     new_cart = {
#         "telegram_id": int(Cart.telegram_id),
#         "good_id": int(Cart.good_id),
#         "count": 1
#     }
#
#     with open("data/shopping_cart.json", "r+") as file:
#         file_data = json.load(file)
#         new_cart['id'] = int(file_data[-1]["id"])+1
#         file_data.append(new_cart)
#         file.seek(0)
#         json.dump(file_data, file, indent=4)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
