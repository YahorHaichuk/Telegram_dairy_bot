import time
from datetime import datetime

import telebot
from telebot import types

from config import TOKEN
from database import BotDb

bot = telebot.TeleBot(TOKEN)

timer = datetime.now()
hour = timer.hour

class AutoSendMessage:
    def __init__(self):
        self.db = BotDb('dairy_db.sql')

    def send_today_tasks_in_text(self, text):
        """Sends the user a list of tasks in the form of text messages."""
        users = self.db.get_all_users()

        for user in users:
            bot.send_message(user[0], text)
            day_tasks = self.db.get_day_tasks(user)

            for el in day_tasks:
                bot.send_message(user[0], f'{el}')
        self.db.close()

    def send_today_tasks_in_buttons(self, text):
        """Sends the user a list of tasks for today in the form of buttons."""
        users = self.db.get_all_users()

        for user in users:
            markup = types.InlineKeyboardMarkup()
            day_tasks = self.db.get_day_tasks(user)
            buttons = []
            for i in day_tasks:
                data = '' + i[0] + '&' + i[1]
                buttons.append(types.InlineKeyboardButton(text=i[0], callback_data=data))
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
        text = f'Уже {hour} часов! Поднажмем если остались неоконченные задачи!'
        self.send_today_tasks_in_buttons(text)

    def day_end(self):
        text = 'Наступил вечер, саоме время подвести итоги дня'
        self.send_today_tasks_in_buttons(text)

def run():
    timer = datetime.now()
    hour = timer.hour
    if hour == 6:
        send_message = AutoSendMessage()
        send_message.morning_send()

    if hour == 10:
        send_message = AutoSendMessage()
        send_message.noon_send()

    if hour == 16:
        send_message = AutoSendMessage()
        send_message.evening_send()

    if hour == 19:
        send_message = AutoSendMessage()
        send_message.day_end()

    if hour == 21:
        source_db_path ='/app/dairy_db.sql'   #Путь к исходной базе данных
        backup_folder = '/app/db_backup'  #Путь к папке с резервными копиями
        backup = BotDb('dairy_db.sql')
        backup.create_back_up(source_db_path=source_db_path, backup_folder=backup_folder)

    else:
        pass


if __name__ == '__main__':
    run()

bot.send_message(927883641,
                             f'Сенд меседжер работает')
