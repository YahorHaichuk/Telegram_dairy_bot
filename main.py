import datetime
import sqlite3
import time
from functools import partial

import requests
from telebot import types

from auxiliary_functions import duration_in_minutes
from bot_main import BotTG
from database import BotDb, CurrentHour
import telebot

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)

days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
start_time_task = None
end_time_task = None
text = None
user_today_tasks = None
current_task_time_add = None
current_task_days_add = None
recurring_this_week = []


@bot.message_handler(commands=['week'])
def get_week_tasks(message):
    BotTG().get_week_tasks(message)


@bot.message_handler(commands=['day'])
def get_day_tasks(message):
    BotTG().get_day_tasks(message)

@bot.message_handler(commands=['month'])
def get_month_tasks(message):
    BotTG().get_month_tasks(message)

@bot.message_handler(commands=['add_task'])
def add_task(message):
    """Добавление кнопок повторения задач"""
    BotTG().add_task(message)
    bot.register_next_step_handler(message, start)


@bot.callback_query_handler(
    func=lambda call: call.data.split()[0] == text and call.data.split()[1] in days_of_week
)
def cycle_month(message):
    task = 0


@bot.message_handler(commands=['task_edit'])
def get_editing_task_text(message):
    BotTG().get_editing_task_text(message)

    bot.register_next_step_handler(message, get_editing_task_db)
    # bot.register_next_step_handler(message, get_editing_task_db)

def get_editing_task_db(message):
    #BotTG().get_editing_task_db(edited_message)
    pass

def get_editing_task_db(message):
    BotTG().get_editing_task_db(message)
    bot.register_next_step_handler(message, get_update_text)


def get_update_text(message, editing_task, editing_date):
    bot.send_message(message.chat.id, editing_task)
    bot.send_message(message.chat.id, editing_date)
    bot.send_message(message.chat.id, message.text)
    # BotTG().update_task(message, editing_task, editing_date)
    #
    # bot.send_message(message.chat.id, 'Задача изменена')




# def update_task(message):
#     editing_task = message.from_user.editing_task
#     editing_date = message.from_user.editing_date
#
#     db = BotDb('dairy_db.sql')
#     db.update_task(message.text, editing_task, editing_date)
#     bot.send_message(message.chat.id, 'Задача изменена')



@bot.message_handler(commands=['start'])
def start(message):
    BotTG().start(message)
    bot.send_message(message.chat.id, 'Напишите задачу')
    bot.register_next_step_handler(message, task)


def task(message):
    BotTG().post_task_text(message)
    #TODO сделать кнопки
    bot.register_next_step_handler(message, task_date)


def task_date(message):
    BotTG().post_task_date(message)



# @bot.callback_query_handler(func=lambda call: True)
# def callback_handler(call):
#     if call.data == 'week':
#         # Если выбрана кнопка "Неделя", создаем подменю для выбора дней недели
#         markup = types.InlineKeyboardMarkup(row_width=3)
#         days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
#         buttons = [types.InlineKeyboardButton(day, callback_data=day) for day in days]
#         markup.add(*buttons)
#
#         # Редактируем сообщение с кнопками, чтобы заменить основное меню на подменю
#         bot.edit_message_text('Выберите день недели:', call.message.chat.id, call.message.message_id, reply_markup=markup)
#     elif call.data == 'month':
#         # Если выбрана кнопка "Месяц", делаем какие-то действия или отправляем другое меню
#         # Например:
#         bot.send_message(call.message.chat.id, 'Вы выбрали "Месяц"')
#     else:
#         # Обработка выбора дня недели или других кнопок, которые вы добавите
#         bot.send_message(call.message.chat.id, f'Вы выбрали день: {call.data}')

@bot.message_handler(commands=['morning_send'])
def morning_send(message):
    """копия метода из класса для русного вызова"""
    db = BotDb('dairy_db.sql')
    users = db.get_all_users()

    for user in users:

        day_tasks = db.day_tasks(user[0])

        for el in day_tasks:
            bot.send_message(user[0], f'задачу  {el[1]} нужно сделать {el[2]}\n')
            x = 0

# def return_day_task_list():
#     db = BotDb('dairy_db.sql')
#     day_tasks = db.day_tasks(message.chat.id)
#     db.close()
#
#     today_tasks = []
#     buttons = []
#     for t in day_tasks:
#         today_tasks.append(t[1])


@bot.message_handler(commands=['done_today_tasks'])
def done_today_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.day_tasks(message.chat.id)
    db.close()

    today_tasks = []
    buttons = []

    markup = types.InlineKeyboardMarkup()

    for t in day_tasks:
        today_tasks.append(t[1])

    for i in today_tasks:
        buttons.append(types.InlineKeyboardButton(text=i, callback_data=i))

    markup.add(*buttons)
    bot.send_message(message.chat.id, 'нажмите на выполненную задачу', reply_markup=markup)
    global user_today_tasks
    user_today_tasks = today_tasks


@bot.callback_query_handler(func=lambda call: True)
def all_callbacks_handler(call):
    if call.data is not None and user_today_tasks is not None and call.data in user_today_tasks:
        done_today_callback(call)
    elif len(call.data.split('*')) > 2 and call.data.split('*')[1] == text[1:-1] and call.data.split('*')[2] == ' week':
        callback_recurring_tasks_many_words_handler(call)

    elif call.data == 'only_one':
        bot.send_message(call.message.chat.id, 'Задача добавлена')

    elif ((call.data.lstrip('"(').rstrip(')"').split(' * ')[0], call.data.lstrip('"(').rstrip(')"').split(' * ')[1]) in
          BotDb('dairy_db.sql').get_task_editing(call.message, call.data.lstrip('"(').rstrip(')"').split(' * ')[0])):
        editing_task = call.data.lstrip('"(').rstrip(')"').split(' * ')[0]
        editing_date = call.data.lstrip('"(').rstrip(')"').split(' * ')[1]
        bot.send_message(
            call.message.chat.id, f'Введите исправленный текст для задачи {editing_task}, в день {editing_date}')
        get_update_text(call.message, editing_task, editing_date)

    elif call.data.split(' * ')[0] == text[1:-1] and call.data.split('*')[1].replace(" ", "") in days:
        recurring_tasks_week(call)




@bot.callback_query_handler(
    func=lambda call: call.data is not None and user_today_tasks is not None and call.data in user_today_tasks
)
def done_today_callback(call):
    """Обработчик колбэка на выполнение сегодняшней задачи."""
    global current_task_time_add
    current_task_time_add = call.data[:]
    bot.send_message(call.message.chat.id,
                     f''' Ведите время в которое вы начали выполнять задачу {call.data[:]}\nв формате "ЧЧ:ММ"''')

    bot.register_next_step_handler(call.message, add_start_time)


def callback_recurring_tasks_many_words_handler(call):
    """Обработка повторяющихя задач периодом в 1 неделю."""
    current_task = call.data.split('*')[1:2][0]

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(day, callback_data=f'{current_task} * {day}') for day in days]
    markup.add(*buttons)
    text = '''Выберите дни недели в которые будет повторятся ваша задача от сегодняшнего дня и до конца недели.\n
            Вы находитесь в режиме выбора дней повтора задач на текущую неделю.\n
            Что бы добавить повторяющмеся задачи на следующую неделю сделайте это в понедельник,
            или добавте задачу в ручную с помошью команды /start\n
            Либо выберите период повторения месяц'''
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


def recurring_tasks_week(call):
    db = BotDb('dairy_db.sql')
    global recurring_this_week
    day = call.data.split('*')[1].replace(" ", "")
    if day not in recurring_this_week:
        recurring_this_week.append(day)
    task = call.data.split('*')[0]

    db.recurring_tasks_week(task, day, call.message.chat.id)


def add_start_time(message):
    global start_time_task
    start_time_task = message.text
    t = current_task_time_add

    bot.send_message(message.chat.id, f'Ведите время в которое вы закончили выполнять задачу\n{t} в формате "ЧЧ:ММ"')

    bot.register_next_step_handler(message, add_end_time)


def add_end_time(message):
    db = BotDb('dairy_db.sql')
    end_time = message.text
    minutes = duration_in_minutes(start_time_task, end_time)
    db.spent_time_task_add(current_task_time_add, minutes)
    db.close()

    bot.send_message(message.chat.id,
                     f'на задачу {current_task_time_add} вы потратили {minutes} минут.\nрезультат сохранен.')


# @bot.callback_query_handler(func=lambda call: True)
# def callback(call):
#     conn = sqlite3.connect('dairy_db.sql')
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM tasks WHERE user_id = ?', (call.message.chat.id,))
#
#     rows = cur.fetchall()
#     info = ''
#     for el in rows:
#         info += f'задачу  {el[1]} нужно сделать {el[2]}\n'
#
#     cur.close()
#     conn.close()
#
#     bot.send_message(call.message.chat.id, info)


def send_time():

    hours = CurrentHour()
    hours.start()


#send_time()

#TODO не работает функция при дисконекте
def bot_polling():
    try:
        bot.polling(none_stop=True)
    except requests.exceptions.ConnectionError or ConnectionResetError:
        time.sleep(5)
        bot_polling()


if __name__ == "__main__":
    bot_polling()
