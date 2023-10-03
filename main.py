import datetime

from auxiliary_functions import duration_in_minutes, get_all_days_of_current_month
from bot_handlers import *
from database import BotDb
import telebot

from messages_sender import CurrentHour
from auxiliary_functions import days_until_end_of_month_list
from config import TOKEN

bot = telebot.TeleBot(TOKEN)

days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']


@bot.message_handler(commands=['create_db'])
def create_db(message):
    db = BotDb('dairy_db.sql')
    db.create_db(message.chat.id)


@bot.message_handler(commands=['copy_db'])
def copy_db(message):
    copy_db_from_container_to_host()

@bot.message_handler(commands=['week'])
def week_tasks_handler(message):
    get_user_week_tasks(message)


@bot.message_handler(commands=['backup'])
#MANUAL CALL DB backup
def create_back_up(message):
    source_db_path = '/app/dairy_db.sql'  # Path to source database
    backup_folder = '/app/db_backup'  # Path to the backup folder
    backup = BotDb('dairy_db.sql')
    backup.create_back_up(source_db_path=source_db_path, backup_folder=backup_folder)


@bot.message_handler(commands=['today_tasks'])
def get_day_tasks_handler(message):
    get_day_tasks(message)


@bot.message_handler(commands=['month'])
def get_month_tasks_handler(message):
    get_month_tasks(message)


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
    text = """Ведите задачу для редактирования
    Чтобы получить список задач на сегодня нажмите /today_tasks\n
    Чтобы получить список задач на неделю нажмите /week\n
    Чтобы получить список задач на месяц нажмите /month\n
    После того как вам придет список задание еще раз нажмите на /task_edit"""
    bot.send_message(message.chat.id, text)

    bot.register_next_step_handler(message, get_editing_task_db)


def get_editing_task_db_handler(message):
    get_editing_task_db(message)


def update_info_handler(message, editing_task, editing_date):
    data = [editing_task, editing_date]
    bot.send_message(message.chat.id, f'Введите отредактированный текст:')

    bot.register_next_step_handler(message, update_task_handler, data=data)


def update_task_handler(message, data):
    db = BotDb('dairy_db.sql')
    db.update_task(message.text, data[0], data[1])
    bot.send_message(message.chat.id, 'Задача изменена')


@bot.message_handler(commands=['task_add'])
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


def add_start_time(message, task_time_add, date_data):
    start_time = message.text

    bot.send_message(message.chat.id, f'Ведите время в которое вы закончили выполнять задачу\n{task_time_add} в формате "ЧЧ:ММ"')
    hours = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
             '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', ]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*hours)
    bot.send_message(message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)

    bot.register_next_step_handler(
        message, add_end_time, task_time_add=task_time_add, start_time=start_time, date_data=date_data)


def add_end_time(message, task_time_add, start_time, date_data):
    db = BotDb('dairy_db.sql')
    end_time = message.text
    try:
        minutes = duration_in_minutes(start_time, end_time)
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное время. Время должно быть больше 0.")
        sys.exit()
    db.spent_time_task_add(task_time_add, date_data, minutes)

    db.close()

    bot.send_message(message.chat.id,
                     f'на задачу {task_time_add} вы потратили {minutes} минут.\nрезультат сохранен.')


@bot.message_handler(commands=['delete_all_info'])
def delete_all_tasks_by_user_id(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton('Я хочу удалить все данные', callback_data=f'DELETE_ALL_YES*{message.chat.id}'),
        types.InlineKeyboardButton('Я передумал удалять все данные', callback_data=f'DELETE_ALL_NO*{message.chat.id}')
    ]
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'АСТАНАВИТЕСЬ!', reply_markup=markup)


def confirmation_delete_all_tasks_by_user_id(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [
        types.InlineKeyboardButton('Я хочу точно удалить ВСЁ',
                                   callback_data=f'EXACTLY_DELETE_ALL_YES*{message.chat.id}'),
        types.InlineKeyboardButton('Я передумал удалять все данные', callback_data=f'DELETE_ALL_NO*{message.chat.id}')
    ]
    markup.add(*buttons)
    bot.edit_message_text('АСТАНАВИТЕСЬ!', message.chat.id, message.message_id, reply_markup=markup)


def month_cycle_add(call):
    db = BotDb('dairy_db.sql')
    current_year = str(datetime.now().year) + '-'
    current_month = str(datetime.now().month) + '-'
    day = call.data.split('*')[1][4:]
    current_date = current_year + current_month + day
    task = call.data.split('*')[0].strip()

    db.recurring_tasks_month(task, current_date.strip(), call.message.chat.id)


@bot.callback_query_handler(
    func=lambda call: (call.data is not None and BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id) is not None
                       and call.data in BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id))
)
def done_today_callback(call):
    """Обработчик колбэка на выполнение сегодняшней задачи."""
    task_time_add = call.data.split("&")[0]
    date_data = call.data.split("&")[1]
    bot.send_message(call.message.chat.id,
                     f''' Ведите время в которое вы начали выполнять задачу {task_time_add}\nв формате "ЧЧ:ММ"''')

    hours = ['06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00',
             '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00', ]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*hours)
    bot.send_message(call.message.chat.id, "Вы можете вписать дату или выбрать кнопкой", reply_markup=markup)

    bot.register_next_step_handler(call.message, add_start_time, task_time_add=task_time_add, date_data=date_data)


def callback_recurring_tasks_week_handler(call):
    """Обработка повторяющихя задач периодом в 1 неделю."""
    current_task = call.data.split('*')[1:2][0]

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(day, callback_data=f'{current_task} * {day}') for day in days]
    next_week_button = types.InlineKeyboardButton('Следующая неделя', callback_data=f'{current_task} *next_week_recurring')
    buttons.append(next_week_button)
    markup.add(*buttons)

    text = '''Выберите дни недели в которые будет повторятся ваша задача от сегодняшнего дня и до конца недели.\n
            Вы находитесь в режиме выбора дней повтора задач на текущую неделю.'''
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


def callback_recurring_tasks_next_week_handler(call):
    """Обработка повторяющихя задач периодом в 1 неделю."""
    current_task = call.data.split('*')[0:1][0].strip()

    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(day, callback_data=f'{current_task} * {day} *next') for day in days]
    markup.add(*buttons)

    text = '''Выберите дни недели в которые будет повторятся ваша задача от понедельника и до конца недели.\n
            Вы находитесь в режиме выбора дней повтора задач на следующую неделю.'''
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)


def recurring_tasks_week(call):
    db = BotDb('dairy_db.sql')
    day = call.data.split('*')[1].replace(" ", "")

    task = call.data.split('*')[0].strip()

    db.recurring_tasks_week(task, day, call.message.chat.id)


def recurring_tasks_next_week(call):
    db = BotDb('dairy_db.sql')
    day = call.data.split('*')[1].replace(" ", "")

    task = call.data.split('*')[0].strip()

    db.recurring_tasks_next_week(task, day, call.message.chat.id)



@bot.callback_query_handler(func=lambda call: True)
def all_callbacks_handler(call):
    x =  call.data.split('*')
    db = BotDb('dairy_db.sql')
    task_text_range_week = None
    task_text_range_month = None
    get_today_tasks = db.get_day_tasks(call.message.chat.id)
    today_tasks = tuple(i for i, x in get_today_tasks)
    try:
        if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'week':
            task_text_range_week = (db.get_task_range_week(call.data.split('*')[1].strip(), call.message.chat.id))
    except TypeError:
        task_text_range_week = None

    try: #Pressing the "month" button
        if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'month':
            task_text_range_month = (
                BotDb('dairy_db.sql').get_task_range_month(call.data.split('*')[1].strip(), call.message.chat.id))
    except TypeError:
        task_text_range_month = None

    try: #Pressing the "day of the month" button
        if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'month_daily':
            task_text_range_month = (
                BotDb('dairy_db.sql').get_task_range_month(call.data.split('*')[0].strip(), call.message.chat.id))
    except TypeError:
        task_text_range_month = None

    if (
            call.data is not None and today_tasks is not None and call.data.split("&")[0] in today_tasks):  #complete today's task
            x = call.data
            done_today_callback(call)
    if len(call.data.split('*')) == 3:
        if (task_text_range_week is not None
                and call.data.split('*')[1] == task_text_range_week
                and call.data.split('*')[2].strip() == 'week'):
            callback_recurring_tasks_week_handler(call)  # repeat period week
    if len(call.data.split('*')) == 3:
        if (task_text_range_month is not None and
                call.data.split('*')[1].strip() == task_text_range_month and call.data.split('*')[
                    2].strip() == 'month'):
            cycle_month(call)  # repeat period month

    if 3 > len(call.data.split('*')) > 1 and call.data.split('*')[1].strip() in days: #calls the function to record repeated tasks for the week
        if (BotDb('dairy_db.sql').get_task_range_week(
                call.data.split('*')[0].strip(), call.message.chat.id)) and (
                call.data.split('*')[1].strip() in days):
            recurring_tasks_week(call)
    if len(call.data.split('*')) > 1 and call.data.split('*')[1].strip() == 'next_week_recurring':
        if (BotDb('dairy_db.sql').get_task_range_week(
                call.data.split('*')[0].strip(), call.message.chat.id)):
            callback_recurring_tasks_next_week_handler(call)
    if (len(call.data.split('*')) > 2 and call.data.split('*')[1].strip() in days and
    call.data.split('*')[2].strip() == 'next'): #calls the function to record repeated tasks for the week
        if (BotDb('dairy_db.sql').get_task_range_week(
                call.data.split('*')[0].strip(), call.message.chat.id)) and (
                call.data.split('*')[1].strip() in days):
            recurring_tasks_next_week(call)

    if call.data == 'only_one':#adds a task without repetition
        bot.send_message(call.message.chat.id, 'Задача добавлена')
    if len(call.data.split('*')) == 3: #calls the function of recording repeated tasks for a month
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
    if call.data.split('*')[0] == 'DELETE_ALL_YES':
        confirmation_delete_all_tasks_by_user_id(call.message)

    if call.data.split('*')[0] == 'EXACTLY_DELETE_ALL_YES':
        db.delete_tasks_by_user_id(call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Все данные о вас удалены')

    if call.data.split('*')[0] == 'DELETE_ALL_NO':
        bot.send_message(call.message.chat.id, 'Разумное решение')


@bot.message_handler(commands=['help'])
def help_handler(message):
    text = '''Привет, я Телеграм бот ежедневник,
с помощью меня ты можешь добавить задачи на сегодня,
на текущую неделю и на следующую неделю,
а так же на месяц
можно просматривать задачт на сегодня\неделю\месяц
можно редактировать и удалять добавленные задачи,
при выполнии задания ты можешь указать время которое затратили на данную задачу и я запомню его
позже ты можешь посмотреть статистику за день, месяц, неделю или выбранный тобой период 
и там будет указано сколько времени и на какие задачи ты потратил
при нажатии кнопки меню всплывет список доступных команд'''

    bot.send_message(message.chat.id, text)


def send_time():

    hours = CurrentHour()
    hours.start()


if __name__ == '__main__':

    bot.polling(none_stop=True)
