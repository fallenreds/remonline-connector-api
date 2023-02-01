from typing import Union
from fastapi import FastAPI
from RestAPI.RemonlineAPI import *
from fastapi.middleware.cors import CORSMiddleware
from config import *


app = FastAPI()
origins = [
    "http://localhost",
    "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
CRM = RemonlineAPI(REMONLINE_API_KEY_PROD)

goods = CRM.get_goods(CRM.get_main_warehouse_id())

@app.get("/api/v1/goods")
async def read_root():
    return goods


# @app.get("/items/{item_id}")
# async def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}