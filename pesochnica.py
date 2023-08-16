@bot.message_handler(commands=['done_today_tasks'])
def done_today_tasks(message):
    db = BotDb('dairy_db.sql')
    day_tasks = db.day_tasks(message.chat.id)
    db.close()

    today_tasks = []
    buttons = []

    markup = types.InlineKeyboardMarkup()

    for t in day_tasks:
        today_tasks.append(t[1])

    for i in today_tasks:
        buttons.append(types.InlineKeyboardButton(text=i, callback_data=i))

    markup.add(*buttons)
    bot.send_message(message.chat.id, 'нажмите на выполненную задачу', reply_markup=markup)
    global user_today_tasks
    user_today_tasks = today_tasks