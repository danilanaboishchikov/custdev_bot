import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import KeyboardButton, ReplyKeyboardMarkup
import help

def create_keyboard(values:dict, rows=1):
    '''
    Используется для создания клавиатуры по словарю, может обрабатывать кнопки-ссылки
    :param values: словарь, где ключ - текст кнопки, значение - callback_data
    :param rows: параметр row_wight в клавиатуре
    :return: клавиатуру (markup)
    '''

    keyboard = InlineKeyboardMarkup(row_width=rows)
    for text, data in values.items():
        try:
            if help.is_link(data):
                keyboard.add(InlineKeyboardButton(text=text, url=data))
            else:
                keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
        except Exception as er:
            print(f'Ошибка при создании кнопки в клавиатуре: {er}')

    return keyboard


def create_categories_markup(markup, save_data, user_categories=None):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for data, text in markup.items():
        category = data.split('_')[2]
        if user_categories:
            if category in user_categories:
                keyboard.add(InlineKeyboardButton(text=text+' ✅', callback_data=data+'!'+save_data))
            else:
                keyboard.add(InlineKeyboardButton(text=text, callback_data=data+'!'+save_data))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=data+'!'+save_data))
    print('save', save_data)
    keyboard.add(InlineKeyboardButton(text='Сохранить', callback_data=save_data))

    return keyboard


def create_rate_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(row_width=3)
    butn1 = InlineKeyboardButton(text='1', callback_data=f'rate_user_{user_id}_1')
    butn2 = InlineKeyboardButton(text='2', callback_data=f'rate_user_{user_id}_2')
    butn3 = InlineKeyboardButton(text='3', callback_data=f'rate_user_{user_id}_3')
    butn4 = InlineKeyboardButton(text='4', callback_data=f'rate_user_{user_id}_4')
    butn5 = InlineKeyboardButton(text='5', callback_data=f'rate_user_{user_id}_5')
    keyboard.row(butn1, butn2, butn3)
    keyboard.row(butn4, butn5)

    return keyboard


def generate_payment_markup(label, price, link):
    markup = InlineKeyboardMarkup(row_width=1)
    butn1 = InlineKeyboardButton(text='Оплатить 🔗', url=link)
    butn2 = InlineKeyboardButton(text='Проверить 🔎', callback_data=f'customer_check_payment_{label}_{price}')
    markup.add(butn1, butn2)
    return markup
