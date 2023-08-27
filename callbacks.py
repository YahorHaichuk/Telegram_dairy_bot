import sqlite3
from bot_handlers import update_info_handler, update_task
from telebot import types

from auxiliary_functions import duration_in_minutes
from database import BotDb
import telebot


TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)

def all_callbacks(call):
    db = BotDb('dairy_db.sql')
    task_text_range_week = None
    task_text_range_month = None
    today_tasks = BotDb('dairy_db.sql').get_day_tasks(call.message.chat.id)
    # try:
    #     if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'week':
    #         task_text_range_week = (BotDb('dairy_db.sql').get_task_range_week(call.data.split('*')[1].strip(), call.message.chat.id))
    # except TypeError:
    #     task_text_range_week = None
    #
    # try: #Нажатие кнопки "месяц"
    #     if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'month':
    #         task_text_range_month = (
    #             BotDb('dairy_db.sql').get_task_range_month(call.data.split('*')[1].strip(), call.message.chat.id))
    # except TypeError:
    #     task_text_range_month = None
    #
    # try: #Нажатие кнопки "день месяца"
    #     if len(call.data.split('*')) > 2 and call.data.split('*')[2].strip() == 'month_daily':
    #         task_text_range_month = (
    #             BotDb('dairy_db.sql').get_task_range_month(call.data.split('*')[0].strip(), call.message.chat.id))
    # except TypeError:
    #     task_text_range_month = None
    #
    # if (
    #         call.data is not None and today_tasks is not None and call.data in today_tasks):  # выполнение сегодняшней задачи
    #     done_today_callback(call)
    # if len(call.data.split('*')) == 3:
    #     if (task_text_range_week is not None
    #             and call.data.split('*')[1] == task_text_range_week
    #             and call.data.split('*')[2].strip() == 'week'):
    #         callback_recurring_tasks_many_words_handler(call)  # период повторения неделя
    # if len(call.data.split('*')) == 3:
    #     if (task_text_range_month is not None and
    #             call.data.split('*')[1].strip() == task_text_range_month and call.data.split('*')[
    #                 2].strip() == 'month'):
    #         cycle_month(call)  # период повторения месяц
    #
    # if len(call.data.split('*')) > 1 and call.data.split('*')[1].strip() in days:
    #     if (BotDb('dairy_db.sql').get_task_range_week(#вызвывает функцию записи повторных задач на неделю
    #             call.data.split('*')[0].strip(), call.message.chat.id)) and (
    #             call.data.split('*')[1].strip() in days):
    #         recurring_tasks_week(call)
    #
    # if call.data == 'only_one':# добавляет задачу без довторения
    #     bot.send_message(call.message.chat.id, 'Задача добавлена')
    # # вызвывает функцию записи повторных задач на месяц
    # if len(call.data.split('*')) == 3:
    #     if (task_text_range_month is not None and
    #             call.data.split('*')[0].strip() == task_text_range_month and call.data.split('*')[
    #                 2].strip() == 'month_daily'):
    #         month_cycle_add(call)

    # вызывет функцию редактирования задачи
    # if (len(call.data.split('*')) >= 3 and call.data.split('*')[1:][0] == 'task_edit'):
    #     if ((call.data.split('*')[1:][1].strip(), call.data.split('*')[1:][2].strip())
    #             in BotDb('dairy_db.sql').get_task_editing(call.message, call.data.split('*')[1:][1].strip())):
    #         editing_task = call.data.split('*')[1:][1].strip()
    #         editing_date = call.data.split('*')[1:][2].strip()
    #         update_info_handler(call.message, editing_task, editing_date)
    #         data = [editing_task, editing_date]
    #         bot.register_next_step_handler(call.message, lambda msg: update_task(msg, data=data))


#     if (len(call.data.split('*')) >= 3 and call.data.split('*')[1:][0] == 'task_delete'):
#         if ((call.data.split('*')[1:][1].strip(), call.data.split('*')[1:][2].strip())
#                 in BotDb('dairy_db.sql').get_task_editing(call.message, call.data.split('*')[1:][1].strip())):
#             deleting_task = call.data.split('*')[1:][1].strip()
#             deleting_task_date = call.data.split('*')[1:][2].strip()
#             db.delete(deleting_task, deleting_task_date)
#             bot.send_message(call.message.chat.id, f''' задача {deleting_task} в день {deleting_task_date} удалена
# ''')

