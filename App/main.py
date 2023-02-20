import time
import uvicorn
from aiogram.types.base import Integer
from pydantic import PositiveInt
from fastapi import FastAPI

from App.UpdateOrdersTask import update_order_task
from RestAPI.RemonlineAPI import *
from fastapi.middleware.cors import CORSMiddleware
from config import *
from DB import DBConnection
import threading
from engine import manager_notes_builder, find_good, find_discount, get_month_money_spent
from Models import *

CRM = RemonlineAPI(REMONLINE_API_KEY_PROD)
warehouse = CRM.get_main_warehouse_id()
#
TEST_CRM = RemonlineAPI(REMONLINE_API_KEY_TEST)
branch = TEST_CRM.get_branches()["data"][0]["id"]
categories_to_filter = [753923]

# CRM : RemonlineAPI
# warehouse :int


app = FastAPI()
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
#     "http://localhost:3000",
#     "http://localhost:88",
#     "https://stupendous-gnome-b5657d.netlify.app/",
#     "https://app.netlify.com/",
#     "https://stupendous-gnome-b5657d.netlify.app/static/js/main.e9b2a2af.js:2:300830",
# ]
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

json_goods: dict


@app.get("/api/v1/allgoods")
def get_all_goods():
    while True:
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

        filtered_goods = filter(lambda x: x['category']["id"] not in categories_to_filter, goods)

        global json_goods

        json_goods = {"data": list(filtered_goods)}
        print("goods successfully updates")
        time.sleep(20)
        get_all_goods()



t = threading.Thread(target=get_all_goods).start()
upd_order_task = threading.Thread(target=update_order_task).start()

@app.get("/api/v1/alldiscounts/")
def get_discounts():
    db = DBConnection("info.db")
    discounts = db.get_all_discounts()
    discounts.sort(key=lambda x: x['month_payment'])
    return discounts


@app.get("/api/v1/no-paid-along-time/")
def no_paid_along_time():
    db = DBConnection("info.db")
    orders = db.no_paid_along_time()
    if not orders:
        return {"success": False, "data": orders}
    return {"success": True, "data": orders}


@app.get("/api/v1/goods")
def get_goods():
    return json_goods


@app.post("/api/v1/client/")
def get_or_post_client(client: ClientModel):
    client_data = TEST_CRM.find_or_create_client(client.phone, client.name)
    return client_data


@app.post("/api/v1/order")
def post_order(order: OrderModel):
    db = DBConnection("info.db")
    client = db.get_client_by_telegram_id(order.telegram_id)
    if not client:
        return {"success": False, "detail": "client not found"}

    order_id = db.post_orders(
        client['id'],
        order.telegram_id,
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
    if not order.prepayment:
        remonline_order = new_remonline_order(OrderIdModel(**{"order_id": order_id}))
    return {"order_id": order_id}


@app.post("/api/v1/postorder/")
def new_remonline_order(order_id: OrderIdModel):
    db = DBConnection("info.db")
    order = db.get_all_orders(order_id=order_id.order_id)[0]

    if order:
        print("order_find")
        phone = order["phone"]
        name = f"{order['name']} {order['last_name']}"
        client = db.get_client_by_id(order['client_id'])
        client_remonline_id = client['id_remonline']
        order_type = TEST_CRM.get_order_types()["data"][0]["id"]

        manager_notes = manager_notes_builder(order=order, goods=json_goods)

        response = TEST_CRM.new_order(branch_id=branch,
                                      order_type=order_type,
                                      client_id=client_remonline_id,
                                      manager_notes=manager_notes

                                      )
        print(response)
        db.add_remonline_order_id(response['data']['id'], order_id.order_id)
        db.connection.close()

        return {"data": response}
    db.connection.close()


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
    db = DBConnection("info.db")
    db.delete_shopping_cart(id)
    db.connection.close()


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


@app.patch("/api/v1/shoppingcart/{id}")
def update_shopping_cart_count(id: int, CountModel: UpdateCountModel):
    db = DBConnection("info.db")
    db.update_shopping_cart_count(id, CountModel.count)
    db.connection.close()


@app.patch("/api/v1/updatettn/")
def update_order_ttn(TTN_data: NewTTNModel):
    db = DBConnection("info.db")
    response = db.update_ttn(TTN_data.order_id, TTN_data.ttn)
    db.connection.close()
    return response





@app.get("/api/v1/visitors/{telegram_id}")
def get_visitors():
    db = DBConnection("info.db")
    response = db.get_visitors()
    db.connection.close()
    return response


@app.get("/api/v1/orderbyttn/{ttn}")
def get_order_by_ttn(ttn: int):
    db = DBConnection("info.db")
    response = db.find_order_by_ttn(ttn)
    db.connection.close()
    return response


@app.get("/api/v1/getorder/{telegram_id}")
def get_order_by_telegram_id(telegram_id: int):
    db = DBConnection("info.db")
    orders = db.get_all_orders(telegram_id)
    db.connection.close()
    return orders


@app.get("/api/v1/getorderbyid/{order_id}")
def get_order_by_id(order_id: int):
    db = DBConnection("info.db")
    order = db.find_order_by_id(order_id)
    db.connection.close()
    return order


@app.get("/api/v1/ordersuma/{telegram_id}")
def get_order_sum(telegram_id: int):
    data = get_shopping_cart(telegram_id)

    to_pay = 0
    for cart in data:
        good_obj = find_good(json_goods["data"], int(cart["good_id"]))
        to_pay += good_obj["price"][PRICE_ID_PROD] * cart["count"]
    return to_pay


@app.get("/api/v1/checkfreelogin/{login}")
def check_free_login(login: str):
    db = DBConnection("info.db")
    client = db.get_client_by_login(login)
    db.connection.close()

    if not client:
        return True
    else:
        return False


@app.post("/api/v1/signin/")
def signin(auth_data: SignInModel):
    db = DBConnection("info.db")
    client = db.get_client_by_login(auth_data.login)
    if not client:
        return {"success": False, "detail": "client not found"}

    if client["password"] != auth_data.password:
        return {"success": False, "detail": "Incorrect password"}
    db.update_client_telegram_id(client_id=client['id'], new_id=auth_data.telegram_id)
    return {"success": True, "detail": "Session has been updated"}


@app.post("/api/v1/AddNewVisitor/{telegram_id}")
def add_new_visitor(telegram_id):
    db = DBConnection("info.db")
    response = db.post_new_visitor(telegram_id)
    db.connection.close()
    return response

@app.post("/api/v1/singup/")
def create_client(client_data: ClientFullModel):
    remoline_client = TEST_CRM.find_or_create_client(client_data.phone, f"{client_data.name} {client_data.last_name}")
    print(client_data)

    if remoline_client is not None:
        db = DBConnection("info.db")
        client = db.post_client(
            id_remonline=remoline_client["data"][0]["id"],
            telegram_id=str(client_data.telegram_id),
            name=client_data.name,
            last_name=client_data.last_name,
            login=client_data.login,
            password=client_data.password,
            phone=client_data.phone)
        db.connection.close()
        return client
    return False


@app.get("/api/v1/isauthendicated/{telegram_id}")
def isauthenticated(telegram_id: int):
    db = DBConnection("info.db")
    client = db.get_client_by_telegram_id(telegram_id)
    if client:
        client_data = dict(client)
        return {
            "success": True,
            "id": client_data["id"],
            "id_remonline": client_data["id_remonline"],
            "name": client_data["name"],
            "last_name": client_data["last_name"],
            "phone": client_data["phone"]
        }
    else:
        return {"success": False}


@app.get("/api/v1/orders")
def get_orders():
    db = DBConnection("info.db")
    orders = db.get_all_orders()
    db.connection.close()
    return orders


@app.get("/api/v1/monthdiscount/{client_id}")
def get_month_discount(client_id: int):
    db = DBConnection("info.db")
    money_spent: int = 0
    orders = db.get_monthly_finished_orders(client_id)

    if not orders:
        return {"success": False, "data": "No orders", "money_spent": money_spent}

    money_spent = get_month_money_spent(orders, json_goods)
    discounts = db.get_all_discounts()
    client_discount = find_discount(money_spent, discounts)
    print("Потрачено:", money_spent)
    if not client_discount:
        return {"success": False, "data": "No discount", "money_spent": money_spent}

    return {"success": True, "data": client_discount, "money_spent": money_spent}


@app.post("/api/v1/discount/")
def post_discount(discount: DiscountModel):
    print(discount)
    db = DBConnection("info.db")
    response = db.create_discount(discount.procent, discount.month_payment)
    db.connection.close()
    return response


@app.delete("/api/v1/discount/{discount_id}")
def delete_discount(discount_id):
    db = DBConnection("info.db")
    response = db.delete_discount(discount_id)
    db.connection.close()
    return response


@app.patch("/api/v1/disactiveorder/{order_id}")
def finish_order(order_id: int):
    db = DBConnection("info.db")
    response = db.deactivate_order(order_id)
    db.connection.close()
    return response


@app.delete("/api/v1/deleteorder/{order_id}")
def drop_order(order_id: int):
    db = DBConnection("info.db")
    response = db.delete_order(order_id)
    db.connection.close()
    return response


@app.get("/api/v1/activeorders")
def get_active_orders():
    db = DBConnection("info.db")
    active_orders = db.get_active_orders()
    db.connection.close()
    return active_orders


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}
