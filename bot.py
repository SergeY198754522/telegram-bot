import telebot
from telebot import types
import requests
import os

BOT_TOKEN = "7974655972:AAFLmCVwL7amk7B8uQW3UmGP7616GKR8HHY"
CMC_API_KEY = "680f73b1-591c-4d53-817c-d0882ba12253"

bot = telebot.TeleBot(BOT_TOKEN)

# Загрузка всех монет с CoinMarketCap
def load_coin_map():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    response = requests.get(url, headers=headers)
    coins = response.json()["data"]
    symbol_map = {}
    for coin in coins:
        name = coin["name"].lower()
        symbol = coin["symbol"].upper()
        symbol_map[name] = symbol
        symbol_map[symbol.lower()] = symbol  # добавляем сокращения тоже
    return symbol_map

coin_map = load_coin_map()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 Напиши название или сокращение криптомонеты (например: эфириум, btc, sol)")

# 📌 Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().lower()

    for key in coin_map:
        if key in text:
            symbol = coin_map[key]
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton(f"info{symbol}", callback_data=f"info_{symbol}")
            markup.add(btn)
            bot.send_message(message.chat.id, f"Вы выбрали {symbol}", reply_markup=markup)
            return

    bot.send_message(message.chat.id, "❌ Монета не найдена. Попробуй написать её точнее или в виде сокращения (например: BTC, ETH, DOGE)")

@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def handle_info(call):
    symbol = call.data.split("_")[1]
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
        params = {"symbol": symbol, "convert": "USDT"}

        r = requests.get(url, headers=headers, params=params)
        data = r.json()["data"][symbol]["quote"]["USDT"]

        price = data["price"]
        cap = data["market_cap"] / 1_000_000_000  # в миллиардах
        change = data["percent_change_24h"]

        fear_greed = ""
        if symbol == "BTC":
            fng = requests.get("https://api.alternative.me/fng/?limit=30").json()["data"]
            index = round(sum([int(x["value"]) for x in fng]) / len(fng), 1)
            fear_greed = f"\n• 🧠 Индекс страха и жадности (30д): *{index}/100*"

        msg = (
            f"📊 *Информация о {symbol} (в USDT)*\n"
            f"• 💵 Цена: *${price:.5f}*\n"
            f"• 💰 Капитализация: *${cap:.5f}B*\n"
            f"• 📈 Изменение за 24ч: *{change:.2f}%*"
            + fear_greed
        )

        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Ошибка при получении {symbol}: {e}")

bot.polling()
