import os
import subprocess
import sys

# --- [TELETHON နှင့် BOT API ကို အော်တိုသွင်းသည့်စနစ်] ---
try:
    import telethon
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
    import telethon

try:
    import telebot
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"])
    import telebot

import re
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# --- [အခြေခံ SETTINGS များ] ---
BOT_TOKEN = "8589041336:AAHs4twJ3WgVN0T7-fSZuSdU-AJUovRWoBc"
MY_CHAT_ID = 1141743561
API_ID = 32962994
API_HASH = "527688e1a63242cae36f4b5f4e4339e2"
TARGET_GROUP_NAME = "Mr.Wai SIGNAL"

bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient('trx_session', API_ID, API_HASH)
recent_results = []

def check_strategy_and_alert(period, result, level):
    global recent_results
    recent_results.append(result)
    if len(recent_results) > 3:
        recent_results.pop(0)
        
    print(f"[INFO] အလှည့်: {period} | ရလဒ်: {result} | Level: {level} | ပတ်လမ်း: {recent_results}")
    
    if len(recent_results) == 3:
        if recent_results == ['B', 'B', 'B']:
            alert_message = (
                "🎯 **TRX SNIPER ALERT!** 🎯\n\n"
                "🔥 အပိုင်ကွက် ဗဟိုချက်မ မိပါပြီ! 🔥\n"
                "📈 နောက်ဆုံးအလှည့်: {period}\n"
                "⚡ အခုအလှည့်မှာ **S (Small)** ကို အပိုင် ဒိုင်းခနဲ သွားဆွဲလိုက်တော့ဗျာ! 🚀"
            )
            try:
                bot.send_message(MY_CHAT_ID, alert_message, parse_mode="Markdown")
            except Exception as e:
                print(f"[ERROR] Alert Error: {e}")

@client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', '')
        if TARGET_GROUP_NAME in chat_title:
            message_text = event.raw_text
            match = re.search(r"Trx\s+(\d+)\s+([BS])(\d+)", message_text, re.IGNORECASE)
            if match:
                check_strategy_and_alert(match.group(1), match.group(2).upper(), match.group(3))
    except Exception as e:
        print(f"[ERROR] Handler Error: {e}")

app = Flask('')
@app.route('/')
def home():
    return "Bot is running perfectly with Session File!"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

async def main_login():
    print("[INIT] Connecting to Telegram Servers...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print("[ERROR] trx_session.session ဖိုင် မရှိပါ သို့မဟုတ် သက်တမ်းကုန်နေပါသည်။")
        return
        
    print("[START] Connected အောင်မြင်ပါပြီ! စာတင်စောင့်ကြည့်နေပါပြီ...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(main_login())
