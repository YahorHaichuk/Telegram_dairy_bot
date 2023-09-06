import calendar
import sqlite3
import sys
from datetime import datetime

import shutil
import os
import docker
from config import TOKEN

import telebot


from auxiliary_functions import get_week_days_list, convert_to_datetime, get_week_days_dict, days_until_end_of_month, \
    get_days_until_today, get_days_of_current_week, get_next_week_days_dict

bot = telebot.TeleBot(TOKEN)

recurring_days_list = []
recurring_days_dict = {}


class BotDb:

    def __init__(self, db_name):
        """Initialize database connection."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_db(self, chat_id):
        """Creating a database. Table users and tasks"""

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
        """Selects a task from the user to check the condition for adding a repeat per week"""
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
        """Selects a task from the user to check the condition for adding a repeat per week"""
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
        """Tasks for the current week"""
        today = datetime.today().date()
        week = get_week_days_list()
        sunday = week[-1]
        self.cursor.execute(
            f'SELECT * FROM tasks WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 0',
            (str(today), (str(sunday)), chat_id)
        )
        x = self.cursor.fetchall()
        return x

    def get_day_tasks(self, chat_id):
        """Today's tasks"""
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
            x = (i[1], i[2])
            today_tasks.append(x)
        return today_tasks

    def get_month_tasks(self, chat_id):
        """Tasks for the current month"""
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
        x = self.cursor.fetchall()
        return x

    def start(self, chat_id):
        """Adding a task"""
        self.cursor.execute(f'SELECT user_id FROM users WHERE user_id = {chat_id}')
        user = self.cursor.fetchone()

        if user is None:
            self.cursor.execute('INSERT INTO users VALUES(?)', (chat_id,))
            bot.send_message(chat_id, 'Добро пожаловать в котячй ежедневник ваш id успешно добавлен в базу!')
        else:
            bot.send_message(chat_id, f'Добрый день, ваш чат id {chat_id}, желаю продуктивного дня!')
        return self.conn.commit()

    def task_date(self, text, date, message):
        """Adding a due date to the added task"""
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
        return self.conn.commit()

    def get_all_users(self):
        """Selecting all users to auto-send a message"""
        self.cursor.execute(f'SELECT user_id FROM users')
        users = self.cursor.fetchall()
        return users

    def spent_time_task_add(self, task, date, duration):
        """Adding elapsed time to a task when
            pressing the button to complete this task """
        self.cursor.execute(
            f'UPDATE tasks SET elapsed_time = ? WHERE task = ? AND date = ?', (duration, task, date)
        )
        self.cursor.execute(
            f'UPDATE tasks SET is_done = 1 WHERE task = ? AND date = ?', (task, date)
        )

        return self.conn.commit()

    def recurring_tasks_week(self, task, days, user_id):
        """Adding a recurring task for the selected day of the week"""
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

    def recurring_tasks_next_week(self, task, days, user_id):
        """Adding a recurring task for the selected day of the week"""
        week_days = get_next_week_days_dict()
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
        """Adding a recurring task for the selected day of the week"""
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

            self.conn.commit()

    def get_task_editing(self, message, editing_task):
        """Selecting a task to edit"""
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
        """Closing the database connection."""

        self.conn.close()

    def delete(self, task, date):
        self.cursor.execute('''DELETE FROM tasks WHERE task = ? AND date = ?''', (task, date))

        self.conn.commit()

    def create_back_up(self, source_db_path, backup_folder):
        """Creates a database backup.
        source_db_path - Path to source database; backup_folder - Path to folder with backups"""
        try:
            connection = sqlite3.connect('dairy_db.sql')
            connection.close()

            # Создаем копию файла базы данных в папке с резервными копиями
            today = datetime.today().date()
            backup_file_path = os.path.join(backup_folder, f'backup_database_{today}.sql')
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
        """Returns a selection of the task and the time spent on it from the 1st day of the month to today"""
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
            '''SELECT SUM(elapsed_time) AS total_elapsed_time
             FROM tasks
             WHERE date BETWEEN ? AND ? AND user_id = ? AND is_done = 1
             GROUP BY task;''', (str(first_month_day), (str(today)), chat_id)
        )

        total_time = t.fetchall()

        summ = sum(value[0] for value in total_time)
        return summ

    def find_container_id_by_name(self, container_name):
        try:
            # Создаем клиент Docker
            client = docker.from_env()
            # Получаем список контейнеров
            containers = client.containers.list()
            # Поиск контейнера по имени
            for container in containers:
                if container.name == container_name:
                    return container.id
            # Если контейнер не найден, возвращаем None
            return None

        except Exception as e:
            print(f"Ошибка: {e}")
            return None

    def delete_tasks_by_user_id(self, user_id):
        self.cursor.execute("DELETE FROM tasks WHERE user_id = ?", (user_id,))
        self.conn.commit()
    def copy_file_from_container(self, container_id, source_path, destination_path):
        try:
            # Создаем клиент Docker
            client = docker.from_env()
            # Копируем файл из контейнера во временный файл на хосте
            with open(destination_path, 'wb') as f:
                data, _ = client.containers.get(container_id).get_archive(source_path)
                for chunk in data:
                    f.write(chunk)
            # Закрываем клиент Docker
            client.close()
            # Возвращаем путь к скопированному файлу на хосте
            return destination_path

        except Exception as e:
            print(f"Ошибка: {e}")
            return None





