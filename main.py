import os
import subprocess
import sys
import time

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
MY_PHONE_NUMBER = "+959420724320"

API_ID = 32962994
API_HASH = "527688e1a63242cae36f4b5f4e4339e2"
TARGET_GROUP_NAME = "Mr.Wai SIGNAL"

bot = telebot.TeleBot(BOT_TOKEN)
recent_results = []
phone_code_hash = None
current_phone_code = None

# Telethon Client ကို အပြင်မှာ ကြိုတင်ဆောက်ထားခြင်း
client = TelegramClient('trx_session', API_ID, API_HASH)

# --- [ဗျူဟာမြောက် တွက်ချက်မှုအပိုင်း] ---
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
                "⚠️ (၀၊ ၁၊ ၂ မိနစ်) ၃ ကြိမ်ဆက်တိုက် B ချည်းပဲ ထွက်ထားပါတယ်!\n\n"
                f"📈 နောက်ဆုံးအလှည့်: {period}\n"
                "⚡ အခုအလှည့်မှာ **S (Small)** ကို အပိုင် ဒိုင်းခနဲ သွားဆွဲလိုက်တော့ဗျာ! 🚀"
            )
            try:
                bot.send_message(MY_CHAT_ID, alert_message, parse_mode="Markdown")
            except Exception as e:
                print(f"[ERROR] Failed to send alert: {e}")

# --- [TELEGRAM PRIVATE GROUP စောင့်ကြည့်သည့်အပိုင်း] ---
@client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', '')
        if TARGET_GROUP_NAME in chat_title:
            match = re.search(r"Trx\s+(\d+)\s+([BS])(\d+)", event.raw_text, re.IGNORECASE)
            if match:
                check_strategy_and_alert(match.group(1), match.group(2).upper(), match.group(3))
    except Exception as e:
        print(f"[ERROR] Handler Error: {e}")

# --- [BOT စကားပြောခန်း အဆင့်ဆင့် ထိန်းချုပ်မည့်အပိုင်း] ---
@bot.message_handler(func=lambda message: message.chat.id == MY_CHAT_ID)
def handle_all_messages(message):
    global phone_code_hash, current_phone_code
    text = message.text.strip()

    # အဆင့် ၁ - အသုံးပြုသူက /start ပို့လိုက်လျှင် OTP တောင်းရန် အလုပ်စခိုင်းခြင်း
    if text == "/start":
        bot.reply_to(message, "⏳ Telegram ဆီကနေ OTP Code တောင်းဆိုနေပါပြီ။ ခဏစောင့်ပေးပါဗျာ...")
        
        # Telethon ကို ချိတ်ဆက်ပြီး OTP ကုဒ် လှမ်းတောင်းခိုင်းခြင်း
        async def request_code():
            global phone_code_hash
            await client.connect()
            if not await client.is_user_authorized():
                try:
                    send_code_result = await client.send_code_request(MY_PHONE_NUMBER)
                    phone_code_hash = send_code_result.phone_code_hash
                    bot.send_message(MY_CHAT_ID, "🔑 **Telegram OTP Code ထွက်လာပါပြီ!**\n\nသင့်ရဲ့ Telegram Official အကောင့်ထဲကို ဝင်လာတဲ့ **ဂဏန်း ၅ လုံး** ကို ဒီ Bot ထဲမှာတင် စာအဖြစ် ပြန်ရိုက်ပို့ပေးပါဗျာ။")
                except Exception as e:
                    bot.send_message(MY_CHAT_ID, f"❌ ကုဒ်တောင်းတာ မအောင်မြင်ပါ။ Error: {e}\nခဏနေမှ `/start` ပြန်နှိပ်ပေးပါ။")
            else:
                bot.send_message(MY_CHAT_ID, "✅ **အကောင့်က ဝင်ပြီးသားဖြစ်နေပါတယ်ဗုာ!** Sniper Bot စတင် အလုပ်လုပ်နေပါပြီ။")
        
        asyncio.run_coroutine_threadsafe(request_code(), client.loop)

    # အဆင့် ၂ - အသုံးပြုသူက ဂဏန်း ၅ လုံး ပို့လာလျှင် Login ဝင်ခိုင်းခြင်း
    elif re.match(r"^\d{5}$", text):
        current_phone_code = text
        bot.reply_to(message, f"📥 OTP ကုဒ် [{text}] ကို လက်ခံရရှိပါပြီ။ အကောင့်ထဲ စတင် Login ဝင်နေပါပြီ...")
        
        async def login_with_code():
            try:
                await client.sign_in(MY_PHONE_NUMBER, current_phone_code, phone_code_hash=phone_code_hash)
                bot.send_message(MY_CHAT_ID, "✅ **Telegram Account ချိတ်ဆက်မှု အောင်မြင်သွားပါပြီဗျာ!**\n\nSniper Bot စတင်အသက်ဝင်သွားပါပြီ။ Mr.Wai SIGNAL ဂရုထဲက စာတွေကို စောင့်ကြည့်နေပါပြီ။")
            except Exception as e:
                bot.send_message(MY_CHAT_ID, f"❌ Login မအောင်မြင်ပါ။ Error: {e}\nကျေးဇူးပြု၍ ပြန်စရန် `/start` ကို ပြန်နှိပ်ပေးပါ။")
        
        asyncio.run_coroutine_threadsafe(login_with_code(), client.loop)
        
    else:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ စတင်ရန် `/start` လို့ရိုက်ပို့ပါ (သို့မဟုတ်) Telegram က ပို့ပေးတဲ့ ဂဏန်း ၅ လုံး သက်သက်ပဲ ပို့ပေးပါဗျာ။")

def run_bot_polling():
    print("[BOT] Telegram Bot Polling started...")
    try:
        bot.send_message(MY_CHAT_ID, "🔔 **TRX Sniper Bot ဆာဗာပေါ်တွင် အဆင်သင့်ဖြစ်နေပါပြီဗျာ!**\n\nTelegram OTP Code လှမ်းတောင်းဖို့အတွက် အခု ဒီ Bot ထဲကို **`/start`** လို့ စာရိုက်ပို့ပေးလိုက်ပါဗျာ။")
    except Exception as e:
        print(f"[BOT ERROR] {e}")
    bot.infinity_polling()

# --- [WEB SERVER - RENDER အသက်ဆက်ရန်] ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is running perfectly. Awaiting user action."

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def run_telethon_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Loop ထဲမှာ client အလုပ်လုပ်အောင် ကြိုတင် ပွင့်ထားခိုင်းခြင်း
    loop.run_until_complete(client.connect())
    print("[TELETHON] Client loop is running...")
    loop.run_forever()

# --- [ပင်မ စတင်မောင်းနှင်ချက်] ---
if __name__ == '__main__':
    # ၁။ Flask Web Server မောင်းနှင်ခြင်း
    t_flask = Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()
    
    # ၂။ Telegram Bot Polling မောင်းနှင်ခြင်း
    t_bot = Thread(target=run_bot_polling)
    t_bot.daemon = True
    t_bot.start()
    
    # ၃။ Telethon Loop ကို သီးသန့် Background Thread မှာ မောင်းနှင်ခြင်း
    t_telethon = Thread(target=run_telethon_thread)
    t_telethon.daemon = True
    t_telethon.start()
    
    # ပင်မဆာဗာ မပိတ်သွားအောင် စောင့်ထိန်းထားခြင်း
    while True:
        time.sleep(1)
