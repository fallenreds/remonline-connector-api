from pydantic import BaseModel
from typing import Any


class ClientModel(BaseModel):
    phone: str
    name: str


class SignInModel(BaseModel):
    login: str
    password: str
    telegram_id: int

class ClientFullModel(BaseModel):
    id_remonline: int = None
    telegram_id: int
    name: str
    last_name: str
    login: str
    password: str
    phone: str


class OrderIdModel(BaseModel):
    order_id: int


class CartModel(BaseModel):
    telegram_id: int
    good_id: int


class UpdateCountModel(BaseModel):
    count: int

class DiscountModel(BaseModel):
    month_payment: int
    procent: int

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
