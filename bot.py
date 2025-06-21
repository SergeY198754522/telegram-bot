import telebot
import os

# Временно передаём токен напрямую
BOT_TOKEN = "7974655972:AAFLmCVwL7amk7B8uQW3UmGP7616GKR8HHY"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Бот работает на Railway ✅")

bot.polling()
