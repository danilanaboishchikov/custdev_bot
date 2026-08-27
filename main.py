import os

import config
import pay
import base as db
import survey
from config import *
import excel
from help import *
from keyboard import *
import create_task

bot = config.bot
os.chdir(config.BASE_DIR)


test_shop = True

def delete(call):
    try:
        bot.delete_message(call.from_user.id, call.message.id)
    except Exception as er:
        print(er)


def show_menu(who, message):
    user_id = message.from_user.id
    if who == 'admin':
        bot.send_message(user_id, f'Доброго времени суток, {message.from_user.first_name}!',
                         reply_markup=create_keyboard(ADMIN_KEYBOARD, 1))
    elif who == 'worker':
        bot.send_message(user_id, f'Доброго времени суток, {message.from_user.first_name}!',
                         reply_markup=create_keyboard(WORKER_KEYBOARD, 1))
    elif who == 'customer':
        bot.send_message(user_id, f'Доброго времени суток, {message.from_user.first_name}!',
                         reply_markup=create_keyboard(CUSTOMER_KEYBOARD, 1))


@bot.message_handler(commands=['start'])
def start(message):
    '''
    Функция, принимающая команду /start проверяет регистрацию, начинает регистрировать пользователя
    '''
    user_id = message.chat.id
    if message.chat.type == 'private':
        if db.is_user_registered(user_id) or user_id in ADMINS:
            if user_id in ADMINS:
                bot.send_message(user_id, f'Доброго времени суток, {message.from_user.first_name}!', reply_markup=create_keyboard(ADMIN_KEYBOARD, 1))
            else:
                user = db.get_user(user_id)

                if user['type'] == 'customer':
                    bot.send_message(user_id, f'Доброго времени суток, {message.from_user.first_name}!', reply_markup=create_keyboard(CUSTOMER_KEYBOARD, 1))
                if user['type'] == 'worker':
                    bot.send_message(user_id, f'Доброго времени суток, {message.from_user.first_name}!', reply_markup=create_keyboard(WORKER_KEYBOARD, 1))
        else:
            bot.send_message(user_id, f'Доброго времени суток, {message.from_user.first_name}! \nДобро пожаловать в наш сервис для проведения Customer Development! Пожалуйста, выберите свою роль, чтобы мы могли настроить ваш профиль.',
                             reply_markup=create_keyboard(REGISTER_KEYBOARD, 2))


@bot.callback_query_handler(lambda x: True)
def callback(call):
    '''
    user types:
    customer - заказчик
    worker - исполнитель

    task statuses:
    free - в поиске исполнителя
    work - в работе (есть исполнитель)
    wait_creator - ожидает подтверждения заказчика
    '''
    user_id, data = call.from_user.id, call.data
    bot.clear_step_handler_by_chat_id(user_id)
    print(data, user_id)
    if 'admin' in data:
        if 'admin_complete_payment_' in data:
            _, _, _, user_id, sum = data.split('_')
            bot.delete_message(ADMIN_CHAT_ID, call.message.id)
            db.update_user_money(user_id, bufer_money_change=f'-{int(float(sum))}')
            bot.send_message(user_id, f'Выплата на сумму {sum} подтверждена администратором!')
        elif 'admin_arbitrash_menu' in data:
            bot.send_message(user_id, 'Введите код (task_id), который отправил вам пользователь:')
            bot.register_next_step_handler(call.message, get_task_id_arbitrash)
        elif 'admin_get_reports' in data:
            with open(PATH+'registration_customers.xlsx', 'rb+') as doc:
                bot.send_document(user_id, doc)
            with open(PATH+'registration_workers.xlsx', 'rb+') as doc:
                bot.send_document(user_id, doc)
            path = db.export_to_excel()
            with open(path, 'rb+') as doc:
                bot.send_document(user_id, doc)
        elif 'pay_worker' in data:
            task_id = data.split('worker_')[1]
            task = db.get_task(task_id)
            price = task['price']
            db.update_user_money(task['creator_id'], bufer_money_change=f'-{price}')
            db.update_user_money(task['worker'], money_change=f'+{price}')
            db.delete_task(task_id)
            db.remove_task_to_user(task['worker'], task_id)
            bot.send_message(task['creator_id'], f'Задание {task["name"]} завершено в пользу исполнителя по решению арбитража.')
            bot.send_message(task['worker'], f'Задание {task["name"]} завершено в вашу пользу по решению арбитража. Деньги начислены на баланс.')
            bot.send_message(user_id, 'Операция проведена успешно!')
            delete(call)
        elif 'pay_customer' in data:
            task_id = data.split('customer_')[1]
            task = db.get_task(task_id)
            price = task['price']
            db.update_user_money(task['creator_id'], money_change=f'+{price}', bufer_money_change=f'-{price}')
            db.delete_task(task_id)
            db.remove_task_to_user(task['worker'], task_id)
            bot.send_message(task['worker'],
                             f'Задание {task["name"]} завершено в пользу заказчика по решению арбитража.')
            bot.send_message(task['creator_id'],
                             f'Задание {task["name"]} завершено в вашу пользу по решению арбитража. Деньги начислены на баланс.')
            bot.send_message(user_id, 'Операция проведена успешно!')
            delete(call)
        elif 'pay_part' in data:
            task_id = data.split('part_')[1]
            bot.send_message(user_id, 'Введите процент, который получит ИСПОЛНИТЕЛЬ, например 0.7 (означает, что 70% денег получил исполнитель, а 30% - заказчик).')
            bot.register_next_step_handler(call.message, get_worker_percent, task_id)
            delete(call)

    elif 'edit_category' in data:
        category = data.split('!')[0].split('_')[2]
        end_data = data.split('!')[1]
        print(category)
        if category not in CATEGORIES_DATA[user_id]:
            CATEGORIES_DATA[user_id].append(category)
        else:
            CATEGORIES_DATA[user_id].remove(category)

        bot.edit_message_reply_markup(user_id, call.message.id,
                                      reply_markup=create_categories_markup(categories, end_data,
                                                                            user_categories=CATEGORIES_DATA[user_id]))
    elif '_about_creator_' in data:
        creator_id = data.split('_about_creator_')[1]
        creator = db.get_user(creator_id)
        if creator['type'] == 'customer':
            type = 'Заказчик'
        else:
            type = 'Исполнитель'
        mes = f'<b>{type} {creator["name"]}:</b>\n\nРейтинг: {"-" if str(int(creator["rates"])) == "-1" else round(float(creator["rates"]), 2)} ({creator["rates_cnt"]})\nВсего заказов: {creator["tasks_cnt"]}'
        bot.send_message(user_id, mes)
        bot.send_message(user_id, str(creator['info']))
        reviews = db.get_rates_by_user_id(creator_id)
        if len(reviews) > 0:
            show_reviews(call, creator_id, 0)
    elif 'show_review_' in data:
        delete(call)
        index, creator_id = int(data.split('_')[2]), int(data.split('_')[3])

        n = len(db.get_rates_by_user_id(creator_id))

        if index < 0:
            index = n - 1
        elif index > n - 1:
            index = 0

        show_reviews(call, int(creator_id), int(index))

    elif '_write_text_' in data:
        send_id = data.split('_write_text_')[1]
        bot.send_message(user_id, 'Отправьте ваше сообщение (для отмены нажмите /cancel):')
        bot.register_next_step_handler(call.message, get_message_to_send, send_id)

    elif 'start_arbitrash' in data:
        bot.send_message(user_id,
                         f'Очень жаль, что вы столкнулись со спорной ситуацией. Чтобы её разрешить, напишите в чат ниже, приложите необходимые скриншоты и код задания: <code>{data.split("start_arbitrash_")[1]}</code>.',
                         reply_markup=create_keyboard({'Группа арбитража': ARBITRASH_CHAT_URL}))


    elif 'rate_user_' in data:
        _, _, rate_id, rate = data.split('_')
        delete(call)
        bot.send_message(user_id, 'Теперь введите отзыв до 200 символов:')
        bot.register_next_step_handler(call.message, get_review, rate_id, rate)

    elif 'customer' in data:
        if data == 'customer_registration':
            bot.edit_message_reply_markup(user_id, call.message.id, reply_markup=create_keyboard({'Я заказчик ✅': '.'}))
            REGISTRATION_DATA[user_id] = {}
            REGISTRATION_DATA[user_id]['type'] = data.split('_')[0]
            survey.start_survey(REGISTRATION_CUSTOMER_QUESTIONS, user_id, call.message, 'registration_customers.xlsx', finish_registration_customer, end_mes='Ваш профиль зарегистрирован как Заказчик. Вы можете начать создавать задачи для исполнения.')
        elif 'my_profile' in data:
            send_profile(user_id, 'customer')
        elif data == 'customer_create_task':
            CATEGORIES_DATA[user_id] = []
            create_task.start_creating_task(call, user_id)
        elif data == 'customer_save_categories':
            delete(call)
            TASKS_DATA = create_task.TASKS_DATA[user_id]
            db.add_task(TASKS_DATA['task_id'], user_id, TASKS_DATA['target_people'], TASKS_DATA['comment'], TASKS_DATA['price'], CATEGORIES_DATA[user_id], TASKS_DATA['name'], TASKS_DATA['about'])
            del CATEGORIES_DATA[user_id]
            db.update_user_money(user_id, money_change='-'+TASKS_DATA['price'], bufer_money_change='+'+TASKS_DATA['price'])
            bot.send_message(user_id, 'Ваше задание успешно создано и доступно исполнителям!')
            show_menu('customer', call)
        elif '_about_work_' in data:
            worker_id = data.split('_work_')[1]
            worker = db.get_user(worker_id)
        elif '_no_work_' in data:
            delete(call)
            _, _, _, task_id, worker_id = data.split('_')
            task = db.get_task(task_id)
            bot.send_message(worker_id, f'Ваша заявка на задание {task["name"]} была отклонена.')
            bot.send_message(user_id, 'Вы успешно отклонили заявку.')
        elif '_start_work_' in data:
            delete(call)
            _, _, _, task_id, worker_id = data.split('_')
            task = db.get_task(task_id)
            if task['worker'] == '-':
                db.add_task_to_user(worker_id, task_id)
                db.update_task_status(task_id, 'work', worker_id)
                bot.send_message(worker_id,
                                 f'Ваша заявка на задание {task["name"]} была принята. Теперь вы можете найти доп. информацию в меню "Мои заказы в работе" и сдать работу там, после выполнения.')
                bot.send_message(user_id, 'Вы успешно одобрили исполнителя. Статус задания переведён в работу.')
            else:
                bot.send_message(user_id, 'Вы уже назначили исполнителя на этот заказ.')
        elif 'my_tasks' in data:
            tasks = db.get_user_tasks(user_id)
            markup = InlineKeyboardMarkup(row_width=1)
            cnt = 0
            for task in tasks:
                markup.add(InlineKeyboardButton(text=task['name'], callback_data=f'customer_get_task_{task["task_id"]}'))
                cnt += 1
            if cnt > 0:
                bot.send_message(user_id, 'Ваши задания:', reply_markup=markup)
            else:
                bot.send_message(user_id, 'У вас пока нет заданий.')
        elif '_get_task_' in data:
            task_id = data.split('_get_task_')[1]
            task = db.get_task(task_id)

            if task:
                if task['status'] == 'free':
                    markup = {'Удалить задание': f'customer_delete_task_{task_id}',
                              'Статус: в поиске 🔎': '.'}
                    mes = f"<b>{task['name']}</b>\n\n<i>{task['about']}</i>\n\n<b>Целевая аудитория:</b> {task['target_people']}\n\n<b>Цена: </b>{task['price']}"
                    bot.send_message(user_id, mes, reply_markup=create_keyboard(markup, 1))
                elif task['status'] == 'work':
                    markup = {'Написать исполнителю': f'customer_write_text_{task["worker"]}',
                              'Статус: в работе 👨‍💻': '.'}
                    mes = f"<b>{task['name']}</b>\n\n<i>{task['about']}</i>\n\n<b>Целевая аудитория:</b> {task['target_people']}\n\n<b>Цена: </b>{task['price']}"
                    bot.send_message(user_id, mes, reply_markup=create_keyboard(markup, 1))
                elif task['status'] == 'wait_creator':
                    markup = {'Подтвердить выполнение ✅': f'customer_finish_task_{task_id}',
                              'Отправить на доработку ✏': f'customer_continuous_task_{task_id}',
                              'Арбитраж': f'customer_start_arbitrash_{task_id}',
                              'Статус: ожидает проверки ✅': '.'}
                    mes = f"Результат работы исполнителя выше 👆\n\n<b>{task['name']}</b>\n\n<i>{task['about']}</i>\n\n<b>Целевая аудитория:</b> {task['target_people']}\n\n<b>Цена: </b>{task['price']}\n\n<b>Комментарий Исполнителя:</b> <i>{task['report']}</i>"
                    with open(PATH + f'content/work_{task_id}.xlsx', 'rb+') as file:
                        bot.send_document(user_id, file, caption=mes, reply_markup=create_keyboard(markup, 1))
            else:
                delete(call)
                bot.send_message(user_id, 'Задание больше недоступно.')
        elif '_delete_task_' in data:
            task_id = data.split('_delete_task_')[1]
            task = db.get_task(task_id)
            if task and task['status'] == 'free':
                db.delete_task(task_id)
                delete(call)
                db.update_user_money(user_id, f'+{task["price"]}', f'-{task["price"]}')
                bot.send_message(user_id, 'Задание успешно удалено. Деньги возращены из буфера на активный счёт.')
                show_menu('customer', call)
            else:
                delete(call)
                bot.answer_callback_query(call.id, text="Это действие недоступно!", show_alert=True)
        elif '_finish_task_' in data:
            task_id = data.split('_task_')[1]
            delete(call)
            task = db.get_task(task_id)
            if task and task['status'] == 'wait_creator':
                db.delete_task(task_id)

                delete_files(task_id)

                db.update_user_money(user_id, bufer_money_change=f'-{task["price"]}')
                db.update_user_money(task["worker"], money_change=f'+{task["price"]}')
                db.update_user_task_cnt(user_id)
                db.update_user_task_cnt(task["worker"])
                db.remove_task_to_user(task["worker"], task_id)

                bot.send_message(user_id, f'Задание завершено. С вашего счёта списано {task["price"]} рублей.\nПожалуйста, оцените исполнителя.', reply_markup=create_rate_keyboard(task["worker"]))
                bot.send_message(task["worker"], f'Задание завершено. На ваш счёт поступило {task["price"]} рублей.\nПожалуйста, оцените заказчика.', reply_markup=create_rate_keyboard(user_id))

                show_menu('customer', call)
            else:
                bot.answer_callback_query(call.id, text="Это действие недоступно!", show_alert=True)
        elif '_continuous_task_' in data:
            task_id = data.split('_task_')[1]
            task = db.get_task(task_id)
            if task and task['status'] == 'wait_creator':
                db.update_task_status(task_id, 'work')
                delete(call)
                show_menu('customer', call)

                bot.send_message(user_id, 'Задание возращено в работу. Отправьте исполнителю необходимые правки ччерез меню "Мои задания".')
                bot.send_message(task["worker"], 'Задание возращено в работу по решению заказчика.')
            else:
                delete(call)
                bot.answer_callback_query(call.id, text="Это действие недоступно!", show_alert=True)
        elif 'put_money' in data:
            bot.send_message(user_id, 'На какую сумму хотите пополнить? (Комиссия 3%, минимальная сумма: 5000р) \nВведите целое положительное число.')
            bot.register_next_step_handler(call.message, get_price_to_put)
        elif '_check_payment_' in data:
            _, _, _, label, price = data.split('_')
            balance_amount = int(float(price))
            payment_amount = round(balance_amount / 0.97)

            if pay.check_payment(label, payment_amount) or test_shop:
                db.update_user_money(user_id, money_change=f'+{balance_amount}')
                bot.send_message(user_id, f'Успешное пополнение на {balance_amount} рублей!')
                show_menu('customer', call)
            else:
                bot.answer_callback_query(call.id, text="Вы не отправили деньги, попробуйте ещё раз позже.", show_alert=True)


    elif 'worker' in data:
        if data == 'worker_registration':
            bot.edit_message_reply_markup(user_id, call.message.id, reply_markup=create_keyboard({'Я исполнитель ✅': '.'}))
            REGISTRATION_DATA[user_id] = {}
            REGISTRATION_DATA[user_id]['type'] = data.split('_')[0]
            survey.start_survey(REGISTRATION_WORKER_QUESTIONS, user_id, call.message, 'registration_workers.xlsx', worker_registration)

        elif data == 'worker_save_categories':
            delete(call)
            db.add_user(user_id, call.from_user.first_name, call.from_user.username, REGISTRATION_DATA[user_id]['type'], REGISTRATION_DATA[user_id]['info'], CATEGORIES_DATA[user_id])
            del REGISTRATION_DATA[user_id]
            del CATEGORIES_DATA[user_id]

            bot.send_message(user_id, 'Ваш профиль зарегистрирован как Исполнитель. Вы можете начать просматривать задачи и выбирать те, которые вам интересны.')
            show_menu('worker', call)
        elif data == 'worker_save_new_categories':
            delete(call)
            db.update_user_category(user_id, CATEGORIES_DATA[user_id])
            del CATEGORIES_DATA[user_id]

            bot.send_message(user_id,
                             'Успешно изменено!')
            show_menu('worker', call)
        elif 'my_profile' in data:
            send_profile(user_id, 'worker')
        elif call.data == 'worker_watch_tasks':
            show_match_events(call, 0)
        elif 'worker_show_task_' in data:
            delete(call)
            n = len(get_match_tasks(db.get_all_tasks(), db.get_user(user_id)))
            index = int(data.split('_task_')[1])

            if index < 0:
                index = n-1
            elif index > n-1:
                index = 0

            show_match_events(call, index)
        elif '_send_ask_' in data:
            task_id = data.split('_send_ask_')[1]
            task = db.get_task(task_id)
            user = db.get_user(user_id)

            if str(user_id) in task["regs"]:
                delete(call)
                bot.send_message(user_id, 'Вы уже подавали заявку!')
                show_menu('worker', call)
            else:
                db.add_reg_to_task(task_id, str(user_id))

                if call.from_user.username:
                    name = f'<a href="https://t.me/{call.from_user.username}">{call.from_user.first_name}</a>'
                else:
                    name = call.from_user.first_name

                mes = f'Новая заявка на задание {task["name"]}! 🔔\n\nПользователь {name} с рейтингом {"-" if str(int(user["rates"])) == "-1" else round(float(user["rates"]), 2)} подал заявку на ваше задание.'

                bot.send_message(task["creator_id"], mes, reply_markup=create_keyboard({'Одобрить исполнителем ✅': f'customer_start_work_{task_id}_{user_id}',
                                                                                        'Отказать ❌': f'customer_no_work_{task_id}_{user_id}',
                                                                                        'Об исполнителе': f'customer_about_creator_{user_id}'}))
        elif 'my_tasks' in data:
            user = db.get_user(user_id)
            if len(user['taken_tasks']) > 1:
                tasks = user['taken_tasks'].split('|')
                markup = InlineKeyboardMarkup(row_width=1)
                cnt = 0
                for i in tasks:
                    task = db.get_task(i)
                    if task:
                        markup.add(InlineKeyboardButton(text=task['name'], callback_data=f'worker_get_task_{i}'))
                        cnt += 1

                if cnt > 0:
                    bot.send_message(user_id, 'Ваши задания, взятые в работу:', reply_markup=markup)
                else:
                    bot.send_message(user_id, 'Нет взятых заданий')
            else:
                bot.send_message(user_id, 'Нет взятых заданий')
        elif '_get_task_' in data:
            task_id = data.split('_get_task_')[1]
            task = db.get_task(task_id)

            if task and task['status'] == 'work':
                markup = {'Написать заказчику': f'worker_write_text_{task["creator_id"]}',
                          'Сдать на проверку': f'worker_finish_task_{task["task_id"]}',
                          'Арбитраж': f'worker_start_arbitrash_{task_id}',
                          'Статус: в работе 👨‍💻': '.'}
                mes = f"<b>{task['name']}</b>\n\n<i>{task['about']}</i>\n\n<b>Целевая аудитория:</b> {task['target_people']}\n\n<b>Комментарий: {task['comment']}</b>\n\n<b>Цена: </b>{task['price']}"
                with open(PATH + f'excel/{task_id}.xlsx', 'rb+') as file:
                    bot.send_document(user_id, file, caption=mes, reply_markup=create_keyboard(markup, 1))
            elif task and task['status'] == 'wait_creator':

                markup = {'Написать заказчику': f'worker_write_text_{task["creator_id"]}',
                          'Арбитраж': f'worker_start_arbitrash_{task_id}',
                          'Статус: ожидает проверки ✅': '.'}
                mes = f"Ваш отчёт выше 👆\n\n<b>{task['name']}</b>\n\n<i>{task['about']}</i>\n\n<b>Целевая аудитория:</b> {task['target_people']}\n\n<b>Комментарий: {task['comment']}</b>\n\n<b>Цена: </b>{task['price']}"
                with open(PATH+f'content/work_{task_id}.xlsx', 'rb+') as file:
                    bot.send_document(user_id, file, caption=mes, reply_markup=create_keyboard(markup, 1))
            else:
                delete(call)
                bot.answer_callback_query(call.id, text="Это действие недоступно!", show_alert=True)
        elif 'finish_task' in data:
            task_id = data.split('finish_task_')[1]
            task = db.get_task(task_id)
            if task and task['status'] == 'work':
                bot.send_message(user_id,
                                 'Отлично! Предоставьте, пожалуйста, отчёт по проделанной работе в виде заполненной таблицы excel, которую вам ранее прислал бот.')
                bot.register_next_step_handler(call.message, get_finish_file, task_id)
            else:
                delete(call)
                bot.answer_callback_query(call.id, text="Это действие недоступно!", show_alert=True)
        elif '_ask_payment' in data:
            user = db.get_user(user_id)
            bot.send_message(user_id, f'Ваш баланс: {user["money"]}. Сколько вы хотите вывести?')
            bot.register_next_step_handler(call.message, get_money_to_pay, user["money"])
        elif data == 'worker_change_categories':
            user = db.get_user(user_id)
            categ = user['category']
            if '|' in categ:
                categ = categ.split('|')
            else:
                categ = [categ]
            bot.send_message(user_id, 'В каких отраслях вы можете наиболее профессионально выполнять задачи?',
                             reply_markup=create_categories_markup(categories, f'worker_save_new_categories', user_categories=categ))
            CATEGORIES_DATA[user_id] = categ


def get_worker_percent(message, task_id):
    user_id = message.chat.id
    print(float(message.text) > 0, float(message.text) < 1, float(message.text), is_text(message.text))
    if is_text(message) and is_digit(message.text) and len(message.text) < 6 and float(message.text) > 0 and float(message.text) < 1:
        if message.text != '/cancel':
            task = db.get_task(task_id)
            price = task['price']
            x = float(message.text) # исполнитель
            y = 1 - x # заказчик
            db.update_user_money(task['creator_id'], money_change=f'+{int(price * y)}', bufer_money_change=f'-{int(price)}')
            db.update_user_money(task['worker'], money_change=f'+{int(price * x)}')
            db.delete_task(task_id)
            db.remove_task_to_user(task['worker'], task_id)
            bot.send_message(task['worker'],
                             f'Задание {task["name"]} завершено частичной оплатой, вы получили {float(x)*100}%.')
            bot.send_message(task['creator_id'],
                             f'Задание {task["name"]} завершено частичной оплатой, вы получили {float(y)*100}%.')
            bot.send_message(user_id, 'Операция проведена успешно!')
        else:
            bot.send_message(user_id, 'Отменено.')
    else:
        bot.send_message(user_id,
                         'Введите процент, который получит ИСПОЛНИТЕЛЬ, например 0.725 (означает, что 72.5% денег получил исполнитель, а 27.5% - заказчик).')
        bot.register_next_step_handler(message, get_worker_percent, task_id)

def get_task_id_arbitrash(message):
    user_id = message.chat.id
    if is_text(message) and len(message.text) < 11:
        if message.text != '/cancel':
            task = db.get_task(message.text)
            if task:
                mes = f"<b>{task['name']}</b>\n\n<i>{task['about']}</i>\n\n<b>Целевая аудитория:</b> {task['target_people']}\n\n<b>Цена: </b>{task['price']}"
                bot.send_message(user_id, mes, reply_markup=create_keyboard({'Оплатить исполнителю': f'admin_pay_worker_{task["task_id"]}', 'Вернуть деньги заказчику': f'admin_pay_customer_{task["task_id"]}', 'Частичная оплата': f'admin_pay_part_{task["task_id"]}'}))
            else:
                bot.send_message(user_id,
                                 'Введите код (task_id), который отправил вам пользователь (ведённый task_id не найден), для отмены отправьте /cancel:')
                bot.register_next_step_handler(message, get_task_id_arbitrash)
        else:
            bot.send_message(user_id, 'Отменено.')
    else:
        bot.send_message(user_id, 'Введите код (task_id), который отправил вам пользователь:')
        bot.register_next_step_handler(message, get_task_id_arbitrash)

def get_money_to_pay(message, max):
    user_id = message.chat.id
    if is_text(message) and is_digit(message.text) and len(message.text) < 7 and float(message.text) <= float(max):
        bot.send_message(user_id, 'Деньги перемещены в буфер, укажите номер телефона или карты, куда хотите получить деньги (будьте внимательны, иначе деньги могут уйти не туда):')
        bot.register_next_step_handler(message, get_payment_card, message.text)
    else:
        user = db.get_user(user_id)
        bot.send_message(user_id, f'Ваш баланс: {user["money"]}. Сколько вы хотите вывести? Нельзя выводить больше имеющейся суммы.')
        bot.register_next_step_handler(message, get_money_to_pay, max)


def get_payment_card(message, sum):
    user_id = message.chat.id
    sum = float(sum)
    if is_text(message) and is_digit(message.text) and len(message.text) < 40:
        db.update_user_money(user_id, f'-{int(sum)}', f'+{int(sum)}')
        bot.send_message(user_id, f'Отлично, {sum*(1-BOT_PERCENT)} рублей ({sum*BOT_PERCENT} рублей - комиссия сервиса) поступят на ваш счёт ({message.text}) в течение некоторого времени.')
        bot.send_message(ADMIN_CHAT_ID, f'Запрос на вывод средств от {"@"+message.from_user.username if message.from_user.username else message.from_user.first_name}:\nСумма: {sum*(1-BOT_PERCENT)} рублей\nРеквизиты: {message.text}\n\nКомиссия бота: {sum*BOT_PERCENT} рублей', reply_markup=create_keyboard({'Подтвердить выплату': f'admin_complete_payment_{user_id}_{sum}'}))
    else:
        bot.send_message(user_id,
                         'Укажите номер телефона или карты, куда хотите получить деньги (будьте внимательны, иначе деньги могут уйти не туда):')
        bot.register_next_step_handler(message, get_payment_card, sum)

def get_price_to_put(message):
    user_id = message.chat.id

    if is_text(message) and is_digit(message.text) and len(message.text) < 7 and int(message.text) >= min_pay_sum:
        balance_amount = int(message.text)
        payment_amount = round(balance_amount / 0.97)
        link, label = pay.create_payment(payment_amount)

        bot.send_message(user_id, f'К оплате {payment_amount} рублей. \nПерейдите по ссылке, переведите деньги и нажмите кнопку "Проверить платёж" ниже 👇', reply_markup=generate_payment_markup(label, balance_amount, link))
    else:
        bot.send_message(user_id, 'На какую сумму хотите пополнить? Введите целое положительное число от 5000р.')
        bot.register_next_step_handler(message, get_price_to_put)



def get_review(message, rate_id, rate):
    if is_text(message) and len(message.text) < 200:
        db.add_rate(rate_id, message.chat.id, message.text, rate)
        db.update_user_rate(rate_id, rate)
        bot.send_message(message.chat.id, 'Спасибо за отзыв!')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, введите отзыв до 200 символов:')
        bot.register_next_step_handler(message, get_review, rate_id, rate)


def get_finish_file(message, task_id):
    user_id = message.chat.id
    if message.content_type == 'document':
        if message.document.file_name.endswith(('.xlsx', '.xls')):
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            file_path = os.path.join('content', f'work_{task_id}.xlsx')
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, f'Файл {message.document.file_name} успешно загружен!')
            bot.send_message(user_id,
                             'Теперь вы можете отправить комментарий, ссылку на облачное хранилище с доп. материалами и т.д.',)
            bot.register_next_step_handler(message, get_finish_comment, task_id)
        else:
            bot.send_message(user_id,
                             'Отлично! Предоставьте, пожалуйста, отчёт по проделанной работе в виде заполненной таблицы excel, которую вам ранее прислал бот.')
            bot.register_next_step_handler(message, get_finish_file, task_id)
    else:
        bot.send_message(user_id,
                         'Отлично! Предоставьте, пожалуйста, отчёт по проделанной работе в виде заполненной таблицы excel, которую вам ранее прислал бот.')
        bot.register_next_step_handler(message, get_finish_file, task_id)


def get_finish_comment(message, task_id):
    if is_text(message) and len(message.text) < 1024:
        db.set_report(task_id, message.text)
        db.update_task_status(task_id, 'wait_creator')
        task = db.get_task(task_id)

        bot.send_message(message.chat.id, 'Отчёт отправлен, ожидайте решения.')
        bot.send_message(task['creator_id'], f'Пришёл отчёт по заданию {task["name"]}. С ним можно ознакомиться в меню "Мои задания".')
    else:

        bot.send_message(message.chat.id,
                         'Теперь вы можете отправить комментарий, ссылку на облачное хранилище с доп. материалами и т.д. Ограничение 1024 символа.', )
        bot.register_next_step_handler(message, get_finish_comment, task_id)


def finish_registration_customer(data, user_id, message):
    REGISTRATION_DATA[user_id]['info'] = generate_info_message(data)
    db.add_user(user_id, message.from_user.first_name, message.from_user.username, REGISTRATION_DATA[user_id]['type'],
                REGISTRATION_DATA[user_id]['info'], '-')
    show_menu('customer', message)
    del REGISTRATION_DATA[user_id]

def worker_registration(data, user_id, message):
    REGISTRATION_DATA[user_id]['info'] = generate_info_message(data)
    bot.send_message(user_id, 'В каких отраслях вы можете наиболее профессионально выполнять задачи?',
                     reply_markup=create_categories_markup(categories, f'worker_save_categories'))
    CATEGORIES_DATA[user_id] = []

def send_profile(user_id, type):
    user = db.get_user(user_id)
    if type == 'customer':
        mes = f'<b>🆔 Ваш профиль #{user_id}:</b>\n\n<b>Имя:</b> {user["name"]}\n<b>Ник:</b> @{user["username"]}\n<b>Тип аккаунта:</b> Заказчик\n\n<b>Деньги на счету:</b> {user["money"]}₽\n<b>Деньги в буфере:</b> {user["bufer_money"]}\n\n<b>Рейтинг:</b> {"-" if str(int(user["rates"])) == "-1" else round(float(user["rates"]), 2)} ({user["rates_cnt"]})\n<b>Заданий завершено:</b> {user["tasks_cnt"]}'
        bot.send_message(user_id, mes)
    else:
        mes = f'<b>🆔 Ваш профиль #{user_id}:</b>\n\n<b>Имя:</b> {user["name"]}\n<b>Ник:</b> @{user["username"]}\n<b>Тип аккаунта:</b> Исполнитель\n\n<b>Деньги на счету:</b> {user["money"]}₽\n<b>Деньги в буфере:</b> {user["bufer_money"]}₽\n\n<b>Рейтинг:</b> {"-" if str(int(user["rates"])) == "-1" else round(float(user["rates"]), 2)} ({user["rates_cnt"]})\n<b>Заданий выполнено:</b> {user["tasks_cnt"]}'
        bot.send_message(user_id, mes, reply_markup=create_keyboard({'Поменять отрасли': 'worker_change_categories'}))
    bot.send_message(user_id, f'<b>О себе:</b>\n\n{user["info"]}')

def show_reviews(call, creator_id, index):
    user_id = call.from_user.id

    reviews = db.get_rates_by_user_id(creator_id)
    review = reviews[index]
    from_user = db.get_user(review['from_id'])

    mes = f'<b>Отзыв от {from_user["name"]} (Оценка: {round(float(review["rate"]), 2)}):</b>\n\n<i>{review["text"]}</i>'
    markup = InlineKeyboardMarkup(row_width=1)
    markup.row(InlineKeyboardButton(text='⬅', callback_data=f'show_review_{index-1}_{creator_id}'),
                                                InlineKeyboardButton(text='➡', callback_data=f'show_review_{index+1}_{creator_id}'))
    bot.send_message(user_id, mes, reply_markup=markup)


def show_match_events(call, index):
    user_id = call.from_user.id

    tasks = db.get_all_tasks()
    user = db.get_user(user_id)
    match_tasks = get_match_tasks(tasks, user)

    if match_tasks != '-':
        task = match_tasks[index]

        if str(user_id) in task['regs']:
            send_ask, ask_data = 'Заявка подана ✔', '.'
        else:
            send_ask, ask_data = 'Отправить заявку', f'worker_send_ask_{task["task_id"]}'

        mes = f"<b>{task['name']}</b>\n\n<i>{task['about']}</i>\n\n<b>Целевая аудитория:</b> {task['target_people']}\n\n<b>Цена: </b>{task['price']}"
        markup = {'О заказчике': f'worker_about_creator_{task["creator_id"]}', send_ask: ask_data}
        markup = create_keyboard(markup, 2).row(InlineKeyboardButton(text='⬅', callback_data=f'worker_show_task_{index-1}'),
                                                InlineKeyboardButton(text='➡', callback_data=f'worker_show_task_{index+1}'))
        bot.send_message(user_id, mes, reply_markup=markup)

    else:
        bot.send_message(user_id, 'Пока что нет доступных заданий, попробуйте расширить фильтры.')


def get_message_to_send(message, send_id):
    if is_text(message) and message.text == '/cancel':
        bot.send_message(message.chat.id, 'Отменено.')
    else:
        bot.forward_message(send_id, message.chat.id, message.id)
        mes = f'👆🔔 Сообщение от {message.from_user.first_name} {f"(@{message.from_user.username})" if message.from_user.username else nothing}.'
        bot.send_message(send_id, mes,
                         reply_markup=create_keyboard({'Ответить': f'reply_write_text_{message.chat.id}'}))
        bot.send_message(message.chat.id, 'Сообщение переслано.')


if __name__ == '__main__':
    if not os.getenv('TELEGRAM_BOT_TOKEN'):
        raise RuntimeError('Set TELEGRAM_BOT_TOKEN in .env before running the bot.')
    bot.infinity_polling(timeout=120)
