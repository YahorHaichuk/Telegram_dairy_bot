import datetime
import sys
import time

import requests
from telebot import types

from auxiliary_functions import duration_in_minutes, get_week_days_list, days_until_end_of_month, \
    get_all_days_of_current_month
from bot_handlers import Handlers
from database import BotDb
import telebot

from messages_sender import AutoSendMessage, CurrentHour
from auxiliary_functions import days_until_end_of_month_list

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)

days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
recurring_this_week = []


class Example(Handlers):
    def __init__(self, message):
        self.bot = telebot.TeleBot(TOKEN)

    def first_foo(self, message, editing_task, editing_date):
        data = [editing_task, editing_date]
        self.bot.send_message(message.chat.id, f'Привет! Введите текст:')

        self.bot.register_next_step_handler(message, self.second_foo, data=data)

    def second_foo(self, message, data):
        db = BotDb('dairy_db.sql')
        db.update_task(message.text, data[0], data[1])
        self.bot.send_message(message.chat.id, 'Задача изменена')