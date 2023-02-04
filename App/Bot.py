import json
from aiogram import Bot, Dispatcher, executor, types, filters
from DB import DBConnection
from config import *
from RestAPI.RemonlineAPI import RemonlineAPI

CRM = RemonlineAPI(REMONLINE_API_KEY_PROD)
warehouse = CRM.get_main_warehouse_id()


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
    return {"data": goods}


bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_message(message):
    greetings_text = f"Здравствуйте, {message.chat.first_name}. \nВы можете просмотреть и купить товары в магазине 🛒, или же просмотреть статус ваших заказов 📦"

    markup_k = types.ReplyKeyboardMarkup(resize_keyboard=True)
    order_status_button = types.KeyboardButton("Статус заказов 📦")
    markup_k.add(order_status_button)
    await bot.send_message(message.chat.id, text=greetings_text, reply_markup=markup_k)


async def make_order(message, data, goods, order):

    text = f'<b>Имя:</b> {order["name"]}\n<b>Фамилия</b>: {order["last_name"]}\n<b>Адрес доставки:</b> {order["nova_post_address"]} \n'
    if order["prepayment"]:
        text +=f'<b>Тип платежа:</b> Нуждается в оплате\n\n'
    else:
        text += f'<b>Тип платежа:</b> Наложенный платеж\n\n'
    to_pay = 0
    for obj in data:
        good = find_good(goods, obj['good_id'])
        to_pay += good["price"][PRICE_ID_PROD] * obj['count']
        text += f"<b>Товар:</b> {good['title']} - Количество: {obj['count']}\n\n"
    text += f"<b>К оплате {to_pay}💳</b>"
    await bot.send_message(message.chat.id, text=text)
    if order["prepayment"] and not order["is_paid"]:
        await bot.send_invoice(message.chat.id,
                               title="Оплатить заказ",
                               description='Для успешного оформления заказа осталось лишь его оплатить',
                               provider_token='5322214758:TEST:4eb03c3b-916d-436b-aba8-3b70b54c711e',
                               currency="uah",
                               is_flexible=False,
                               prices=[types.LabeledPrice(label='Настоящая Машина Времени', amount=int(to_pay)*100)],
                               payload="test"


        )


def find_good(goods, good_id):
    for good in goods:
        if good["id"] == good_id:
            return good


@dp.message_handler(filters.Text(contains="статус", ignore_case=True))
async def check_status(message: types.Message):
    db = DBConnection("info.db")
    orders = db.get_all_orders(int(message.chat.id))
    db.connection.close()
    if len(orders) == 0:
        return await message.reply(f"У вас нет заказов")

    goods = get_all_goods()["data"]
    await message.reply(f"У вас {len(orders)} заказов:")

    for order in orders:
        data = json.loads(order["goods_list"].replace("'", '"'))
        await make_order(message, data, goods, order)


executor.start_polling(dp, skip_updates=True)

# @bot.message_handler(commands=['start'])
# def start_message(message):
#     markup_k = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     markup_i = types.InlineKeyboardMarkup(row_width=3)
#
#     shop_button = types.KeyboardButton("Магазин🛒", web_app=types.WebAppInfo(url=WEB_URL))
#     form_button = types.KeyboardButton("Оформить заказ🛍", web_app=form_web_app)
#     cart_button = types.KeyboardButton("Корзина", web_app=cart_web_app)
#     markup_i.add(shop_button, form_button, cart_button)
#
#
#     bot.send_message(message.chat.id, text='Привет, я ваш менеджер👋.\nЧто вы хотите сделать?', reply_markup=markup_i)
#
#
#
# @bot.message_handler(content_types=["text"])
# def catalog(message):
#     print(message)
#     if message.text == "Каталог":
#         markup = types.InlineKeyboardMarkup(row_width=2)
#         category_button = types.InlineKeyboardButton("Поиск по категории", callback_data="category")
#         text_search = types.InlineKeyboardButton("Поиск по тексту", callback_data='textsearch')
#         markup.add(category_button, text_search)
#         search_ans = bot.send_message(message.chat.id, text='Выберите способ поиска товара', reply_markup=markup)
#     else:
#         search_ans = bot.send_message(message.chat.id, text="Я вас не понял, выберите из списка доступных вариантов")
#
# @bot.message_handler(content_types=["web_app_data"])
# def web_app_handler(message):
#     print(message.web_app_data.data )
#
# @bot.callback_query_handler(func=lambda call: True)
# def inline_callback(call):
#     print(call)
#     form_web_app.check_json()
#     if call.data == 'category':
#         category_data = remonline.get_categories().get("data")
#         category = Category(category_data)
#         markup = types.InlineKeyboardMarkup(row_width=8)
#         for head in category.get_headers():
#             button = types.InlineKeyboardButton(head.title, callback_data=head.id)
#             markup.add(button)
#         bot.send_message(call.message.chat.id, text="Выберите одну из категорий: ", reply_markup=markup)
#     if call.data == 'textsearch':
#         bot.send_message(call.message.chat.id, text='Вы выбрали категорию')
