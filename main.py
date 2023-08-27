import datetime
import sys


from auxiliary_functions import duration_in_minutes, get_all_days_of_current_month
from bot_handlers import *
from database import BotDb
import telebot

from messages_sender import CurrentHour
from auxiliary_functions import days_until_end_of_month_list

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)

days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
recurring_this_week = []


@bot.message_handler(commands=['week'])
def week_tasks_handler(message):
    get_user_week_tasks(message)


@bot.message_handler(commands=['backup'])
#рУЧНОЙ ВЫЗОВ бжкапа бд
def create_back_up(message):
    source_db_path = 'D:\DEVELOP\cats_dairy\dairy_db.sql'  # Путь к исходной базе данных
    backup_folder = 'D:\DEVELOP\cats_dairy\db_backup'  # Путь к папке с резервными копиями
    backup = BotDb('dairy_db.sql')
    backup.create_back_up(source_db_path=source_db_path, backup_folder=backup_folder)



def get_day_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_day_tasks(message.chat.id)
    db.close()
    bot.send_message(message.chat.id, 'Сеодня вам нужно сделать следующик задачи')
    for el in day_tasks:
        bot.send_message(message.chat.id, f'{el}')


@bot.message_handler(commands=['month'])
def get_month_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.get_month_tasks(message.chat.id)
    db.close()
    for el in day_tasks:
        bot.send_message(message.chat.id, f'{el[1]}')
        bot.send_message(message.chat.id, f'дата выполнения этой задачи {el[2]}')


def cycle_month(call):
    days_list = days_until_end_of_month_list()
    current_task = call.data.split('*')[1:2][0]

    markup = types.InlineKeyboardMarkup(row_width=5)
    buttons = [types.InlineKeyboardButton(day, callback_data=f'{current_task} * {day} * month_daily') for day in days_list]
    markup.add(*buttons)
    text = '''Выберите дни недели в которые будет повторятся ваша задача от сегодняшнего дня и до конца месяца.\n
               Вы находитесь в режиме выбора дней повтора задач на текущий месяц.\n
               '''
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


@bot.message_handler(commands=['task_delete'])
def get_task_delete_handler(message):
    get_task_delete(message)

    bot.register_next_step_handler(message, task_delete_handler)


def task_delete_handler(message):
    task_delete(message)


@bot.message_handler(commands=['task_edit'])
def get_editing_task_text_handler(message):
    bot.send_message(message.chat.id, 'Ведите задачу для редактирования')

    bot.register_next_step_handler(message, get_editing_task_db)


def get_editing_task_db_handler(message):
    get_editing_task_db(message)


def update_info_handler(message, editing_task, editing_date):
    data = [editing_task, editing_date]
    bot.send_message(message.chat.id, f'Привет! Введите текст:')

    bot.register_next_step_handler(message, update_task_handler, data=data)


def update_task_handler(message, data):
    db = BotDb('dairy_db.sql')
    db.update_task(message.text, data[0], data[1])
    bot.send_message(message.chat.id, 'Задача изменена')


@bot.message_handler(commands=['start'])
def start_handler(message):
    start(message)
    bot.register_next_step_handler(message, task_handler)


def task_handler(message):
    task(message)
    task_text = f'*{message.text}*'
    bot.register_next_step_handler(message, task_date, task_text=task_text)


def task_date_handler(message):
    task_date(message, task_date)


@bot.message_handler(commands=['today_statistic'])
def get_today_tasks_statistic_handler(message):
    """копия метода из класса для русного вызова"""
    get_today_tasks_statistic(message)


@bot.message_handler(commands=['period_statistic'])
def get_start_point_period_statistic(message):
    bot.send_message(message.chat.id, f'Введите дату начала отрезка статистики в формате "2023-01-01"')

    month = get_all_days_of_current_month()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*month)
    bot.send_message(message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)
    bot.register_next_step_handler(message, get_end_point_period_statistic)


def get_end_point_period_statistic(message):
    bot.send_message(message.chat.id, f'Введите дату конца отрезка статистики в формате "2023-01-01"')
    month = get_all_days_of_current_month()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*month)
    bot.send_message(message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)
    start_point = message.text
    bot.register_next_step_handler(message, get_period_tasks_statistic, start_point=start_point)


def get_period_tasks_statistic(message, start_point):
    """копия метода из класса для русного вызова"""
    db = BotDb('dairy_db.sql')
    end_point = message.text
    period = db.get_task_statistic_period(message.chat.id, start_point, end_point)

    period_total_time = period[-1]
    period.pop()

    bot.send_message(message.chat.id, 'Вот важи результаты на текуший месяц')

    for i in period:
        task = i[0]
        time = i[1]
        bot.send_message(message.chat.id, f"На задачу: {task} вы потратили {time} минут")

    bot.send_message(message.chat.id, f'''В период от {start_point} до {end_point}
    вы продуктивно провели {period_total_time} минут''')


@bot.message_handler(commands=['week_statistic'])
def get_week_tasks_statistic_handler(message):
    get_week_tasks_statistic(message)


@bot.message_handler(commands=['month_statistic'])
def get_month_statistic_handler(message):
    get_month_statistic(message)


@bot.message_handler(commands=['month_total_time'])
def get_total_time_statistic_month(message):
    db = BotDb('dairy_db.sql')
    month_total_time = db.get_user_statistic_month(message.chat.id)
    bot.send_message(message.chat.id, f'В этом месяце вы продуктивно провели {month_total_time} минут')


@bot.message_handler(commands=['week_total_time'])
def get_total_time_statistic_week(message):
    db = BotDb('dairy_db.sql')
    month_total_time = db.get_user_statistic_week(message.chat.id)
    bot.send_message(message.chat.id, f'На этой неделе вы продуктивно провели {month_total_time} минут')


@bot.message_handler(commands=['done_today_tasks'])
def done_today_tasks_handler(message):
    done_today_tasks(message)


def add_start_time(message, task_time_add):
    start_time = message.text

    bot.send_message(message.chat.id, f'Ведите время в которое вы закончили выполнять задачу\n{task_time_add} в формате "ЧЧ:ММ"')
    hours = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
             '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', ]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*hours)
    bot.send_message(message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)

    bot.register_next_step_handler(message, add_end_time, task_time_add=task_time_add, start_time=start_time)


def add_end_time(message, task_time_add, start_time):
    db = BotDb('dairy_db.sql')
    end_time = message.text
    try:
        minutes = duration_in_minutes(start_time, end_time)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное время. Время должно быть больше 0.")
        sys.exit()
    db.spent_time_task_add(task_time_add, minutes)

    db.close()

    bot.send_message(message.chat.id,
                     f'на задачу {task_time_add} вы потратили {minutes} минут.\nрезультат сохранен.')


def month_cycle_add(call):
    db = BotDb('dairy_db.sql')
    current_year = str(datetime.datetime.now().year) + '-'
    day = call.data.split('*')[1][4:]
    current_date = current_year + day
    task = call.data.split('*')[0].strip()

    db.recurring_tasks_month(task, current_date.strip(), call.message.chat.id)


@bot.callback_query_handler(
    func=lambda call: (call.data is not None and BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id) is not None
                       and call.data in BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id))
)
def done_today_callback(call):
    """Обработчик колбэка на выполнение сегодняшней задачи."""
    task_time_add = call.data[:]
    bot.send_message(call.message.chat.id,
                     f''' Ведите время в которое вы начали выполнять задачу {call.data[:]}\nв формате "ЧЧ:ММ"''')

    hours = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
             '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', ]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*hours)
    bot.send_message(call.message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)

    bot.register_next_step_handler(call.message, add_start_time, task_time_add=task_time_add)


def callback_recurring_tasks_many_words_handler(call):
    """Обработка повторяющихя задач периодом в 1 неделю."""
    current_task = call.data.split('*')[1:2][0]

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(day, callback_data=f'{current_task} * {day}') for day in days]
    markup.add(*buttons)
    text = '''Выберите дни недели в которые будет повторятся ваша задача от сегодняшнего дня и до конца недели.\n
            Вы находитесь в режиме выбора дней повтора задач на текущую неделю.\n
            Что бы добавить повторяющмеся задачи на следующую неделю сделайте это в понедельник,
            или добавте задачу в ручную с помошью команды /start\n
            Либо выберите период повторения месяц'''
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


def recurring_tasks_week(call):
    db = BotDb('dairy_db.sql')
    day = call.data.split('*')[1].replace(" ", "")

    task = call.data.split('*')[0].strip()

    db.recurring_tasks_week(task, day, call.message.chat.id)


@bot.callback_query_handler(func=lambda call: True)
def all_callbacks_handler(call):
    db = BotDb('dairy_db.sql')
    task_text_range_week = None
    task_text_range_month = None
    today_tasks = BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id)
    try:
        if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'week':
            task_text_range_week = (BotDb('dairy_db.sql').get_task_range_week(call.data.split('*')[1].strip(), call.message.chat.id))
    except TypeError:
        task_text_range_week = None

    try: #Нажатие кнопки "месяц"
        if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'month':
            task_text_range_month = (
                BotDb('dairy_db.sql').get_task_range_month(call.data.split('*')[1].strip(), call.message.chat.id))
    except TypeError:
        task_text_range_month = None

    try: #Нажатие кнопки "день месяца"
        if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'month_daily':
            task_text_range_month = (
                BotDb('dairy_db.sql').get_task_range_month(call.data.split('*')[0].strip(), call.message.chat.id))
    except TypeError:
        task_text_range_month = None

    if (
            call.data is not None and today_tasks is not None and call.data in today_tasks):  # выполнение сегодняшней задачи
        done_today_callback(call)
    if len(call.data.split('*')) == 3:
        if (task_text_range_week is not None
                and call.data.split('*')[1] == task_text_range_week
                and call.data.split('*')[2].strip() == 'week'):
            callback_recurring_tasks_many_words_handler(call)  # период повторения неделя
    if len(call.data.split('*')) == 3:
        if (task_text_range_month is not None and
                call.data.split('*')[1].strip() == task_text_range_month and call.data.split('*')[
                    2].strip() == 'month'):
            cycle_month(call)  # период повторения месяц

    if len(call.data.split('*')) > 1 and call.data.split('*')[1].strip() in days:
        if (BotDb('dairy_db.sql').get_task_range_week(#вызвывает функцию записи повторных задач на неделю
                call.data.split('*')[0].strip(), call.message.chat.id)) and (
                call.data.split('*')[1].strip() in days):
            recurring_tasks_week(call)

    if call.data == 'only_one':# добавляет задачу без довторения
        bot.send_message(call.message.chat.id, 'Задача добавлена')
    # вызвывает функцию записи повторных задач на месяц
    if len(call.data.split('*')) == 3:
        if (task_text_range_month is not None and
                call.data.split('*')[0].strip() == task_text_range_month and call.data.split('*')[
                    2].strip() == 'month_daily'):
            month_cycle_add(call)

    # вызывет функцию редактирования задачи
    if len(call.data.split('*')) >= 3 and call.data.split('*')[1:][0] == 'task_edit':
        if ((call.data.split('*')[1:][1].strip(), call.data.split('*')[1:][2].strip())
                in BotDb('dairy_db.sql').get_task_editing(call.message, call.data.split('*')[1:][1].strip())):
            editing_task = call.data.split('*')[1:][1].strip()
            editing_date = call.data.split('*')[1:][2].strip()
            update_info_handler(call.message, editing_task, editing_date)

    if len(call.data.split('*')) >= 3 and call.data.split('*')[1:][0] == 'task_delete':
        if ((call.data.split('*')[1:][1].strip(), call.data.split('*')[1:][2].strip())
                in BotDb('dairy_db.sql').get_task_editing(call.message, call.data.split('*')[1:][1].strip())):
            deleting_task = call.data.split('*')[1:][1].strip()
            deleting_task_date = call.data.split('*')[1:][2].strip()
            db.delete(deleting_task, deleting_task_date)
            bot.send_message(call.message.chat.id, f''' задача {deleting_task} в день {deleting_task_date} удалена
''')


def send_time():

    hours = CurrentHour()
    hours.start()


#send_time()


if __name__ == "__main__":
    bot.polling(none_stop=True)
