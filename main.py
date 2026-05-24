import os
import re
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
import telebot

# --- [အခြေခံ SETTINGS များ - မိတ်ဆွေ၏ အချက်အလက်များ ထည့်သွင်းပြီး] ---
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
current_phone_code = None  # OTP ကုဒ် ယာယီသိမ်းရန်

# --- [ဗျူဟာမြောက် တွက်ချက်မှုအပိုင်း] ---
def check_strategy_and_alert(period, result, level):
    global recent_results
    recent_results.append(result)
    if len(recent_results) > 3:
        recent_results.pop(0)
        
    print(f"[INFO] အလှည့်: {period} | ရလဒ်: {result} | Level: {level} | ပတ်လမ်းလက်ရှိအခြေအနေ: {recent_results}")
    
    # ရလဒ် ၃ ကြိမ် ပြည့်ပြီဆိုမှ ဗျူဟာကို စစ်မည်
    if len(recent_results) == 3:
        # ဗျူဟာအိုင်ဒီယာ - (၀၊ ၁၊ ၂ မိနစ် အတွဲလိုက်ကြီး ၃ ကြိမ်ဆက်တိုက် S မပါရဘူး)
        # တစ်နည်းအားဖြင့် ၃ ကြိမ်ဆက်တိုက် 'B' ချည်းပဲ ထွက်လာခဲ့လျှင် (Big, Big, Big ဖြစ်လျှင်) Sniper မိပြီ!
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
                print("[SUCCESS] Alert message sent to your Telegram!")
            except Exception as e:
                print(f"[ERROR] Failed to send alert: {e}")

# --- [TELEGRAM PRIVATE GROUP စောင့်ကြည့်သည့်အပိုင်း] ---
@client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        chat = await event.get_chat()
        chat_title = getattr(chat, 'title', '')
        
        # သတ်မှတ်ထားသည့် Group နာမည် ဟုတ်မဟုတ် စစ်ဆေးခြင်း
        if TARGET_GROUP_NAME in chat_title:
            message_text = event.raw_text
            
            # 'Trx 44 B2' သို့မဟုတ် 'Trx 37 S1' စာသားပုံစံကို ဖတ်ခြင်း
            match = re.search(r"Trx\s+(\d+)\s+([BS])(\d+)", message_text, re.IGNORECASE)
            if match:
                period = match.group(1)   # အလှည့်
                result = match.group(2).upper()  # ရလဒ် B သို့မဟုတ် S
                level = match.group(3)    # Level
                
                check_strategy_and_alert(period, result, level)
    except Exception as e:
        print(f"[ERROR] Handler Error: {e}")

# --- [WEB SERVER & OTP RECEIVER အပိုင်း] ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running. Waiting for OTP code via Web Link if needed."

# Render ပေါ်တွင် OTP ဖြည့်ရန် စာမျက်နှာလင့်ခ်ဖန်တီးခြင်း
@app.route('/set_code/<code>')
def set_code(code):
    global current_phone_code
    current_phone_code = code
    return f"OTP Code {code} received! App is now signing in..."

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- [AUTOMATED TELETHON LOGIN] ---
async def main_login():
    global current_phone_code
    await client.connect()
    
    # Login ဝင်ရန်လိုအပ်ပါက OTP တောင်းမည်
    if not await client.is_user_authorized():
        print(f"[LOGIN] Sending code request to {MY_PHONE_NUMBER}...")
        try:
            await client.send_code_request(MY_PHONE_NUMBER)
            
            # မိတ်ဆွေ၏ ကိုယ်ပိုင် Bot ဆီသို့ လင့်ခ်လှမ်းပို့ခိုင်းခြင်း
            login_instruction = (
                "🔑 **Telegram OTP Code တောင်းနေပါပြီဗျာ!**\n\n"
                "မိတ်ဆွေရဲ့ Telegram Official ကနေ ပို့ပေးလိုက်တဲ့ ဂဏန်း ၅ လုံးကို အောက်ပါလင့်ခ်ရဲ့ အနောက်မှာ အစားထိုးပြီး Browser (Chrome) ထဲ ဝင်ပေးလိုက်ပါဗျာ -\n\n"
                "`https://trx-bot-hika.onrender.com/set_code/ဒီနေရာမှာဂဏန်း၅လုံးထည့်`"
            )
            bot.send_message(MY_CHAT_ID, login_instruction, parse_mode="Markdown")
        except Exception as e:
            print(f"[ERROR] Cannot send code request: {e}")
            return
            
        # လင့်ခ်ကနေတစ်ဆင့် ဂဏန်းဝင်လာသည်အထိ ဆာဗာကို စောင့်ခိုင်းခြင်း
        while current_phone_code is None:
            await asyncio.sleep(2)
            
        print(f"[LOGIN] Attempting to sign in with code: {current_phone_code}")
        try:
            await client.sign_in(MY_PHONE_NUMBER, current_phone_code)
            print("[LOGIN] Successfully authorized!")
            bot.send_message(MY_CHAT_ID, "✅ **Telegram Account ချိတ်ဆက်မှု အောင်မြင်သွားပါပြီဗျာ!**\n\nSniper Bot စတင် အလုပ်လုပ်နေပါပြီ။ Mr.Wai SIGNAL ဂရုထဲမှာ ၃ ကြိမ်ဆက်တိုက် B ထွက်တာနဲ့ သတိပေးချက် လှမ်းပို့ပေးပါ့မယ်ဗျာ။")
        except Exception as e:
            print(f"[ERROR] Sign in failed: {e}")
            bot.send_message(MY_CHAT_ID, f"❌ Sign in မအောင်မြင်ပါဗျာ။ Error: {e}\nကျေးဇူးပြု၍ Render ကို Manual Deploy ပြန်လုပ်ပေးပါ။")
            return
            
    print("[START] Script is listening to group messages...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    # Web Server ကို Thread ခွဲမောင်းနှင်ခြင်း
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # Telethon ကို Async Loop ဖြင့် အသက်သွင်းခြင်း
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_login())
