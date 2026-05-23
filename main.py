import os
import sys
import telebot
from flask import Flask
from threading import Thread

# Environment Variables မှ သော့ချက်များ ယူခြင်း
TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

if not TOKEN or not CHAT_ID:
    print("CRITICAL ERROR: TOKEN သို့မဟုတ် CHAT_ID မရှိသေးပါဗျာ။")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running live!"

# Flask Web Server ကို သီးသန့် အလုပ်လုပ်ခိုင်းမည့် လုပ်ဆောင်ချက်
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🚀 Web Server ကို အရင်စတင် နှိုးနေပါတယ်...")
    # Flask ဆာဗာကို Background အနေနဲ့ Thread ပေါ်မှာ အရင်မောင်းနှင်မည်
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    
    try:
        print("🚀 Telegram Bot စတင် လည်ပတ်ပါပြီ...")
        # သင့် Telegram ဆီသို့ စာလှမ်းပို့မည်
        bot.send_message(CHAT_ID, "🚀 Sniper Alert Bot ဆာဗာပေါ်တွင် အောင်မြင်စွာ စတင်လည်ပတ်နေပါပြီဗျာ။")
        
        # Bot ကို ပိတ်မသွားအောင် ထိန်းထားမည်
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"Bot Error Occurred: {e}")
        sys.exit(1)
