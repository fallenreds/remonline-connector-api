import json
from config import PRICE_ID_PROD
from DB import DBConnection


def find_good(goods, good_id):
    for good in goods:
        if good["id"] == good_id:
            return good


def manager_notes_builder(order, goods):
    name = f"{order['name']} {order['last_name']}"
    phone = f"{order['phone']}"
    address = f"{order['nova_post_address']}"
    prepayment = "Предоплата" if order["prepayment"] else "Наложенный платеж"
    goods_list = json.loads(order["goods_list"].replace("'", '"'))
    goods_info = f"ФИО: {name}\nТелефон: {phone}\nАдрес: {address}\nТип платежа: {prepayment}"

    for obj in goods_list:
        good = find_good(goods["data"], obj['good_id'])
        goods_info += f"\n\nТовар: {good['title']} - Количество: {obj['count']}"

    return goods_info


def build_order_suma(order: dict, goods: dict):
    goods_list = json.loads(order["goods_list"].replace("'", '"'))

    for selected_good in goods_list:
        good = find_good(goods['data'], selected_good['good_id'])
        print("Сумма заказа", good['price'][PRICE_ID_PROD] * selected_good['count'])
        return good['price'][PRICE_ID_PROD] * selected_good['count']


def find_discount(money_spent, discounts):
    discounts.sort(key=lambda x: x['month_payment'])
    for discount in discounts[::-1]:
        if money_spent >= discount['month_payment']:
            return discount


def get_month_money_spent(orders, all_goods):
    money_spent: int = 0
    for order in orders:
        money_spent += build_order_suma(order, all_goods)
    return money_spent


def get_month_money_spent_by_client_id(client_id, all_goods):
    db = DBConnection("info.db")
    orders = db.get_monthly_finished_orders(client_id)
    db.connection.close()
    return get_month_money_spent(orders, all_goods)
