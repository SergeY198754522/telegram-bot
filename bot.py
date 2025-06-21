import telebot
from telebot import types
import requests
import os

BOT_TOKEN = "7974655972:AAFLmCVwL7amk7B8uQW3UmGP7616GKR8HHY"
CMC_API_KEY = "680f73b1-591c-4d53-817c-d0882ba12253"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Напиши название монеты (например, Биткоин)")

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

@bot.callback_query_handler(func=lambda call: call.data == "info_btc")
def handle_info_btc(call):
    try:
        # --- Получаем данные о BTC с CoinMarketCap
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
        params = {"symbol": "BTC", "convert": "USD"}

        response = requests.get(url, headers=headers, params=params)
        data = response.json()["data"]["BTC"]["quote"]["USD"]

        price = round(data["price"], 2)
        market_cap = round(data["market_cap"] / 1_000_000_000, 2)
        percent_change = round(data["percent_change_24h"], 2)

        # --- Получаем индекс страха и жадности
        fng_response = requests.get("https://api.alternative.me/fng/?limit=30")
        fng_data = fng_response.json()["data"]
        last_30 = [int(item["value"]) for item in fng_data]
        average_fng = round(sum(last_30) / len(last_30), 1)

        # --- Формируем сообщение
        message_text = (
            f"📊 *Информация о Bitcoin (BTC)*\n"
            f"• 💵 Цена: *${price}*\n"
            f"• 💰 Капитализация: *${market_cap}B*\n"
            f"• 📈 Изменение за 24ч: *{percent_change}%*\n"
            f"• 🧠 Средний индекс страха и жадности (30д): *{average_fng}/100*"
        )

        bot.send_message(call.message.chat.id, message_text, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Ошибка получения данных: {e}")

bot.polling()