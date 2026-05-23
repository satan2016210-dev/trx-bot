import os
import telebot
from flask import Flask

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live!"

try:
    bot.send_message(CHAT_ID, "🚀 Sniper Alert Bot ဆာဗာပေါ်တွင် အောင်မြင်စွာ စတင်လည်ပတ်နေပါပြီဗျာ။")
except Exception as e:
    print(f"Error sending message: {e}")

if name == "main":
    port = int(os.environ.get("PORT", 5000))
    from threading import Thread
    Thread(target=lambda: bot.infinity_polling()).start()
    app.run(host="0.0.0.0", port=port)
