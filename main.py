import os
import subprocess
import sys

# --- [TELETHON နှင့် BOT API ကို အော်တိုသွင်းသည့်စနစ်] ---
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

# --- [အခြေခံ SETTINGS များ - မိတ်ဆွေ၏ အချက်အလက်များ] ---
BOT_TOKEN = "8589041336:AAHs4twJ3WgVN0T7-fSZuSdU-AJUovRWoBc"
MY_CHAT_ID = 1141743561  # ဂဏန်းသက်သက်အဖြစ် ပြောင်းလဲထားပါသည်
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

# --- [BOT ကနေ OTP ကုဒ်ကို တိုက်ရိုက်ဖတ်မည့်အပိုင်း] ---
@bot.message_handler(func=lambda message: message.chat.id == MY_CHAT_ID)
def handle_otp_from_user(message):
    global current_phone_code
    text = message.text.strip()
    
    # မိတ်ဆွေ ပို့လိုက်တဲ့စာက ဂဏန်း ၅ လုံး ဖြစ်မဖြစ် စစ်ဆေးခြင်း
    if re.match(r"^\d{5}$", text):
        current_phone_code = text
        bot.reply_to(message, f"📥 OTP ကုဒ် [{text}] ကို ဆာဗာထဲ ထည့်သွင်းလိုက်ပါပြီဗျာ။ အကောင့်ထဲ စတင် Login ဝင်နေပါပြီ...")
    else:
        bot.reply_to(message, "⚠️ ကျေးဇူးပြု၍ Telegram က ပို့ပေးတဲ့ ဂဏန်း ၅ လုံးသက်သက်ပဲ စာရိုက်ပို့ပေးပါဗျာ။")

# --- [WEB SERVER - RENDER အတွက် အသေထားရမည့်အပိုင်း] ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running perfectly. Waiting for OTP via Telegram Chat Bot."

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- [AUTOMATED TELETHON LOGIN] ---
async def main_login():
    global phone_code_hash, current_phone_code
    print("[INIT] Connecting to Telegram Servers...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print(f"[LOGIN] Requesting OTP code for {MY_PHONE_NUMBER}...")
        try:
            send_code_result = await client.send_code_request(MY_PHONE_NUMBER)
            phone_code_hash = send_code_result.phone_code_hash
            
            # မိတ်ဆွေဆီ စာလှမ်းပို့ပြီး ကုဒ်တောင်းခြင်း
            login_instruction = (
                "🔑 **Telegram OTP Code ရောက်လာပါပြီဗျာ!**\n\n"
                "မိတ်ဆွေရဲ့ Telegram Official အကောင့်ထဲကို ရောက်လာတဲ့ **ဂဏန်း ၅ လုံး** ကို **ဒီ Bot ချက်တင်ထဲမှာတင် စာအဖြစ် တိုက်ရိုက် ရိုက်ပို့ပေးလိုက်ပါဗျာ**။\n\n"
                "*(ဥပမာ - `54321` လို့ ဂဏန်းချည်းပဲ ရိုက်ပို့ပေးရမှာပါဗျ)*"
            )
            bot.send_message(MY_CHAT_ID, login_instruction, parse_mode="Markdown")
            print("[LOGIN] Instruction link sent to Telegram Bot.")
        except Exception as e:
            print(f"[ERROR] Cannot send code request: {e}")
            return
            
        # မိတ်ဆွေက Bot ထဲမှာ စာရိုက်ပို့မည့်အချိန်အထိ စောင့်ဆိုင်းခြင်း
        while current_phone_code is None:
            await asyncio.sleep(1)
            
        print(f"[LOGIN] Logging in with OTP Code: {current_phone_code}")
        try:
            await client.sign_in(MY_PHONE_NUMBER, current_phone_code, phone_code_hash=phone_code_hash)
            print("[LOGIN] Successfully authorized with Telegram!")
            bot.send_message(MY_CHAT_ID, "✅ **Telegram Account ချိတ်ဆက်မှု အောင်မြင်သွားပါပြီဗျာ!**\n\nSniper Bot အသက်ဝင်သွားပါပြီ။ Mr.Wai SIGNAL ဂရုထဲက စာတွေကို စတင်စောင့်ကြည့်နေပါပြီ။")
        except Exception as e:
            print(f"[ERROR] Login Failed: {e}")
            bot.send_message(MY_CHAT_ID, f"❌ Sign in မအောင်မြင်ပါဗျာ။ Error: {e}\nကျေးဇူးပြု၍ Render ကို တစ်ခေါက် Manual Deploy ပြန်လုပ်ပေးပါ။")
            return
            
    print("[START] Connected! Listening to target private group...")
    await client.run_until_disconnected()

# Bot ရဲ့ Message Listener ကို နောက်ကွယ်ကနေ မောင်းထားရန်
def run_bot_polling():
    bot.infinity_polling()

if __name__ == '__main__':
    # Web Server မောင်းနှင်ခြင်း
    t_flask = Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()
    
    # Telegram Bot Messages ဖတ်မည့်စနစ် မောင်းနှင်ခြင်း
    t_bot = Thread(target=run_bot_polling)
    t_bot.daemon = True
    t_bot.start()
    
    # Async Event Loop ဖြင့် Telethon ကို အသက်သွင်းခြင်း
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(main_login())
