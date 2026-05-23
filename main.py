import os
import sys
import time
import requests
from flask import Flask
from threading import Thread

# ----------------- စနစ်အတွက် အချက်အလက်များ -----------------
TELEGRAM_TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
API_URL = "https://api.6a2d9r.com/api/games/trx-win/history"

if not TELEGRAM_TOKEN or not CHAT_ID:
    print("CRITICAL ERROR: Render Settings ထဲတွင် TOKEN သို့မဟုတ် CHAT_ID မရှိသေးပါဗျာ။")
    sys.exit(1)

app = Flask(__name__)

# UptimeRobot က လာပုတ်ရင် ချက်ချင်း "OK" ပြန်ပြီး ဆာဗာကို နိုးစေမည့်အလှည့်
@app.route('/')
def home():
    return "OK", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    # Threading သုံးပြီး ပေါ့ပေါ့ပါးပါး မောင်းနှင်ခြင်း
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

def monitor_trx():
    # ရုတ်တရက် ဆာဗာနိုးနိုးချင်း API ဆီ တန်းမတောင်းဘဲ ဆာဗာ အခြေကျအောင် ၅ စက္ကန့် စောင့်ခြင်း
    time.sleep(5)
    last_period = ""
    no_s_combo_count = 0 
    
    print("🚀 TRX Win Sniper Bot (012 Combo 3X Mode) စတင်ပါပြီ...")
    
    while True:
        try:
            response = requests.get(API_URL, timeout=15)
            if response.status_code == 200:
                data = response.json()
                game_list = data.get('data', {}).get('list', [])
                
                if not game_list or len(game_list) < 15:
                    time.sleep(15)
                    continue
                    
                latest_game = game_list[0]
                current_period = str(latest_game['period'])
                
                if current_period != last_period:
                    last_period = current_period
                    current_minute = current_period[-1]
                    
                    if current_minute == '2':
                        result_0 = None
                        result_1 = None
                        result_2 = None
                        
                        for game in game_list:
                            p_str = str(game['period'])
                            p_min = p_str[-1]
                            
                            if p_str[:-1] == current_period[:-1]:
                                if p_min == '0': result_0 = game['result']
                                if p_min == '1': result_1 = game['result']
                                if p_min == '2': result_2 = game['result']
                        
                        if result_0 and result_1 and result_2:
                            results_012 = [result_0, result_1, result_2]
                            
                            if "S" not in results_012 and "Small" not in results_012:
                                no_s_combo_count += 1
                                print(f"🔥 မိနစ် 012 S မပါမှု အောင်မြင်: {no_s_combo_count}/3")
                            else:
                                no_s_combo_count = 0
                                print(f"❌ မိနစ် 012 တွင် S ပါသွားသဖြင့် 0 ပြန်စပါမည်။")
                            
                            if no_s_combo_count >= 3:
                                msg = (
                                    "🚨🚨🚨 *TRX WIN - SUPER SNIPER ALERT! (အထူးအပိုင်ကွက်)* 🚨🚨🚨\n\n"
                                    "⚠️ *သတိပေးချက် အဆင့်မြင့် -* \n"
                                    f"မိနစ် `0`၊ `1`၊ `2` အတွဲလိုက်ကြီး **(၃) ကြိမ်ဆက်တိုက်** အတွင်း `S (Small)` ထွက်ခြင်း လုံးဝ မရှိသေးပါခင်ဗျာ။\n\n"
                                    f"📋 နောက်ဆုံးထွက်ခဲ့သည့် 012 ရလဒ်အတွဲ - `{results_012}`\n\n"
                                    "🎯 ယခုလာမည့်အလှည့်များတွင် `S` ပြန်ထွက်ရန် အခွင့်အလမ်း အလွန်အမင်း မြင့်မားနေပါပြီ။ ဗျူဟာအတိုင်း လုံးဝ အပိုင်ဆွဲနိုင်ပါပြီဗျာ။"
                                )
                                send_telegram_alert(msg)
                                no_s_combo_count = 0
            
            time.sleep(15)
            
        except Exception as e:
            print("Error fetching data, retrying...", e)
            time.sleep(10)

if __name__ == "__main__":
    # Flask Web Server ကို သီးသန့် Background Thread တစ်ခုအနေဖြင့် အရင်မောင်းမည်
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()
    
    # ဂိမ်းဒေတာ စောင့်ကြည့်ရေးလုပ်ငန်းကို Main ပတ်လမ်းတွင် မောင်းမည်
    monitor_trx()
