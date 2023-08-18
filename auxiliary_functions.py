import datetime
from datetime import timedelta
import telebot

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'

bot = telebot.TeleBot(TOKEN)
today = datetime.date.today()


def duration_in_minutes(start_time, end_time):
    start = datetime.datetime.strptime(start_time, '%H:%M')
    end = datetime.datetime.strptime(end_time, '%H:%M')

    time_difference = end - start

    minutes = time_difference.total_seconds() / 60
    return int(minutes)


def get_week_days_list():
    """Возвращает оставшиеся дни недели  до конца недели в формате даты."""
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
    """Возвращает оставшиеся дни недели  до конца недели в формате даты."""
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
    """Получаем все оставшиеся дни текущего месяца начиная с сегодня в виде списка"""
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
