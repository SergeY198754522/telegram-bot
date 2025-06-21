import telebot
from telebot import types
import requests
import os

BOT_TOKEN = "7974655972:AAFLmCVwL7amk7B8uQW3UmGP7616GKR8HHY"
CMC_API_KEY = "680f73b1-591c-4d53-817c-d0882ba12253"

bot = telebot.TeleBot(BOT_TOKEN)

# Загружаем доступные монеты при старте
def load_coin_map():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    response = requests.get(url, headers=headers)
    coins = response.json()["data"]
    name_to_symbol = {}
    for coin in coins:
        name = coin["name"].lower()
        symbol = coin["symbol"].upper()
        name_to_symbol[name] = symbol
    return name_to_symbol

# Словарь имя монеты → символ (например: "солана" → "SOL")
coin_map = load_coin_map()

# /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 Напиши название криптомонеты (например, Эфириум, Солана)")

# 📌 Обработка обычного текста → предложить кнопку info
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.strip().lower()

    for name in coin_map:
        if text == name:
            symbol = coin_map[name]
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton(f"info{symbol}", callback_data=f"info_{symbol}")
            markup.add(btn)
            bot.send_message(message.chat.id, f"Вы выбрали {name.title()}.", reply_markup=markup)
            return

    bot.send_message(message.chat.id, "❌ Монета не найдена. Попробуй точнее (например: Эфириум, Биткоин, Солана)")

# 📌 Обработка кнопок info_SYMBOL
@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def handle_info(call):
    symbol = call.data.split("_")[1]
    try:
        # Получаем данные монеты
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
        params = {"symbol": symbol, "convert": "USD"}

        r = requests.get(url, headers=headers, params=params)
        data = r.json()["data"][symbol]["quote"]["USD"]

        price = round(data["price"], 2)
        cap = round(data["market_cap"] / 1_000_000_000, 2)
        change = round(data["percent_change_24h"], 2)

        # Индекс страха и жадности — только для BTC
        fear_greed = ""
        if symbol == "BTC":
            fng = requests.get("https://api.alternative.me/fng/?limit=30").json()["data"]
            index = round(sum([int(x["value"]) for x in fng]) / len(fng), 1)
            fear_greed = f"\n• 🧠 Индекс страха и жадности (30д): *{index}/100*"

        msg = (
            f"📊 *Информация о {symbol}*\n"
            f"• 💵 Цена: *${price}*\n"
            f"• 💰 Капитализация: *${cap}B*\n"
            f"• 📈 Изменение за 24ч: *{change}%*"
            + fear_greed
        )

        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Ошибка при получении данных: {e}")

bot.polling()
