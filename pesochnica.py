import telebot

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)
@bot.message_handler(commands=['start'])
def start(message):
    f = [1, 2, 4]
    bot.send_message(message.chat.id, f' {f}Привет! Введите текст:')

    # Регистрируем следующий шаг для ожидания ввода текста от пользователя
    bot.register_next_step_handler(message, lambda msg: process_text_input(msg, f, message.chat.id))

def process_text_input(message, f, chat_id):
    user_text = message.text
    bot.send_message(chat_id, f'Вы ввели:  {f} {user_text}')

bot.polling()
