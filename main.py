import os
import re
from flask import Flask
from threading import Thread
import telethon
from telethon import TelegramClient, events
import telebot

# --- [အခြေခံ SETTINGS များ] ---
# TODO: သင့်ရဲ့ မူလ Bot Token နဲ့ သင့်ကိုယ်ပိုင် Telegram Chat ID ကို အောက်မှာ ပြန်ထည့်ပေးပါဗျာ
BOT_TOKEN = 8589041336:AAHs4twJ3WgVN0T7-fSZuSdU-AJUovRWoBc
MY_CHAT_ID = 1141743561

# my.telegram.org မှ ရရှိထားသော သော့ချက်များ
API_ID = 32962994
API_HASH = "527688e1a63242cae36f4b5f4e4339e2"
TARGET_GROUP_NAME = "Mr.Wai SIGNAL"

# Bot နှင့် Client များ တည်ဆောက်ခြင်း
bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient('trx_session', API_ID, API_HASH)

# ဗျူဟာမှတ်ဉာဏ်ပတ်လမ်း (ရလဒ် နောက်ဆုံး ၃ ကြိမ်စာ မှတ်ထားရန်)
# ဥပမာ - ['S', 'B', 'S'] စသဖြင့် မှတ်ပါမည်။
recent_results = []

# --- [ဗျူဟာမြောက် တွက်ချက်မှုအပိုင်း] ---
def check_strategy_and_alert(period, result, level):
    global recent_results
    
    # ရလဒ်အသစ်ကို ပတ်လမ်းထဲ ထည့်ပြီး နောက်ဆုံး ၃ ကြိမ်စာပဲ ချန်မည်
    recent_results.append(result)
    if len(recent_results) > 3:
        recent_results.pop(0)
        
    print(self_status_log := f"[INFO] အလှည့်: {period} | ရလဒ်: {result} | Level: {level} | ပတ်လမ်းလက်ရှိအခြေအနေ: {recent_results}")
    
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
    # စာဝင်လာသော Group/Channel နာမည်ကို စစ်ဆေးခြင်း
    chat = await event.get_chat()
    chat_title = getattr(chat, 'title', '')
    
    if TARGET_GROUP_NAME in chat_title:
        message_text = event.raw_text
        
        # 'Trx 44 B2' သို့မဟုတ် 'Trx 37 S1' စာသားပုံစံကို Regular Expression ဖြင့် ဖတ်ခြင်း
        match = re.search(r"Trx\s+(\d+)\s+([BS])(\d+)", message_text, re.IGNORECASE)
        if match:
            period = match.group(1)   # အလှည့် (ဥပမာ - 44)
            result = match.group(2).upper()  # ရလဒ် B သို့မဟုတ် S
            level = match.group(3)    # Level (ဥပမာ - 2)
            
            # ဗျူဟာ စစ်ဆေးရန် ပို့ပေးခြင်း
            check_strategy_and_alert(period, result, level)

# --- [WEB SERVER & KEEP ALIVE အပိုင်း] ---
app = Flask('')

@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- [MAIN EXECUTION] ---
if __name__ == '__main__':
    # Web Server ကို Thread ခွဲပြီး မောင်းထားရန်
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    print("[START] Telegram Client Script is starting...")
    # Telegram Client ကို အသက်သွင်းပြီး မောင်းနှင်ခြင်း
    client.start()
    client.run_until_disconnected()
