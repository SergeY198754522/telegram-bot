import telebot
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # читаем токен из переменной окружения
bot = telebot.TeleBot(BOT_TOKEN)    # передаём токен

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Бот работает на Railway ✅")

bot.polling()
