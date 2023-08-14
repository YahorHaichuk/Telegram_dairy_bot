import sys
from telebot import types

from database import BotDb, CurrentHour
import telebot

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)


class BotTG:
    def __init__(self):
        self.db = BotDb('dairy_db.sql')
        #self.message = message
        self.editing_task = None
        self.editing_date = None
        self.updated_task_text = None
        self.add_task_text = None
        self.add_task_date = None

    def get_week_tasks(self, message):
        """Отправка в чат пользователю задач на текущую неделю"""
        self.db = BotDb('dairy_db.sql')
        week_tasks = self.db.week_tasks(message.chat.id)
        self.db.close()
        for el in week_tasks:
            bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}\n')

    def get_day_tasks(self, message):
        """Отправка в чат пользователю задач на текущий день"""
        day_tasks = self.db.day_tasks(message.chat.id)
        self.db.close()
        for el in day_tasks:
            bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}\n')

    def get_month_tasks(self, message):
        """Отправка в чат пользователю задач на текущую неделю"""
        month_tasks = self.db.month_tasks(message.chat.id)
        self.db.close()
        for el in month_tasks:
            bot.send_message(message.chat.id, f'задачу  {el[1]} нужно сделать {el[2]}\n')

    def start(self, message):
        self.db.start(message.chat.id)

    def post_task_text(self, message):
        self.add_task_text = f'*{message.text}*'
        bot.send_message(message.chat.id, 'Напишите дату в формате:  2023-06-30')

    def post_task_date(self, message):
        BotDb('dairy_db.sql').task_date(self.add_task_text, message.text, message)

        markup = types.InlineKeyboardMarkup(row_width=2)
        button_week = types.InlineKeyboardButton('Неделя', callback_data=f'{self.add_task_text} week')
        button_month = types.InlineKeyboardButton('Месяц', callback_data='month')
        no_repeatable = types.InlineKeyboardButton('Без повторения', callback_data='only_one')
        markup.add(button_week, button_month, no_repeatable)

        bot.send_message(message.chat.id, 'Выберите период повторения:', reply_markup=markup)

    def get_editing_task_text(self, message):
        bot.send_message(message.chat.id, 'Ведите задачу для редактирования')

    def get_editing_task_db(self, message):
        buttons = []
        db = BotDb('dairy_db.sql')
        task = message.text.strip()
        result = db.get_task_editing(message, task)
        if len(result) == 0:
            bot.send_message(message.chat.id, 'Выборка пуста')
            sys.exit()

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

    def update_task(self, message, editing_task, editing_date):
        self.updated_task_text = message.text
        self.editing_task = editing_task
        self.editing_date = editing_date

        BotDb('dairy_db.sql').update_task(self.updated_task_text, editing_task, editing_date)

        bot.send_message(message.chat.id, 'Задача изменена')
