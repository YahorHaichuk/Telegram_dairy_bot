import time
from threading import Thread
from datetime import datetime
import telebot
from telebot import types

from database import BotDb
TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)


class CurrentHour(Thread):

    def run(self):
        timer = datetime.now()
        hour = timer.hour
        while True:
            if hour == 8:
                send_message = AutoSendMessage()
                send_message.morning_send()
                time.sleep(3600)
                continue

            elif hour == 14:
                send_message = AutoSendMessage()
                send_message.noon_send()
                time.sleep(3600)
                continue

            elif hour == 18:
                send_message = AutoSendMessage()
                send_message.evening_send()
                time.sleep(3600)
                continue

            elif hour == 14:
                send_message = AutoSendMessage()
                send_message.day_end()
                time.sleep(3600)
                continue
            elif hour == 23:
                source_db_path ='D:\DEVELOP\cats_dairy\dairy_db.sql'   #Путь к исходной базе данных
                backup_folder = 'D:\DEVELOP\cats_dairy\db_backup'  #Путь к папке с резервными копиями
                backup = BotDb('dairy_db.sql')
                backup.create_back_up(source_db_path=source_db_path, backup_folder=backup_folder)


class AutoSendMessage:
    def __init__(self):
        self.db = BotDb('dairy_db.sql')

    def send_today_tasks_in_text(self, text):
        """Отправляет пользователю список заданий в виде тексровых сообщений."""
        users = self.db.get_all_users()

        for user in users:
            bot.send_message(user[0], text)
            day_tasks = self.db.get_day_tasks(user)

            for el in day_tasks:
                bot.send_message(user[0], f'{el}')
        self.db.close()

    def send_today_tasks_in_buttons(self, text):
        """Отправляет пользователю список задач на сегодня в виде кнопок"""
        users = self.db.get_all_users()

        for user in users:
            markup = types.InlineKeyboardMarkup()
            day_tasks = self.db.get_day_tasks(user)
            buttons = []
            for i in day_tasks:
                buttons.append(types.InlineKeyboardButton(text=i, callback_data=i))
            markup.add(*buttons)
            if len(buttons) == 0:
                bot.send_message(user[0], "У вас нет задач на сегодня")
            else:
                bot.send_message(user[0], text, reply_markup=markup)
                buttons.clear()

        self.db.close()

    def morning_send(self):
        text = 'Доброе утро вот ваш список заданий на сегодня'
        self.send_today_tasks_in_text(text)

    def noon_send(self):
        text = 'Уже полдень, вот ваши задачи на сегодня, что то выполнил?'
        self.send_today_tasks_in_buttons(text)

    def evening_send(self):
        text = 'День подходит к концу, выполнил еще что нибудь? если нет надо поднажать!'
        self.send_today_tasks_in_buttons(text)

    def day_end(self):
        text = 'Наступил вечер, саоме время подвести итоги дня'
        self.send_today_tasks_in_buttons(text)
