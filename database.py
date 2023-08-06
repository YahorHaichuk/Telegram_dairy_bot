import calendar
import sqlite3
import sys
import time
from datetime import datetime
from threading import Thread

import telebot

from auxiliary_functions import get_week_days_list, convert_to_datetime, get_week_days_dict

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)

recurring_days_list = []
recurring_days_dict = {}


def morning_send():
    db = BotDb('dairy_db.sql')
    users = db.get_all_users()

    for user in users:

        day_tasks = db.day_tasks(user[0])

        for el in day_tasks:
            bot.send_message(user[0], f'задачу  {el[1]} нужно сделать {el[2]}\n')


def noon_send():
    pass


class CurrentHour(Thread):

    def run(self):
        timer = datetime.now()
        hour = timer.hour
        while True:
            if hour == 17:
                morning_send()
                time.sleep(30)
                continue


class BotDb:

    def __init__(self, db_name):
        """Инициализация соеденения с БД."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.date = None
        self.edited_task_text = None
        self.editing_task_date = None
        self.editing_task_text = None


    def create_db(self, chat_id):
        """Создание базы данных. Таблица users и tasks"""

        self.cursor.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER)')

        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT,
            date DATETIME,
            user_id INTEGER,
            elapsed_time INTEGER,
            is_done INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(user_id));'''
        )
        bot.send_message(chat_id, 'Database is created.')
        return self.conn.commit()

    def week_tasks(self, chat_id):
        """Задачи на текущую неделю"""
        today = datetime.today().date()
        week = get_week_days_list()
        sunday = week[-1]
        self.cursor.execute(
            f'SELECT * FROM tasks WHERE date BETWEEN ? AND ? AND user_id = ?',
            (str(today), (str(sunday)), chat_id)
        )
        return self.cursor.fetchall()

    def day_tasks(self, chat_id):
        """Задачи на текущий день"""
        today = datetime.today().date()
        self.cursor.execute(
            f'SELECT * FROM tasks WHERE date = ? AND user_id = ?', (str(today), chat_id)
        )
        return self.cursor.fetchall()

    def month_tasks(self, chat_id):
        """Задачи на текущий месяц"""
        today = datetime.today().date()
        month = str(today).split('-')
        last_day = calendar.monthrange(today.year, today.month)[1]
        month[2] = str(last_day)
        result = '-'.join(month)
        month_object = datetime.strptime(result, "%Y-%m-%d")
        self.cursor.execute(
            f'SELECT * FROM tasks WHERE date BETWEEN ? AND ? AND user_id = ?',
            (str(today), (str(month_object)), chat_id)
        )
        return self.cursor.fetchall()

    def start(self, chat_id):
        """Добавление задачи"""
        self.cursor.execute(f'SELECT user_id FROM users WHERE user_id = {chat_id}')
        user = self.cursor.fetchone()

        if user is None:
            self.cursor.execute('INSERT INTO users VALUES(?)', (chat_id,))
            bot.send_message(chat_id, 'Добро пожаловать в котячй ежедневник ваш id успешно добавлен в базу!')
        else:
            bot.send_message(chat_id, f'Добрый день, ваш чат id {chat_id}, желаю продуктивного дня!')

        return self.conn.commit()

    def task_date(self, text, date, message):
        """Добавление даты выполнения в добавляемую задачу"""
        task = text.replace("*", "")
        self.date = date
        date_str = self.date.strip()
        date = convert_to_datetime(message, date=date_str)
        if date is None:
            sys.exit()
        data = [task, date, message.chat.id, 0, 0]

        self.cursor.execute('INSERT INTO tasks (task, date, user_id, elapsed_time, is_done) VALUES (?,?,?,?,?)', data)

        return self.conn.commit()

    def get_all_users(self):
        """Выборка всех пользователей для автоотправки сообщения"""
        self.cursor.execute(f'SELECT user_id FROM users')
        users = self.cursor.fetchall()

        return users

    def spent_time_task_add(self, task, duration):
        """Добавление затраченного времени на задачу при
            нажатии кнопки вылолнения этой задачи"""
        self.cursor.execute(
            f'UPDATE tasks SET elapsed_time = ? WHERE task = ?', (duration, task)
        )
        self.cursor.execute(
            f'UPDATE tasks SET is_done = 1 WHERE task = ?', (task,)
        )

        return self.conn.commit()

    def recurring_tasks_week(self, task, days, user_id):
        """Добавление повторяюзейся задачи на выбранный день недели"""
        week_days = get_week_days_dict()
        try:
            date = week_days[days]
            task_in_day = self.cursor.execute('SELECT task, date FROM tasks WHERE task = ? AND date = ?', (task, date))
            result = task_in_day.fetchone()

            if days in week_days.keys() and not result:
                self.cursor.execute('INSERT INTO tasks (task, date, user_id, elapsed_time, is_done) VALUES (?,?,?,?,?)',
                                    (task, week_days[days], user_id, 0, 0))
                bot.send_message(user_id, f'Задача {task} добавлена на день {days}')
            else:
                bot.send_message(user_id, 'Вы уже выбрали этот день')

        except KeyError:
            bot.send_message(user_id, 'Выберите день от сегодняшнего и позже')

        return self.conn.commit()

    def task_editing(self):
        pass

    def close(self):
        """Закрытие соеденения с БД."""

        self.conn.close()



