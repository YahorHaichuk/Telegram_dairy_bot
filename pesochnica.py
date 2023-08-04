import datetime
import time
import threading
from threading import Thread
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'

bot = telebot.TeleBot(TOKEN)
locker = threading.RLock()

@bot.message_handler(commands=['start'])
def start(message):
    # Создаем основное меню
    markup = InlineKeyboardMarkup(row_width=2)
    button_week = InlineKeyboardButton('Неделя', callback_data='week')
    button_month = InlineKeyboardButton('Месяц', callback_data='month')
    markup.add(button_week, button_month)

    # Отправляем меню пользователю
    bot.send_message(message.chat.id, 'Выберите период повторения:', reply_markup=markup)

# Обработчик нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'week':
        # Если выбрана кнопка "Неделя", создаем подменю для выбора дней недели
        markup = InlineKeyboardMarkup(row_width=3)
        days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
        buttons = [InlineKeyboardButton(day, callback_data=day) for day in days]
        markup.add(*buttons)

        # Редактируем сообщение с кнопками, чтобы заменить основное меню на подменю
        bot.edit_message_text('Выберите день недели:', call.message.chat.id, call.message.message_id, reply_markup=markup)
    elif call.data == 'month':
        # Если выбрана кнопка "Месяц", делаем какие-то действия или отправляем другое меню
        # Например:
        bot.send_message(call.message.chat.id, 'Вы выбрали "Месяц"')
    else:
        # Обработка выбора дня недели или других кнопок, которые вы добавите
        bot.send_message(call.message.chat.id, f'Вы выбрали день: {call.data}')

# Запускаем бота
bot.polling()
