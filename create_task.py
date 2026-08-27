import os

import config, help
import base as db
import keyboard

bot = config.bot

TASKS_DATA = {}

def start_creating_task(call, user_id):
    bot.send_message(user_id, 'Введите название для задания (для отмены используйте /cancel):')
    TASKS_DATA[user_id] = {}
    bot.register_next_step_handler(call.message, get_name, user_id)


def get_name(message, user_id):
    max_len = 200
    if help.is_text(message) and len(message.text) < max_len:
        if message.text == '/cancel':
            bot.send_message(user_id, 'Создание отменено')
        else:
            TASKS_DATA[user_id]['name'] = message.text
            bot.send_message(user_id, 'Введите описание для задания:')
            bot.register_next_step_handler(message, get_about, user_id)
    else:
        bot.send_message(user_id, f'Введите название для задания (ограничение {max_len} символов, у вас {len(message.text)}):')
        bot.register_next_step_handler(message, get_name, user_id)


def get_about(message, user_id):
    max_len = 500
    if help.is_text(message) and len(message.text) < max_len:
        if message.text == '/cancel':
            bot.send_message(user_id, 'Создание отменено')
        else:
            TASKS_DATA[user_id]['about'] = message.text
            bot.send_message(user_id, 'Введите целевую аудиторию для задания (кого опрашиваем):')
            bot.register_next_step_handler(message, get_target_people, user_id)
    else:
        bot.send_message(user_id, f'Введите целевую аудиторию для опроса (ограничение {max_len} символов, у вас {len(message.text)}):')
        bot.register_next_step_handler(message, get_about, user_id)


def get_target_people(message, user_id):
    max_len = 500
    if help.is_text(message) and len(message.text) < max_len:
        if message.text == '/cancel':
            bot.send_message(user_id, 'Создание отменено')
        else:
            TASKS_DATA[user_id]['target_people'] = message.text
            bot.send_message(user_id, 'Введите комментарий для исполнителя:')
            bot.register_next_step_handler(message, get_comment, user_id)
    else:
        bot.send_message(user_id, f'Введите целевую аудиторию для опроса (ограничение {max_len} символов, у вас {len(message.text)}):')
        bot.register_next_step_handler(message, get_target_people, user_id)


def get_comment(message, user_id):
    max_len = 500
    if help.is_text(message) and len(message.text) < max_len:
        if message.text == '/cancel':
            bot.send_message(user_id, 'Создание отменено')
        else:
            TASKS_DATA[user_id]['comment'] = message.text
            bot.send_message(user_id, 'Введите цену задания:')
            bot.register_next_step_handler(message, get_price, user_id)
    else:
        bot.send_message(user_id, f'Введите целевую аудиторию для опроса (ограничение {max_len} символов, у вас {len(message.text)}):')
        bot.register_next_step_handler(message, get_comment, user_id)


def get_price(message, user_id):
    max_len = 8
    if help.is_text(message) and len(message.text) < max_len and help.is_digit(message.text):
        if message.text == '/cancel':
            bot.send_message(user_id, 'Создание отменено')
        else:
            if int(message.text) < 5000:
                bot.send_message(user_id,
                                 f'Минимальная стоимость задания - 5000р. Попробуйте ещё раз.')
                bot.register_next_step_handler(message, get_price, user_id)
            else:
                user = db.get_user(user_id)
                if user["money"] >= int(message.text):
                    TASKS_DATA[user_id]['price'] = message.text
                    with open(help.PATH + 'files/Пример_Данных.xlsx', 'rb+') as file:
                        bot.send_document(user_id, file,
                                          caption='Заполните информацию и контакты опрашиваемых, а также создайте столбцы с вопросами, предоставьте файл в формате .xlsx по примеру ниже:')
                    bot.register_next_step_handler(message, get_file, user_id)
                else:
                    bot.send_message(user_id, 'У вас недостаточно средств. Пополните баланс и попробуйте заново.')
    else:
        if help.is_text(message) and message.text == '/cancel':
            bot.send_message(user_id, 'Создание отменено')
        else:
            bot.send_message(user_id,
                         f'Введите положительное число:')
            bot.register_next_step_handler(message, get_price, user_id)


def get_file(message, user_id):
    if message.content_type == 'document':
        if message.document.file_name.endswith(('.xlsx', '.xls')):
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            task_id = db.generate_task_id()

            file_path = os.path.join(help.PATH, 'excel', f'{task_id}.xlsx')
            with open(file_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            TASKS_DATA[user_id]['task_id'] = task_id
            bot.reply_to(message, f'Файл {message.document.file_name} успешно загружен!')
            bot.send_message(user_id, 'Выберите отрасли, к которым относится ваша задача, чтобы мы могли точнее подобрать исполнителей:', reply_markup=keyboard.create_categories_markup(markup=help.categories, save_data='customer_save_categories'))
        else:
            bot.send_message(user_id,
                             f'Заполните информацию и контакты опрашиваемых, а также создайте столбцы с вопросами, предоставьте файл в формате .xlsx по примеру выше:')
            bot.register_next_step_handler(message, get_file, user_id)
    else:
        if help.is_text(message) and message.text == '/cancel':
            bot.send_message(user_id, 'Создание отменено')
        else:
            bot.send_message(user_id,
                         f'Заполните информацию и контакты опрашиваемых, а также создайте столбцы с вопросами, предоставьте файл в формате .xlsx по примеру выше:')
            bot.register_next_step_handler(message, get_file, user_id)