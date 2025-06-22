import telebot
from telebot import types
import requests

BOT_TOKEN = "7974655972:AAFLmCVwL7amk7B8uQW3UmGP7616GKR8HHY"
CMC_API_KEY = "680f73b1-591c-4d53-817c-d0882ba12253"

bot = telebot.TeleBot(BOT_TOKEN)

# Загружаем все монеты с CoinMarketCap
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
        symbol_map[symbol.lower()] = symbol
    return symbol_map

coin_map = load_coin_map()

def find_symbol(text):
    return coin_map.get(text.lower())

# Команда /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("/topgainers")
    btn2 = types.KeyboardButton("/toplosers")
    btn3 = types.KeyboardButton("BTC")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "\U0001F44B Напиши название или сокращение криптомонеты (например: эфириум, btc, sol)\n\n\U0001F4CD Или выбери одну из команд ниже:", reply_markup=markup)

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: message.text and not message.text.startswith("/"))
def handle_text(message):
    text = message.text.strip().lower()
    symbol = find_symbol(text)
    if symbol:
        # Вместо кнопки создаем inline-кнопку с callback
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(f"info{symbol}", callback_data=f"info_{symbol}")
        markup.add(btn)
        bot.send_message(message.chat.id, f"Вы выбрали {symbol.upper()}.", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "\u274C Монета не найдена. Попробуй точнее (например: Эфириум, Биткоин, Солана)")

# Обработка callback кнопки info
@bot.callback_query_handler(func=lambda call: call.data.startswith("info_"))
def handle_info(call):
    symbol = call.data.split("_")[1].upper()
    try:
        url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
        params = {"symbol": symbol, "convert": "USDT"}

        r = requests.get(url, headers=headers, params=params)
        data = r.json()["data"][symbol]["quote"]["USDT"]

        price = data["price"]
        cap = data["market_cap"] / 1_000_000_000
        change = data["percent_change_24h"]

        fear_greed = ""
        if symbol == "BTC":
            fng = requests.get("https://api.alternative.me/fng/?limit=30").json()["data"]
            index = round(sum([int(x["value"]) for x in fng]) / len(fng), 1)
            fear_greed = f"\n\u2022 \U0001F9E0 Индекс страха и жадности (30д): *{index}/100*"

        msg = (
            f"\U0001F4CA *Информация о {symbol} (в USDT)*\n"
            f"\u2022 \U0001F4B5 Цена: *${price:.5f}*\n"
            f"\u2022 \U0001F4B0 Капитализация: *${cap:.2f}B*\n"
            f"\u2022 \U0001F4C8 Изменение за 24ч: *{change:.2f}%*"
            + fear_greed
        )
        bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Ошибка при получении {symbol}: {e}")

# Обработка команд /topgainers и /toplosers
@bot.message_handler(commands=['topgainers'])
def top_gainers(message):
    bot.send_message(message.chat.id, get_top_movers("gainers"))

@bot.message_handler(commands=['toplosers'])
def top_losers(message):
    bot.send_message(message.chat.id, get_top_movers("losers"))

def get_top_movers(direction="gainers", limit=10):
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    params = {"convert": "USDT", "limit": 100}

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()["data"]
        sorted_data = sorted(
            data,
            key=lambda x: x["quote"]["USDT"]["percent_change_24h"],
            reverse=(direction == "gainers")
        )
        top = sorted_data[:limit]
        lines = []
        for coin in top:
            name = coin["name"]
            symbol = coin["symbol"]
            price = coin["quote"]["USDT"]["price"]
            change = coin["quote"]["USDT"]["percent_change_24h"]
            emoji = "📈" if change >= 0 else "📉"
            lines.append(f"{emoji} *{symbol}* — ${price:.5f} ({change:.2f}%)")
        return "\n".join(lines)
    except Exception as e:
        return f"⚠️ Ошибка получения данных: {e}"

if __name__ == '__main__':
    print("🤖 Бот запущен.")
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(f"❌ Ошибка при запуске polling: {e}")
