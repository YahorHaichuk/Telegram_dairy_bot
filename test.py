import calendar
import sys
import threading
import time
from datetime import datetime
from threading import Thread

import telebot
import sqlite3
from auxiliary_functions import get_week_days, convert_to_datetime

text = None
edited_task_text = None
editing_task_date = None
editing_task_text = None
TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'

locker = threading.RLock()

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['create_db'])
def create_db(message):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER)')

    cur.execute(
        '''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT,
        date DATETIME,
        user_id INTEGER,
        elapsed_time INTEGER,
        is_done INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(user_id));'''
    )

    cur.execute('''CREATE TABLE IF NOT EXISTS messages_sends (

    FOREIGN KEY(user_id) REFERENCES users(user_id));''')

    conn.commit()
    conn.close()

    bot.send_message(message.chat.id, 'Database is created.')


@bot.message_handler(commands=['week_tasks'])
def week_tasks(message):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    today = datetime.today().date()
    week = get_week_days()
    sunday = week[-1]
    cur.execute(
        f'SELECT * FROM tasks WHERE date BETWEEN ? AND ? AND user_id = ?', (str(today), (str(sunday)), message.chat.id)
    )
    rows = cur.fetchall()
    for el in rows:
        bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}\n')


@bot.message_handler(commands=['day_tasks'])
def day_tasks(message):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    today = datetime.today().date()
    cur.execute(
        f'SELECT * FROM tasks WHERE date = ? AND user_id = ?', (str(today), message.chat.id)
    )

    rows = cur.fetchall()

    for el in rows:
        bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}')

    bot.send_message(message.chat.id, str(today))
    bot.send_message(message.chat.id, str(rows))


@bot.message_handler(commands=['month_tasks'])
def month_tasks(message):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    today = datetime.today().date()
    month = str(today).split('-')
    last_day = calendar.monthrange(today.year, today.month)[1]
    month[2] = str(last_day)
    result = '-'.join(month)
    month_object = datetime.strptime(result, "%Y-%m-%d")
    cur.execute(
        f'SELECT * FROM tasks WHERE date BETWEEN ? AND ? AND user_id = ?', (str(today), (str(month_object)), message.chat.id)
    )

    rows = cur.fetchall()

    for el in rows:
        bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}')


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    cur.execute(f'SELECT user_id FROM users WHERE user_id = {message.chat.id}')
    data = cur.fetchone()
    if data is None:
        cur.execute('INSERT INTO users VALUES(?)', (message.chat.id,))
        bot.send_message(message.chat.id, 'Добро пожаловать в котячй ежедневник ваш id успешно добавлен в базу!')
    else:
        bot.send_message(message.chat.id, f'Добрый день, ваш чат id {message.chat.id}, желаю продуктивного дня!')

    conn.commit()
    cur.close()
    conn.close()

    bot.send_message(message.chat.id, 'Напишите задачу')
    bot.register_next_step_handler(message, tasks)


def tasks(message):
    global text
    text = message.text.strip()

    bot.send_message(message.chat.id, 'Напишите дату в формате:  2023-06-30')
    bot.register_next_step_handler(message, task_date)


def task_date(message):
    date_str = message.text.strip()
    date = convert_to_datetime(message, date=date_str)
    if date is None:
        sys.exit()
    data = [text, date, message.chat.id, 0, 0]

    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (task, date, user_id, elapsed_time, is_done) VALUES (?,?,?,?,?)', data)

    conn.commit()
    conn.close()

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Список задач', callback_data='tasks'))
    bot.send_message(message.chat.id, 'Задача добавлена', reply_markup=markup)


@bot.message_handler(commands=['task_edit'])
def get_task_edit_message(message):
    bot.send_message(message.chat.id, 'Дату задачи которую нужно редактировать')
    bot.register_next_step_handler(message, get_task_date_edit_message)


def get_task_date_edit_message(message):
    global editing_task_date
    editing_task_date = message.text.strip()
    bot.send_message(message.chat.id, 'Напишите текст задачи которую нужно редактировать')
    bot.register_next_step_handler(message, get_editing_task_text)


def get_editing_task_text(message):
    global editing_task_text
    editing_task_text = message.text.strip()
    bot.send_message(message.chat.id, 'Напишите новый текст задачи')
    bot.register_next_step_handler(message, task_editing)


def task_editing(message):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    global edited_task_text
    global editing_task_text
    date = convert_to_datetime(message, date=editing_task_date)
    edited_task_text = message.text.strip()

    cur.execute(f"UPDATE tasks SET task = '{edited_task_text}'  WHERE task = '{editing_task_text}' AND date = '{date}'")

    cur.execute(f"SELECT task FROM tasks WHERE task = '{edited_task_text}' AND date = '{editing_task_date}'")

    result = cur.fetchone()
    if result is None:
        result = '23232'
    conn.commit()
    bot.send_message(message.chat.id, result)


@bot.message_handler(commands=['tasks'])
def show_tasks(message):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE user_id = ?', (message.chat.id,))
    rows = cur.fetchall()
    for el in rows:
        bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}')

    conn.close()
    conn.close()


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('dairy_db.sql')
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE user_id = ?', (call.message.chat.id,))

    rows = cur.fetchall()
    info = ''
    for el in rows:
        info += f'задачу  {el[1]} нужно сделать {el[2]}\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)

class CurrentHour(Thread):
    def run(self):
        timer = datetime.now()
        hour = timer.hour
        while True:
            if hour == 18:
                time.sleep(30)
                continue


def get_chat_id(message):
    return message.chat.id


def send_time():

    hours = CurrentHour()
    hours.start()


bot.polling(none_stop=True)

