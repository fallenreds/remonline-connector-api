from typing import Union
from fastapi import FastAPI
from RestAPI.RemonlineAPI import *
from config import *


app = FastAPI()
CRM = RemonlineAPI(REMONLINE_API_KEY_PROD)

goods = CRM.get_goods(CRM.get_main_warehouse_id())

@app.get("/goods")
async def read_root():
    return goods


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}