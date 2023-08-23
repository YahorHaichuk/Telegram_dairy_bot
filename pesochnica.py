import threading
from datetime import datetime, timedelta
import locale


def days_until_end_of_month_list():
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')  # Устанавливаем русскую локаль
    today = datetime.today()
    year = today.year
    month = today.month
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    first_day_next_month = datetime(next_year, next_month, 1)
    last_day_of_month = first_day_next_month - timedelta(days=1)

    remaining_days = (last_day_of_month - today).days + 1
    days_list = [today.strftime("%Y-%m-%d")]

    for i in range(1, remaining_days + 1):
        day = today + timedelta(days=i)
        day_name = day.strftime('%A')
        if day_name == 'пятница':
            day_name = 'Пт'
        elif day_name == 'суббота':
            day_name = 'Сб'
        elif day_name == 'воскресенье':
            day_name = 'Вс'
        elif day_name == 'понедельник':
            day_name = 'Пн'
        elif day_name == 'вторник':
            day_name = 'Вт'
        elif day_name == 'среда':
            day_name = 'Ср'
        elif day_name == 'четверг':
            day_name = 'Чт'

        days_list.append(f"{day_name} {day.strftime('%m-%d')}")

    return days_list


event = threading.Event()
