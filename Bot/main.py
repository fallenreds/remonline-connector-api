import telebot
from telebot import types
from config import BOT_TOKEN
from RemonlineAPI import *

bot = telebot.TeleBot(token=BOT_TOKEN, parse_mode="HTML")
remonline = RemonlineAPI(api_key=REMONLINE_API_KEY_PROD)


@bot.message_handler(commands=['start'])
def start_message(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    catalog_button = types.KeyboardButton("Каталог")
    markup.add(catalog_button)
    bot.send_message(message.chat.id, text='Привет, я ваш менеджер👋.\nЧто вы хотите сделать?', reply_markup=markup)


@bot.message_handler(content_types=["text"])
def catalog(message):
    if message.text == "Каталог":
        markup = types.InlineKeyboardMarkup(row_width=2)
        category_button = types.InlineKeyboardButton("Поиск по категории", callback_data="category")
        text_search = types.InlineKeyboardButton("Поиск по тексту", callback_data='textsearch')
        markup.add(category_button, text_search)
        search_ans = bot.send_message(message.chat.id, text='Выберите способ поиска товара', reply_markup=markup)
    else:
        search_ans = bot.send_message(message.chat.id, text="Я вас не понял, выберите из списка доступных вариантов")


@bot.callback_query_handler(func=lambda call: True)
def inline_callback(call):
    if call.data == 'category':
        category_data = remonline.get_categories().get("data")
        # data = ([category.get("title") for category in category_data])
        noparent = [cat for cat in category_data if "parent_id" not in cat.keys()]
        markup = types.InlineKeyboardMarkup(row_width=len(noparent))
        for cat in noparent:
            markup.add(types.InlineKeyboardButton(text=cat.get("title"), callback_data=cat.get('id')))
        bot.send_message(call.message.chat.id, text='Выберите категорию', reply_markup=markup)
        # for category in data[:8]:
        #     markup.add(types.InlineKeyboardButton(text=category, callback_data=category))
        # bot.send_message(call.message.chat.id, text='Выберите категорию', reply_markup=markup)

    if call.data == 'textsearch':
        bot.send_message(call.message.chat.id, text='Вы выбрали категорию')


bot.infinity_polling()

