import calendar
import sqlite3
import sys
from datetime import datetime

import shutil
import os

import telebot


from auxiliary_functions import get_week_days_list, convert_to_datetime, get_week_days_dict, days_until_end_of_month, \
    get_days_until_today, get_days_of_current_week

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)

recurring_days_list = []
recurring_days_dict = {}



class BotDb:

    def __init__(self, db_name):
        """Инициализация соеденения с БД."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

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

    def get_task_range_week(self, task, chat_id):
        """Выбирает таск от пользователя для проверки условия на добавление повтора в неделю"""
        task = task.split('* ')
        if task[0][0] == '*':
            task[0] = task[0][1:]
        data = get_week_days_list()
        placeholders = ', '.join('?' for _ in data)
        query = f'SELECT task FROM tasks WHERE task = ? AND user_id = ? AND date IN ({placeholders})'
        params = (task[0], chat_id) + tuple(data)
        self.cursor.execute(query, params)
        x = self.cursor.fetchone()
        return x[0]

    def get_task_range_month(self, task, chat_id):
        """Выбирает таск от пользователя для проверки условия на добавление повтора в неделю"""
        task = task.split('* ')
        if task[0][0] == '*':
            task[0] = task[0][1:]
        data = days_until_end_of_month()
        placeholders = ', '.join('?' for _ in data)
        query = f'SELECT task FROM tasks WHERE task = ? AND user_id = ? AND date IN ({placeholders})'
        params = (task[0], chat_id) + tuple(data)
        self.cursor.execute(query, params)
        x = self.cursor.fetchone()
        return x[0]

    def get_week_tasks(self, chat_id):
        """Задачи на текущую неделю"""
        today = datetime.today().date()
        week = get_week_days_list()
        sunday = week[-1]
        self.cursor.execute(
            f'SELECT * FROM tasks WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 0',
            (str(today), (str(sunday)), chat_id)
        )
        return self.cursor.fetchall()

    def get_day_tasks(self, chat_id):
        """Задачи на текущий день"""
        if isinstance(chat_id, tuple):
            user = chat_id[0]
            user = str(user)
        else:
            user = str(chat_id)

        today = datetime.today().date()
        self.cursor.execute(
            f'SELECT * FROM tasks WHERE date = ? AND is_done = 0 AND user_id = ?', (str(today), user)
        )
        db_today_tasks = self.cursor.fetchall()
        today_tasks = []
        for i in db_today_tasks:
            today_tasks.append(i[1])

        return today_tasks

    def get_month_tasks(self, chat_id):
        """Задачи на текущий месяц"""
        today = datetime.today().date()
        month = str(today).split('-')
        last_day = calendar.monthrange(today.year, today.month)[1]
        month[2] = str(last_day)
        result = '-'.join(month)
        month_object = datetime.strptime(result, "%Y-%m-%d")
        self.cursor.execute(
            f'SELECT * FROM tasks WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 0',
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
        chek = self.cursor.execute(
            'SELECT task FROM tasks WHERE task = ? AND date = ? AND user_id = ?', (data[0], data[1], data[2]))
        if chek.fetchone():
            raise ValueError

        self.cursor.execute('INSERT INTO tasks (task, date, user_id, elapsed_time, is_done) VALUES (?,?,?,?,?)', data)
        self.conn.commit()
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
                self.conn.commit()
                bot.send_message(user_id, f'Задача {task} добавлена на день {days}')
            else:
                bot.send_message(user_id, 'Вы уже выбрали этот день')

        except KeyError:
            bot.send_message(user_id, 'Выберите день от сегодняшнего и позже')

            return self.conn.commit()

    def recurring_tasks_month(self, task, day, user_id):
        """Добавление повторяюзейся задачи на выбранный день недели"""
        month_days = days_until_end_of_month()
        try:
            task_in_day = self.cursor.execute('SELECT task, date FROM tasks WHERE task = ? AND date = ?', (task, day))
            result = task_in_day.fetchone()

            if day in month_days and not result:
                self.cursor.execute('INSERT INTO tasks (task, date, user_id, elapsed_time, is_done) VALUES (?,?,?,?,?)',
                                    (task, day, user_id, 0, 0))
                self.conn.commit()
                bot.send_message(user_id, f'Задача {task} добавлена на день {day}')
            else:
                bot.send_message(user_id, 'Вы уже выбрали этот день')

        except KeyError:
            bot.send_message(user_id, 'Выберите день от сегодняшнего и позже')

            return self.conn.commit()

    def get_task_editing(self, message, editing_task):
        """Выбираем задачу для редактирования"""
        today = datetime.today().date()
        week = get_week_days_list()
        sunday = week[-1]
        self.cursor.execute(
            f"""SELECT task, date FROM tasks WHERE task = ? AND user_id = ? AND date BETWEEN ? AND ?""",
            (editing_task, message.chat.id, str(today), str(sunday))
        )
        x = self.cursor.fetchall()
        return x

    def update_task(self, updated_text, editing_task, editing_date):
        self.cursor.execute(
            f'UPDATE tasks SET task = ?  WHERE task = ? AND date = ?', (updated_text, editing_task, editing_date)
        )

        return self.conn.commit()

    def close(self):
        """Закрытие соеденения с БД."""

        self.conn.close()

    def create_back_up(self, source_db_path, backup_folder):
        """Создает бэкап базы данных.
        source_db_path - Путь к исходной базе данных; backup_folder - Путь к папке с резервными копиями"""
        try:
            connection = sqlite3.connect('dairy_db.sql')
            connection.close()

            # Создаем копию файла базы данных в папке с резервными копиями
            today = datetime.today().date()
            backup_file_path = os.path.join(backup_folder, f'backup_database_{today}.db')
            shutil.copyfile(source_db_path, backup_file_path)
            bot.send_message(927883641, "Резервная копия создана успешно!")
        except Exception as e:
            bot.send_message(927883641, f'Сбой при создании резервной копии БД:\n {e}')

    def get_today_statistic(self, chat_id):
        today = datetime.today().date()
        self.cursor.execute(
            '''SELECT task, SUM(elapsed_time)
             FROM tasks
             WHERE date = ? AND user_id = ? AND is_done = 1
             GROUP BY task;''', (str(today), chat_id))

        s = self.cursor.fetchall()
        t = self.cursor.execute(
            '''SELECT task, SUM(elapsed_time)
             FROM tasks
             WHERE date = ? AND user_id = ? AND is_done = 1
             GROUP BY task;''', (str(today), chat_id))

        total_time = t.fetchone()

        s.append(str(total_time[1]))

        return s

    def get_task_statistic_week(self, chat_id):
        today = datetime.today().date()
        week = get_days_of_current_week()
        monday = week[0]
        self.cursor.execute(
            '''SELECT task, SUM(elapsed_time) AS total_elapsed_time
             FROM tasks
             WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 1
             GROUP BY task;''', (str(monday), (str(today)), chat_id)
        )
        s = self.cursor.fetchall()
        return s

    def get_task_statistic_month(self, chat_id):
        """Возвращает выборку задачи и затраченное на нее время от 1 дня месяца до сегодня"""
        today = datetime.today().date().strftime('%Y-%m-%d')
        current_month_days = get_days_until_today()
        first_month_day = current_month_days[0]
        self.cursor.execute(
            '''SELECT task, SUM(elapsed_time) AS total_elapsed_time
             FROM tasks
             WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 1
             GROUP BY task;''',
            (str(first_month_day), (str(today)), chat_id)
        )
        s = self.cursor.fetchall()
        return s

    def get_task_statistic_period(self, chat_id, start_period_date, end_period_date):
        self.cursor.execute(
            '''SELECT task, SUM(elapsed_time) AS total_elapsed_time
             FROM tasks
             WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 1
             GROUP BY task;''',
            (str(start_period_date), (str(end_period_date)), chat_id))
        s = self.cursor.fetchall()

        t = self.cursor.execute(
            '''SELECT SUM(elapsed_time)
             FROM tasks
             WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 1
             GROUP BY task;''', (str(start_period_date), str(end_period_date), chat_id))
        total_time_list = t.fetchall()
        summ = sum(value[0] for value in total_time_list)
        s.append(summ)
        return s

    def get_user_statistic_week(self, chat_id):
        today = datetime.today().date()
        week = get_days_of_current_week()
        monday = week[0]

        t = self.cursor.execute(
            '''SELECT SUM(elapsed_time)
             FROM tasks
             WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 1
             GROUP BY task;''', (str(monday), str(today), chat_id))
        total_time = t.fetchall()
        summ = sum(value[0] for value in total_time)
        return summ

    def get_user_statistic_month(self, chat_id):
        today = datetime.today().date().strftime('%Y-%m-%d')
        current_month_days = get_days_until_today()
        first_month_day = current_month_days[0]

        t = self.cursor.execute(
            '''SELECT task, SUM(elapsed_time) AS total_elapsed_time
             FROM tasks
             WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 1
             GROUP BY task;''', (str(first_month_day), (str(today)), chat_id)
        )

        total_time = t.fetchall()

        summ = sum(value[0] for value in total_time)
        return summ





