import telebot, config, help, excel

QUESTIONS_DATA = {}

bot = config.bot

def start_survey(questions, user_id, message, excel_name, finish_func, index=0, hi_mes=None, end_mes=None):
    if index == 0:
        QUESTIONS_DATA[user_id] = {}
        if hi_mes:
            bot.send_message(user_id, hi_mes)

    if index >= len(questions):
        if end_mes:
            bot.send_message(user_id, end_mes)
        excel.write_to_excel(message, QUESTIONS_DATA[user_id], excel_name, write_user_info=True)
        data = QUESTIONS_DATA[user_id]
        del QUESTIONS_DATA[user_id]
        finish_func(data, user_id, message)
    else:
        bot.send_message(user_id, str(questions[index]))
        bot.register_next_step_handler(message, get_answer, questions, index, user_id, end_mes, excel_name, finish_func)


def get_answer(message, questions, index, user_id, end_mes, excel_name, finish_func):
    '''
    Принимает ответ ползователя, записывает в словарь, запускает отправку следующего вопроса
    :param end_mes: сообщение в конце опроса
    :param message: сообщение пользователя
    :param questions: все вопросы
    :param index: индекс текущего вопроса с 0
    :param user_id: id пользователя
    :next_step: запускает отправку следующего вопроса
    '''
    if help.is_text(message) and len(message.text) < 512:
        QUESTIONS_DATA[user_id][questions[index]] = message.text
        start_survey(questions, user_id, message, excel_name, finish_func, index=index+1, end_mes=end_mes)
    else:
        bot.send_message(user_id, questions[index] + f'\nОграничение: 500 символов, у вас {len(message.text)}.')
        bot.register_next_step_handler(message, get_answer, questions, index, user_id, end_mes, excel_name, finish_func)