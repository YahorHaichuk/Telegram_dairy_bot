import sys
from telebot import types

from auxiliary_functions import get_week_days_list
from config import TOKEN
from database import BotDb
import telebot


bot = telebot.TeleBot(TOKEN)


def start(message):
    db = BotDb('dairy_db.sql')
    db.start(message.chat.id)

    bot.send_message(message.chat.id, 'Напишите задачу')


def task(message):
    bot.send_message(message.chat.id, 'Напишите дату в формате:  2023-06-30')

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for i in get_week_days_list():
        buttons.append(types.KeyboardButton(i))
    markup.add(*buttons)
    bot.send_message(message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)


def task_date(message, task_text):
    db = BotDb('dairy_db.sql')
    try:
        db.task_date(task_text, message.text, message)
        markup = types.InlineKeyboardMarkup(row_width=2)
        button_week = types.InlineKeyboardButton('Неделя', callback_data=f'{task_text} week')
        button_month = types.InlineKeyboardButton('Месяц', callback_data=f'{task_text} month')
        no_repeatable = types.InlineKeyboardButton('Без повторения', callback_data='only_one')
        markup.add(button_week, button_month, no_repeatable)
        bot.send_message(message.chat.id, 'добавлено')
        bot.send_message(message.chat.id, 'Выберите период повторения:', reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, 'Запись уже существует')


def get_user_week_tasks(message):
    db = BotDb('dairy_db.sql')
    week_tasks = db.get_week_tasks(message.chat.id)
    db.close()
    bot.send_message(message.chat.id, 'на этой неделе вам нужно сделать следующик задачи:')
    for el in week_tasks:
        bot.send_message(message.chat.id, f'{el[1]}')
        bot.send_message(message.chat.id, f'дата выполнения этой задачи {el[2]}')


def get_task_delete(message):
    bot.send_message(message.chat.id, 'Ведите задачу для удаления')

    bot.register_next_step_handler(message, task_delete)


def task_delete(message):
    db = BotDb('dairy_db.sql')
    deleting_task_text = message.text
    result = db.get_task_editing(message, deleting_task_text)
    buttons = []
    markup = types.InlineKeyboardMarkup()
    db.close()
    if len(result) == 0:
        bot.send_message(message.chat.id, 'Такой задачи не найдено проверте правильность написания')

    for i in result:
        buttons.append(types.InlineKeyboardButton(f'{i[1]}', callback_data=f' *task_delete* {i[0]} * {i[1]}'))

    markup.add(*buttons)
    text = f'''задача для удаления {result[0][0]} обнаруженв ы следушмщих днях на ближайжую неделю
            пожалуйста выберите день в который вы хотите удалить данную задачу'''
    if result is not None:
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Выборка пуста')


def get_editing_task_db(message):
    buttons = []
    db = BotDb('dairy_db.sql')
    task = message.text.strip()
    result = db.get_task_editing(message, task)

    markup = types.InlineKeyboardMarkup()

    db.close()
    if len(result) == 0:
        bot.send_message(message.chat.id, 'Такой задачи не найдено проверте правильность написания')
        sys.exit()

    for i in result:
        buttons.append(types.InlineKeyboardButton(f'{i[1]}', callback_data=f' *task_edit* {i[0]} * {i[1]}'))

    markup.add(*buttons)
    if result is not None and len(result) > 0:
        text = f'''Редактируемая задача {result[0][0]} обнаруженв ы следушмщих днях на ближайжую неделю
                пожалуйста выберите день в который вы хотите редактировать данную задачу'''
        bot.send_message(message.chat.id, text, reply_markup=markup)
    elif message.text == '/today_tasks':
        get_day_tasks(message)
    elif message.text == '/week':
        get_user_week_tasks(message)

    elif message.text == '/month':
        get_month_tasks(message)
    else:
        bot.send_message(message.chat.id, 'Выборка пуста')


def get_day_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_day_tasks(message.chat.id)
    db.close()
    bot.send_message(message.chat.id, 'Сеодня вам нужно сделать следующик задачи')
    for el in day_tasks:
        bot.send_message(message.chat.id, f'{el[0]}')


def get_month_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_month_tasks(message.chat.id)
    db.close()
    for el in day_tasks:
        bot.send_message(message.chat.id, f'{el[1]}')
        bot.send_message(message.chat.id, f'дата выполнения этой задачи {el[2]}')

def get_today_tasks_statistic(message):
    """копия метода из класса для русного вызова"""
    db = BotDb('dairy_db.sql')
    today = db.get_today_statistic(message.chat.id)
    db.close()
    today_total_time = today[-1]
    today.pop()

    bot.send_message(message.chat.id, 'Вот важи результаты на текуший месяц')

    for i in today:
        task = i[0]
        time = i[1]
        bot.send_message(message.chat.id, f"На задачу: {task} вы потратили {time} минут")

    bot.send_message(message.chat.id, f' сегодня вы продуктивно провели {today_total_time} минут')


def get_week_tasks_statistic(message):
    db = BotDb('dairy_db.sql')
    week_stat = db.get_task_statistic_week(message.chat.id)
    db.close()
    bot.send_message(message.chat.id, 'Вот важи результаты на текушую неделю')
    for i in week_stat:
        task = i[0]
        time = i[1]
        bot.send_message(message.chat.id, f"На задачу: {task} вы потратили {time} минут")


def get_month_statistic(message):
    db = BotDb('dairy_db.sql')
    month_stat = db.get_task_statistic_month(message.chat.id)
    db.close()
    bot.send_message(message.chat.id, 'Вот важи результаты на текуший месяц')
    for i in month_stat:
        task = i[0]
        time = i[1]
        bot.send_message(message.chat.id, f"На задачу: {task} вы потратили {time} минут")


def done_today_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_day_tasks(message.chat.id)
    db.close()

    buttons = []

    markup = types.InlineKeyboardMarkup()

    for i in day_tasks:
        data = '' + i[0] + '&' + i[1]
        buttons.append(types.InlineKeyboardButton(text=i[0][:12], callback_data=data))

    markup.add(*buttons)
    if len(buttons) == 0:
        bot.send_message(message.chat.id, 'На сегодня у вас нет задач')
    else:
        bot.send_message(message.chat.id, 'нажмите на выполненную задачу', reply_markup=markup)
