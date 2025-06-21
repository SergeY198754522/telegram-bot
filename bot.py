import telebot
from telebot import types

# Временно — прямой токен
BOT_TOKEN = "7974655972:AAFLmCVwL7amk7B8uQW3UmGP7616GKR8HHY"
bot = telebot.TeleBot(BOT_TOKEN)

# 📌 Обработка команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Напиши название монеты (например, Биткоин)")

# 📌 Обработка текстов: если написали "Биткоин" → показываем кнопку infoBTC
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip().lower()

    if text in ["биткоин", "bitcoin", "btc"]:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("infoBTC", callback_data="info_btc")
        markup.add(btn)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Пока распознаю только 'Биткоин' — напиши его 😊")

# 📌 Обработка кнопки infoBTC
@bot.callback_query_handler(func=lambda call: call.data == "info_btc")
def handle_info_btc(call):
    # здесь будет логика запроса информации
    bot.send_message(call.message.chat.id, "ℹ️ Информация о BTC: [будет позже]")

bot.polling()
