import sqlite3

from telebot import types

from auxiliary_functions import duration_in_minutes
from database import BotDb, CurrentHour
import telebot

TOKEN = '6193050640:AAGxCsSYcN9ykAf6N29Z-bcLCYUFqQYJ7YQ'
bot = telebot.TeleBot(TOKEN)