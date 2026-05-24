import os
import subprocess
import sys
import re
import asyncio
from flask import Flask
from threading import Thread

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

from telethon import TelegramClient, events

# --- [အခြေခံ SETTINGS များ] ---
BOT_TOKEN = "8589041336:AAEJ3gwKssb8Dq75tRb6MH08UXLCG74MCQ8"
MY_CHAT_ID = 1141743561
MY_PHONE_NUMBER = "+959420724320"

API_ID = 32962994
API_HASH = "527688e1a63242cae36f4b5f4e4339e2"
TARGET_GROUP_NAME = "Mr.Wai SIGNAL"

bot = telebot.TeleBot(BOT_TOKEN)
client = TelegramClient('trx_session', API_ID, API_HASH)

recent_results = []
phone_code_hash = None
is_processing = False  # ထပ်ခါထပ်ခါ ကုဒ်မတောင်းမိစေရန် သော့ခတ်စနစ်

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

# --- [FLASK WEB SERVER - RENDER အသက်ဆက်ရန်] ---
app = Flask('')
@app.route('/')
def home():
    return "Bot is running perfectly. Awaiting action."

def run_flask():
    app.run(host='0.0.0.0', port=10000)

# --- [အဓိက ASYNCIO ပင်မစနစ်ကြီး] ---
async def main():
    global phone_code_hash, is_processing
    print("[INIT] Connecting to Telegram...")
    await client.connect()
    
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

    try:
        bot.send_message(MY_CHAT_ID, "🔔 **TRX Sniper Bot ဆာဗာပေါ်တွင် အသင့်ဖြစ်ပါပြီ!**\n\nTelegram ဆီကနေ OTP ကုဒ်တောင်းဖို့အတွက် အခု ဒီ Bot ထဲကို **`/start`** လို့ တစ်ချက်ပဲ နှိပ်ပြီး စာရိုက်ပို့ပေးလိုက်ပါဗျာ။")
    except Exception as e:
        print(f"[BOT ERROR] Greeting failed: {e}")

    # Telegram Bot ကနေ စာလာဖတ်မည့်စနစ် (Long Polling ကဲ့သို့ စနစ်တကျ ပြောင်းလဲခြင်း)
    bot.last_update_id = 0
    # ကြိုတင်ပြီး Update ID များကို ရှင်းလင်းခြင်း
    updates = bot.get_updates(timeout=1)
    if updates:
        bot.last_update_id = updates[-1].update_id

    while True:
        updates = bot.get_updates(offset=(bot.last_update_id + 1 if bot.last_update_id else None), timeout=1)
        for update in updates:
            if update.message and update.message.chat.id == MY_CHAT_ID:
                text = update.message.text.strip()
                bot.last_update_id = update.update_id
                
                # ၁။ /start ပို့လာလျှင် (ပတ်မနေအောင် သော့ခတ်ပြီး တစ်ခေါက်ပဲ တောင်းမည်)
                if text == "/start":
                    if is_processing:
                        bot.send_message(MY_CHAT_ID, "⚠️ ခဏစောင့်ပါဦးဗျာ။ အနောက်မှာ အလုပ်လုပ်နေဆဲ ဖြစ်ပါတယ်။")
                        continue
                        
                    is_processing = True
                    bot.send_message(MY_CHAT_ID, "⏳ Telegram Official ထံမှ OTP Code (တစ်ခေါက်တည်း) တောင်းဆိုနေပါပြီ။ ခဏစောင့်ပေးပါဗျာ...")
                    
                    try:
                        if not await client.is_user_authorized():
                            send_code_result = await client.send_code_request(MY_PHONE_NUMBER)
                            phone_code_hash = send_code_result.phone_code_hash
                            bot.send_message(MY_CHAT_ID, "🔑 **Telegram OTP Code ထွက်လာပါပြီဗျာ!**\n\nမိတ်ဆွေရဲ့ Telegram Official အကောင့်ထဲကို ဝင်လာတဲ့ **ဂဏန်း ၅ လုံး** ကို ဒီ Bot ထဲမှာတင် စာရိုက်ပို့ပေးပါဗျာ။")
                        else:
                            bot.send_message(MY_CHAT_ID, "✅ အကောင့်က ဝင်ပြီးသား ဖြစ်နေပါတယ်ဗျာ။ Sniper Bot စတင် အလုပ်လုပ်နေပါပြီ။")
                    except Exception as e:
                        bot.send_message(MY_CHAT_ID, f"❌ ကုဒ်တောင်း၍မရပါ။ Error: {e}\n\n၁ မိနစ်နေမှ `/start` ပြန်နှိပ်ပါ။")
                    finally:
                        is_processing = False

                # ၂။ ဂဏန်း ၅ လုံး ပို့လာလျှင်
                elif re.match(r"^\d{5}$", text):
                    if is_processing:
                        continue
                    is_processing = True
                    bot.send_message(MY_CHAT_ID, f"📥 OTP ကုဒ် [{text}] ကို ရရှိပါပြီ။ အကောင့်ထဲ ဝင်နေပါပြီ...")
                    try:
                        await client.sign_in(MY_PHONE_NUMBER, text, phone_code_hash=phone_code_hash)
                        bot.send_message(MY_CHAT_ID, "✅ **Telegram Account ချိတ်ဆက်မှု အောင်မြင်သွားပါပြီဗျာ!**\n\nSniper Bot စတင်အသက်ဝင်သွားပါပြီ။")
                    except telethon.errors.SessionPasswordNeededError:
                        bot.send_message(MY_CHAT_ID, "⚠️ သင့်အကောင့်မှာ Two-Step Verification (2FA) ခံထားပါတယ်ဗျာ။ သင့်ရဲ့ လုံခြုံရေး Password ကို Bot ထဲ ရိုက်ပို့ပေးပါဗျ။")
                    except Exception as e:
                        bot.send_message(MY_CHAT_ID, f"❌ လော့ဂ်အင်မအောင်မြင်ပါ။ Error: {e}\n\nပြန်စရန် `/start` ပြန်နှိပ်ပါ။")
                    finally:
                        is_processing = False
                
                # ၃။ 2FA Password ရိုက်ပို့လာလျှင်
                elif len(text) > 5 and phone_code_hash:
                    try:
                        await client.sign_in(password=text)
                        bot.send_message(MY_CHAT_ID, "✅ **2FA Password ဖြင့် ချိတ်ဆက်မှု အောင်မြင်သွားပါပြီဗျာ!**\n\nSniper Bot အသက်ဝင်သွားပါပြီ။")
                    except Exception as e:
                        bot.send_message(MY_CHAT_ID, f"❌ Password မှားယွင်းနေပါသည်။ Error: {e}")

        await asyncio.sleep(0.5)

if __name__ == '__main__':
    t_flask = Thread(target=run_flask)
    t_flask.daemon = True
    t_flask.start()
    
    asyncio.run(main())
