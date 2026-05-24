import os
import subprocess
import sys

# --- [မှော်ကွက်- TELETHON မရှိပါက ဆာဗာပေါ်တွင် အော်တိုသွင်းခိုင်းသည့်စနစ်] ---
try:
    import telethon
except ImportError:
    print("[SYSTEM] Telethon not found. Installing it automatically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "telethon"])
    import telethon

try:
    import telebot
except ImportError:
    print("[SYSTEM] pyTelegramBotAPI not found. Installing it automatically...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyTelegramBotAPI"])
    import telebot

import re
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# --- [အခြေခံ SETTINGS များ] ---
BOT_TOKEN = "8589041336:AAHs4twJ3WgVN0T7-fSZuSdU-AJUovRWoBc"
MY_CHAT_ID = "1141743561"
MY_PHONE_NUMBER = "+959420724320"

API_ID = 32962994
API_HASH = "527688e1a63242cae36f4b5f4e4339e2"
TARGET_GROUP_NAME = "Mr.Wai SIGNAL"

# Bot နှင့် Client တည်ဆောက်ခြင်း
bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient('trx_session', API_ID, API_HASH)

recent_results = []
phone_code_hash = None
current_phone_code = None

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
                "⚠️ (၀၊ ၁၊ ၂ မိနစ်) ၃ ကြိမ်ဆက်တိုက် S မပါဘဲ B ချည်းပဲ ထွက်ထားပါတယ်!\n\n"
                f"📈 နောက်ဆုံးအလှည့်: {period}\n"
                f"📊 ထွက်သွားသောပုံစံ: {recent_results[0]} ➡️ {recent_results[1]} ➡️ {recent_results[2]}\n\n"
                "⚡ အခုအလှည့်မှာ **S (Small)** ကို အပိုင် ဒိုင်းခနဲ သွားဆွဲလိုက်တော့ဗျာ! 🚀"
            )
            try:
                bot.send_message(MY_CHAT_ID, alert_message, parse_mode="Markdown")
                print("[SUCCESS] Alert sent to Telegram!")
            except Exception as e:
                print(f"[ERROR] Failed to send alert: {e}")

# --- [TELEGRAM PRIVATE GROUP စောင့်ကြည့်သည့်အပိုင်း] ---
@client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', '')
        if TARGET_GROUP_NAME in chat_title:
            message_text = event.raw_text
            match = re.search(r"Trx\s+(\d+)\s+([BS])(\d+)", message_text, re.IGNORECASE)
            if match:
                period = match.group(1)
                result = match.group(2).upper()
                level = match.group(3)
                check_strategy_and_alert(period, result, level)
    except Exception as e:
        print(f"[ERROR] Handler Error: {e}")

# --- [WEB SERVER & OTP RECEIVER ONSITE] ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly. Waiting for OTP web input if requested."

@app.route('/set_code/<code>')
def set_code(code):
    global current_phone_code
    current_phone_code = str(code).strip()
    return f"<h3>OTP Code [{current_phone_code}] ကို ဆာဗာထဲ ထည့်သွင်းပြီးပါပြီဗျာ။ အကောင့်ထဲ စတင် Login ဝင်နေပါပြီ။</h3>"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- [AUTOMATED LOGIN BYPASS] ---
async def main_login():
    global phone_code_hash, current_phone_code
    print("[INIT] Connecting to Telegram Servers...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print(f"[LOGIN] Requesting OTP code for {MY_PHONE_NUMBER}...")
        try:
            send_code_result = await client.send_code_request(MY_PHONE_NUMBER)
            phone_code_hash = send_code_result.phone_code_hash
            
            login_instruction = (
                "🔑 **Telegram OTP Code တောင်းနေပါပြီဗျာ!**\n\n"
                "မိတ်ဆွေရဲ့ Telegram Official အကောင့်ထဲကို ရောက်လာတဲ့ **ဂဏန်း ၅ လုံး** ကို အောက်ပါလင့်ခ်ရဲ့ အနောက်ဆုံးမှာ အစားထိုးပြီး Chrome Browser ထဲမှာ ရိုက်ထည့်ကာ ဝင်ပေးလိုက်ပါဗျာ -\n\n"
                "`https://trx-bot-hika.onrender.com/set_code/ဒီမှာဂဏန်း၅လုံးထည့်`"
            )
            bot.send_message(MY_CHAT_ID, login_instruction, parse_mode="Markdown")
            print("[LOGIN] Instruction link sent to Telegram Bot.")
        except Exception as e:
            print(f"[ERROR] Cannot send code request: {e}")
            return
            
        while current_phone_code is None:
            await asyncio.sleep(1)
            
        print(f"[LOGIN] Logging in with OTP Code: {current_phone_code}")
        try:
            await client.sign_in(MY_PHONE_NUMBER, current_phone_code, phone_code_hash=phone_code_hash)
            print("[LOGIN] Successfully authorized with Telegram!")
            bot.send_message(MY_CHAT_ID, "✅ **Telegram Account ချိတ်ဆက်မှု အောင်မြင်သွားပါပြီဗျာ!**\n\nSniper Bot အသက်ဝင်သွားပါပြီ။ Mr.Wai SIGNAL ဂရုထဲက စာတွေကို စတင်စောင့်ကြည့်နေပါပြီ။")
        except Exception as e:
            print(f"[ERROR] Login Failed: {e}")
            bot.send_message(MY_CHAT_ID, f"❌ Sign in မအောင်မြင်ပါဗျာ။ Error: {e}")
            return
            
    print("[START] Connected! Listening to target private group...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_login())
