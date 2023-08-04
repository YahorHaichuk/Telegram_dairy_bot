import datetime
import sqlite3
import time

from telebot import types

from auxiliary_functions import duration_in_minutes
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
    db = BotDb('dairy_db.sql')
    week_tasks = db.week_tasks(message.chat.id)
    db.close()
    for el in week_tasks:
        bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}\n')


@bot.message_handler(commands=['day'])
def get_day_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.day_tasks(message.chat.id)
    db.close()
    for el in day_tasks:
        bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}\n')


@bot.message_handler(commands=['month'])
def get_month_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.month_tasks(message.chat.id)
    db.close()
    for el in day_tasks:
        bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}\n')


@bot.message_handler(commands=['add_task'])
def add_task(message):
    """Добавление кнопок повторения задач"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    button_week = types.InlineKeyboardButton('Неделя', callback_data='week')
    button_month = types.InlineKeyboardButton('Месяц', callback_data='month')
    no_repeatable = types.InlineKeyboardButton('Без повторения', callback_data='only_one')
    markup.add(button_week, button_month, no_repeatable)
    bot.send_message(message.chat.id, 'Выберите период повторения:', reply_markup=markup)
    bot.register_next_step_handler(message, start)


@bot.callback_query_handler(
    func=lambda call: call.data.split()[0] == text and call.data.split()[1] in days_of_week
)
def cycle_month(message):
    task = 0


@bot.message_handler(commands=['start'])
def start(message):
    db = BotDb('dairy_db.sql')
    db.start(message.chat.id)

    bot.send_message(message.chat.id, 'Напишите задачу')
    bot.register_next_step_handler(message, task)


def task(message):
    global text
    text = f'*{message.text}*'
    bot.send_message(message.chat.id, 'Напишите дату в формате:  2023-06-30')
    bot.register_next_step_handler(message, task_date)


def task_date(message):
    db = BotDb('dairy_db.sql')
    db.task_date(text, message.text, message)

    markup = types.InlineKeyboardMarkup(row_width=2)
    button_week = types.InlineKeyboardButton('Неделя', callback_data=f'{text} week')
    button_month = types.InlineKeyboardButton('Месяц', callback_data='month')
    markup.add(button_week, button_month)

    bot.send_message(message.chat.id, 'Выберите период повторения:', reply_markup=markup)



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
        bot.send_message(call.message.chat.id, 'обработчик многих слов неделя')

    # elif (len(call.data.split('*')) > 2
    #       and call.data.split('*')[1:2][1] == text[1:-1] and call.data.split()[2] == ' week'):
    #     bot.send_message(call.message.chat.id, 'обработчик одного слова неделя')
    elif call.data.split('*')[0] == text[1:-1] and call.data.split('*')[1].replace(" ", "") in days:
        recurring_tasks_week(call)

    x = 1


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
    buttons = [types.InlineKeyboardButton(day, callback_data=f'{current_task}* {day}') for day in days]
    markup.add(*buttons)
    bot.edit_message_text('Выберите день недели:', call.message.chat.id, call.message.message_id, reply_markup=markup)


def recurring_tasks_week(call):
    db = BotDb('dairy_db.sql')
    global recurring_this_week
    day = call.data.split('*')[1].replace(" ", "")
    if day not in recurring_this_week:
        recurring_this_week.append(day)
    task = call.data.split()[0][:-1]

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

bot.polling(none_stop=True)

