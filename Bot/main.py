import telebot
from telebot import types
from config import BOT_TOKEN
from RemonlineAPI import *
from dataset.Category import *

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
        category = Category(category_data)
        markup = types.InlineKeyboardMarkup(row_width=8)
        for head in category.get_headers():
            button = types.InlineKeyboardButton(head.title, callback_data=head.id)
            markup.add(button)
        bot.send_message(call.message.chat.id, text="Выберите одну из категорий: ", reply_markup=markup)
    if call.data == 'textsearch':
        bot.send_message(call.message.chat.id, text='Вы выбрали категорию')



bot.infinity_polling()

