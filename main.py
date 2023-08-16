import datetime
import sqlite3
import sys
import time

import requests
from telebot import types

from auxiliary_functions import duration_in_minutes, get_week_days_list
from database import BotDb, CurrentHour
import telebot

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)

days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
recurring_this_week = []


@bot.message_handler(commands=['week'])
def get_week_tasks(message):
    db = BotDb('dairy_db.sql')
    week_tasks = db.get_week_tasks(message.chat.id)
    db.close()
    bot.send_message(message.chat.id, 'на этой неделе вам нужно сделать следующик задачи:')
    for el in week_tasks:
        bot.send_message(message.chat.id, f'{el[1]}')
        bot.send_message(message.chat.id, f'дата выполнения этой задачи {el[2]}')


@bot.message_handler(commands=['day'])
def get_day_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_day_tasks(message.chat.id)
    db.close()
    bot.send_message(message.chat.id, 'Сеодня вам нужно сделать следующик задачи')
    for el in day_tasks:
        bot.send_message(message.chat.id, f'{el}')


@bot.message_handler(commands=['month'])
def get_month_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_month_tasks(message.chat.id)
    db.close()
    for el in day_tasks:
        bot.send_message(message.chat.id, f'{el[1]}')
        bot.send_message(message.chat.id, f'дата выполнения этой задачи {el[2]}')




def cycle_month(message):
    task = 0


@bot.message_handler(commands=['task_edit'])
def get_editing_task_text(message):
    bot.send_message(message.chat.id, 'Ведите задачу для редактирования')

    bot.register_next_step_handler(message, get_editing_task_db)


def get_editing_task_db(message):
    buttons = []
    db = BotDb('dairy_db.sql')
    task = message.text.strip()
    result = db.get_task_editing(message, task)

    markup = types.InlineKeyboardMarkup()

    for i in result:
        buttons.append(types.InlineKeyboardButton(f'{i[1]}', callback_data=f'{i[0]} * {i[1]}'))

    markup.add(*buttons)
    text = f'''Редактируемая задача {result[0][0]} обнаруженв ы следушмщих днях на ближайжую неделю
        пожалуйста выберите день в который вы хотите редактировать данную задачу'''
    if result is not None:
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Выборка пуста')


def update_info(message, editing_task, editing_date):
    data = [editing_task, editing_date]
    bot.send_message(message.chat.id, f'Привет! Введите текст:')

    bot.register_next_step_handler(message, update_task, data=data)


def update_task(message, data):
    db = BotDb('dairy_db.sql')
    db.update_task(message.text, data[0], data[1])
    bot.send_message(message.chat.id, 'Задача изменена')


@bot.message_handler(commands=['start'])
def start(message):
    db = BotDb('dairy_db.sql')
    db.start(message.chat.id)

    bot.send_message(message.chat.id, 'Напишите задачу')
    bot.register_next_step_handler(message, task)


def task(message):
    task_text = f'*{message.text}*'
    bot.send_message(message.chat.id, 'Напишите дату в формате:  2023-06-30')

    #TODO сделать кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for i in get_week_days_list():
        buttons.append(types.KeyboardButton(i))
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)
    bot.register_next_step_handler(message, task_date, task_text=task_text)


def task_date(message, task_text):
    db = BotDb('dairy_db.sql')
    try:
        db.task_date(task_text, message.text, message)
        markup = types.InlineKeyboardMarkup(row_width=2)
        button_week = types.InlineKeyboardButton('Неделя', callback_data=f'{task_text} week')
        button_month = types.InlineKeyboardButton('Месяц', callback_data='month')
        no_repeatable = types.InlineKeyboardButton('Без повторения', callback_data='only_one')
        markup.add(button_week, button_month, no_repeatable)

        bot.send_message(message.chat.id, 'Выберите период повторения:', reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, 'Запись уже существует')



@bot.message_handler(commands=['morning_send'])
def morning_send(message):
    """копия метода из класса для русного вызова"""
    db = BotDb('dairy_db.sql')
    users = db.get_all_users()

    for user in users:

        day_tasks = db.get_day_tasks(user[0])

        for el in day_tasks:
            bot.send_message(user[0], f'задачу  {el[1]} нужно сделать {el[2]}\n')
            x = 0

@bot.message_handler(commands=['done_today_tasks'])
def done_today_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_day_tasks(message.chat.id)
    db.close()

    buttons = []

    markup = types.InlineKeyboardMarkup()

    for i in day_tasks:
        buttons.append(types.InlineKeyboardButton(text=i, callback_data=i))

    markup.add(*buttons)
    bot.send_message(message.chat.id, 'нажмите на выполненную задачу', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def all_callbacks_handler(call):
    today_tasks = BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id)
    task_text = (BotDb('dairy_db.sql').get_task(call.data.split(' * ')[0], call.message.chat.id))
    if (
            call.data is not None and today_tasks is not None and call.data in today_tasks):  # выполнение сегодняшней задачи
        done_today_callback(call)
    elif len(call.data.split('*')) > 2 and call.data.split('*')[1] == task_text and call.data.split('*')[2] == ' week':
        callback_recurring_tasks_many_words_handler(call) #период повторения неделя

    elif call.data == 'only_one':# добавляет задачу без довторения
        bot.send_message(call.message.chat.id, 'Задача добавлена')
    #вызывет функцию редактирования задачи
    elif ((call.data.lstrip('"(').rstrip(')"').split(' * ')[0], call.data.lstrip('"(').rstrip(')"').split(' * ')[1]) in
          BotDb('dairy_db.sql').get_task_editing(call.message, call.data.lstrip('"(').rstrip(')"').split(' * ')[0])):
        editing_task = call.data.lstrip('"(').rstrip(')"').split(' * ')[0]
        editing_date = call.data.lstrip('"(').rstrip(')"').split(' * ')[1]
        update_info(call.message, editing_task, editing_date)

    elif (BotDb('dairy_db.sql').get_task(
            call.data.split(' * ')[0], call.message.chat.id)) and (
            call.data.split('*')[1].replace(" ", "") in days):
        recurring_tasks_week(call)


    # elif call.data.split(' * ')[0] == text[1:-1] and call.data.split('*')[1].replace(" ", "") in days:
    #     recurring_tasks_week(call)




@bot.callback_query_handler(
    func=lambda call: (call.data is not None and BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id) is not None
                       and call.data in BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id))
)
def done_today_callback(call):
    """Обработчик колбэка на выполнение сегодняшней задачи."""
    task_time_add = call.data[:]
    bot.send_message(call.message.chat.id,
                     f''' Ведите время в которое вы начали выполнять задачу {call.data[:]}\nв формате "ЧЧ:ММ"''')

    bot.register_next_step_handler(call.message, add_start_time, task_time_add=task_time_add)


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
    task = call.data.split('*')[0].strip()

    db.recurring_tasks_week(task, day, call.message.chat.id)


def add_start_time(message, task_time_add):
    start_time = message.text

    bot.send_message(message.chat.id, f'Ведите время в которое вы закончили выполнять задачу\n{task_time_add} в формате "ЧЧ:ММ"')

    bot.register_next_step_handler(message, add_end_time, task_time_add=task_time_add, start_time=start_time)


def add_end_time(message, task_time_add, start_time):
    db = BotDb('dairy_db.sql')
    end_time = message.text
    minutes = duration_in_minutes(start_time, end_time)
    db.spent_time_task_add(task_time_add, minutes)

    db.close()

    bot.send_message(message.chat.id,
                     f'на задачу {task_time_add} вы потратили {minutes} минут.\nрезультат сохранен.')


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
