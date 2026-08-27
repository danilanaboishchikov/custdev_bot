import os
from datetime import datetime, timedelta
from difflib import SequenceMatcher
import validators

import pytz

from config import BASE_DIR, ADMINS, ADMIN_CHAT_ID, ARBITRASH_CHAT_URL, DEMO_MODE
PATH = str(BASE_DIR) + '/'
BOT_PERCENT = 0.2
min_pay_sum = 5000

'''
user types:
customer - заказчик
worker - исполнитель

task statuses:
free - в поиске исполнителя
work - в работе (есть исполнитель)
get_finish_comment - ожидает подтверждения заказчика

files:
registration_customers.xlsx - инфа о регистрирующихся заказчиках
registration_workers.xlsx - инфа о регистрирующихся работниках


'''

REGISTRATION_DATA = {}
CATEGORIES_DATA = {}


ADMIN_KEYBOARD = {
    'Получить отчёт': 'admin_get_reports',
    'Арбитраж': 'admin_arbitrash_menu'
}

WORKER_KEYBOARD = {
    'Посмотреть заказы': 'worker_watch_tasks',
    'Мои заказы в работе': 'worker_my_tasks',
    'Мой профиль': 'worker_my_profile',
    'Запросить вывод средств': 'worker_ask_payment'
}

CUSTOMER_KEYBOARD = {
    'Создать задание': 'customer_create_task',
    'Мои задания': 'customer_my_tasks',
    'Мой профиль': 'customer_my_profile',
    'Пополнить баланс': 'customer_put_money'
}

REGISTER_KEYBOARD = {
    'Я заказчик': 'customer_registration',
    'Я исполнитель': 'worker_registration'
}


categories = {
    'edit_category_market': 'Анализ рынка и конкурентов',
    'edit_category_interviews': 'Проведение интервью с пользователями',
    'edit_category_testing': 'Тестирование продуктов и услуг',
    'edit_category_hypothesis': 'Разработка и тестирование гипотез',
    'edit_category_ux': 'Оценка пользовательского опыта (UX)',
    'edit_category_preferences': 'Исследование предпочтений клиентов',
    'edit_category_pricing': 'Разработка и проверка ценовых стратегий',
    'edit_category_marketing': 'Создание и проверка маркетинговых сообщений',
    'edit_category_focusgroups': 'Проведение фокус-групп',
    'edit_category_brand': 'Оценка восприятия бренда и позиционирования'
}




REGISTRATION_CUSTOMER_QUESTIONS = [
    'Как называется ваш проект или компания?',
    'Расскажите кратко о вашем проекте и его задачах.',
    'Какую целевую аудиторию вы хотите опросить?'
]

REGISTRATION_WORKER_QUESTIONS = [
    'Расскажите о вашем опыте работы в сфере Customer Development.',
    'Какой ваш подход к проведению Customer Development? Опишите основные этапы вашей работы.',
    'Есть ли у вас примеры успешных проектов, где вы проводили Customer Development? Опишите их кратко.',
    'Какие результаты вашей работы были наиболее значимыми для ваших предыдущих клиентов?',
]

nothing = ''

def is_text(text):
    try:
        if text.content_type == 'text':
            return True
        else:
            return False
    except:
        return False


def get_moscow_datetime():
    # Получаем текущее время в Москве
    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_tz)

    # Форматируем дату и время в нужный формат
    return current_time.strftime('%d.%m.%Y %H:%M')


def has_delay_exceeded(last_date_str, delay):
    # Получаем текущее время в формате dd.mm.yyyy mm:hh
    cur_date_str = get_moscow_datetime()

    # Преобразуем строки в datetime
    last_date = datetime.strptime(last_date_str, '%d.%m.%Y %H:%M')
    cur_date = datetime.strptime(cur_date_str, '%d.%m.%Y %H:%M')

    # Вычисляем разницу в минутах
    difference = (cur_date - last_date).total_seconds() / 60

    # Проверяем, превышает ли разница заданный delay
    return difference > delay


def are_similar(str1, str2, max_diff=1):
    try:
        a = int(str2)
        if str1 == str2:
            return True
        else: return False
    except:
        # Вычисляем коэффициент сходства
        similarity = SequenceMatcher(None, str1, str2).ratio()

        # Определяем максимальную длину строки для вычисления различий
        max_length = max(len(str1), len(str2))

        # Вычисляем допустимое количество различий
        allowed_differences = max_length - max_diff

        # Сравниваем коэффициент сходства с допустимым значением
        return similarity * max_length >= allowed_differences


def is_link(link):
    return validators.url(link)

def is_digit(n):
    try:
        n = float(n)
        return True
    except Exception as er:
        print(er)
        return False


def generate_info_message(data):
    info_message = ''
    i = 1
    print(data)
    for question, answer in data.items():
        info_message += f'{i}. {question}\n- {answer}\n\n'
        i+=1
    return info_message


def get_match_tasks(events, user):
    match_events = []
    user_category = set(user['category'].split('|'))
    for task in events:
        event_category = set(task['category'].split('|'))
        if len(user_category & event_category) > 0 and task['status'] == 'free':
            match_events.append(task)

    return match_events if len(match_events) > 0 else '-'


def delete_files(task_id):
    try:
        os.remove(PATH + f'excel/{task_id}.xlsx')
    except:
        pass

    try:
        os.remove(PATH + f'content/work_{task_id}.xlsx')
    except:
        pass

