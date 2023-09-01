import calendar
import datetime
from datetime import timedelta
import telebot
from config import TOKEN


bot = telebot.TeleBot(TOKEN)
today = datetime.date.today()


def duration_in_minutes(start_time, end_time):

    start = datetime.datetime.strptime(start_time, '%H:%M')
    end = datetime.datetime.strptime(end_time, '%H:%M')
    time_difference = end - start

    minutes = time_difference.total_seconds() / 60
    return int(minutes)


def get_week_days_list():
    """Returns the remaining days of the week until the end of the week in date format."""
    current_weekday = today.weekday()
    days_until_next_monday = (7 - current_weekday) % 7
    if current_weekday == 0:
        days_until_next_monday = 7
    next_monday = today + timedelta(days=days_until_next_monday)

    time_range = []
    days = []
    current_datetime = today
    while current_datetime < next_monday:
        time_range.append(current_datetime)
        current_datetime += timedelta(days=1)

    formatted_list = [dt.strftime('%Y-%m-%d') for dt in time_range]

    for day in formatted_list:
        days.append(day)

    return days


def get_week_days_dict():
    """Returns the remaining days of the week until the end of the week in date format."""
    current_weekday = today.weekday()
    days_until_next_monday = (7 - current_weekday) % 7
    if current_weekday == 0:
        days_until_next_monday = 7
    next_monday = today + timedelta(days=days_until_next_monday)

    time_range = []
    days = []
    current_datetime = today
    while current_datetime < next_monday:
        time_range.append(current_datetime)
        current_datetime += timedelta(days=1)

    formatted_list = [dt.strftime('%Y-%m-%d') for dt in time_range]

    for day in formatted_list:
        days.append(day)

    days_str = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    merged_lists = list(zip(days_str[::-1], days[::-1]))
    days_dict = {}
    for key, value in merged_lists:
        days_dict[key] = value
    return days_dict


def convert_to_datetime(message, date):
    try:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        return date.date()
    except ValueError:
        error = 'Пожалуйста укажити дату так как это показано в примере, добавление задачи сброшено, начните сначала'
        bot.send_message(message.chat.id, error)
        #TODO закинуть эту фунцию с файл с добавочными и переделать добавление задачи


def days_until_end_of_month():
    """Get all the remaining days of the current month starting from today as a list"""
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    first_day_next_month = datetime.datetime(next_year, next_month, 1)
    last_day_of_month = first_day_next_month - timedelta(days=1)

    remaining_days = (last_day_of_month - today).days + 1
    days_list = [today + timedelta(days=i) for i in range(1, remaining_days + 1)]
    x = [today.strftime("%Y-%m-%d")]
    for d in days_list:
        x.append(d.strftime("%Y-%m-%d"))

    return x


def days_until_end_of_month_list():
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    first_day_next_month = datetime.datetime(next_year, next_month, 1)
    last_day_of_month = first_day_next_month - timedelta(days=1)

    remaining_days = (last_day_of_month - today).days + 1
    days_list = [today.strftime("%Y-%m-%d")]

    for i in range(0, remaining_days + 1):
        day = today + timedelta(days=i)
        day_name = day.strftime('%A')
        if day_name == 'Friday':
            day_name = 'Пт'
        elif day_name == 'Saturday':
            day_name = 'Сб'
        elif day_name == 'Sunday':
            day_name = 'Вс'
        elif day_name == 'Monday':
            day_name = 'Пн'
        elif day_name == 'Tuesday':
            day_name = 'Вт'
        elif day_name == 'Wednesday':
            day_name = 'Ср'
        elif day_name == 'Thursday':
            day_name = 'Чт'

        days_list.append(f"{day_name} {day.strftime('%m-%d')}")
    days_list.pop(0)
    return days_list


def get_days_until_today():
    today = datetime.datetime.today()
    first_day_of_month = today.replace(day=1)
    days = []

    current_day = first_day_of_month
    while current_day <= today:
        days.append(current_day.date().strftime("%Y-%m-%d"))
        current_day += timedelta(days=1)

    return days


def get_days_of_current_week():
    today = datetime.datetime.today()
    current_weekday = today.weekday()  # Получаем номер дня недели (понедельник - 0, воскресенье - 6)
    start_of_week = today - timedelta(days=current_weekday)  # Находим первый день текущей недели

    days_of_week = [start_of_week + timedelta(days=i) for i in range(7)]  # Список дней текущей недели
    days_strings = [day.strftime('%Y-%m-%d') for day in days_of_week]  # Преобразование дат в строки

    return days_strings


def get_all_days_of_current_month():
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    _, num_days = calendar.monthrange(year, month)
    days_list = [f"{year}-{month:02d}-{day:02d}" for day in range(1, num_days + 1)]
    return days_list


print(days_until_end_of_month_list())