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

@app.route('/')
def home():
    return "TRX Sniper Bot (012 Combo 3X Mode) is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print("Telegram error:", e)

def monitor_trx():
    last_period = ""
    # 012 မိနစ်အတွဲကြီး ဘယ်နှစ်ကြိမ် ဆက်တိုက် S မပါဘဲ အောင်မြင်ခဲ့လဲ မှတ်မည့် Memory
    no_s_combo_count = 0 
    
    print("🚀 TRX Win Sniper Bot (012 Combo 3X Mode) စတင်ပါပြီ...")
    send_telegram_alert("🚀 Sniper Alert Bot အောင်မြင်စွာ စတင်လည်ပတ်ပါပြီ။\n🎯 ဗျူဟာ - 0,1,2 မိနစ်အတွဲလိုက်ကြီး (၃) ကြိမ်ဆက်တိုက် S လုံးဝမပါဝင်မှသာ အချက်ပေးပါမည်။")
    
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
                
                # ပွဲစဉ်အသစ် တက်လာမှသာ စစ်ဆေးမည်
                if current_period != last_period:
                    last_period = current_period
                    current_minute = current_period[-1] # ယခုပွဲစဉ်၏ နောက်ဆုံးမိနစ်ဂဏန်း
                    
                    # မိနစ် '2' ရောက်တဲ့အချိန်တိုင်း (ဥပမာ - 02, 12, 22... မိနစ်များတွင်) 
                    # ၎င်းအတွဲ၏ 0, 1, 2 မိနစ် ရလဒ်များကို စစ်ဆေးမည်
                    if current_minute == '2':
                        result_0 = None
                        result_1 = None
                        result_2 = None
                        
                        # API ထဲမှ အနီးစပ်ဆုံးထွက်ခဲ့သော 0, 1, 2 မိနစ် ရလဒ်များကို လိုက်လံခွဲထုတ်ခြင်း
                        for game in game_list:
                            p_str = str(game['period'])
                            p_min = p_str[-1]
                            
                            # လက်ရှိပွဲစဉ်တွဲနှင့် ကိုက်ညီသော မိနစ်များကို ရှာဖွေခြင်း
                            # (ဥပမာ - အခုပွဲစဉ်က ၁၂ မိနစ်ဆိုလျှင် ၁၀၊ ၁၁၊ ၁၂ မိနစ် ရလဒ်များကို ယူမည်)
                            if p_str[:-1] == current_period[:-1]:
                                if p_min == '0': result_0 = game['result']
                                if p_min == '1': result_1 = game['result']
                                if p_min == '2': result_2 = game['result']
                        
                        # 0, 1, 2 မိနစ် သုံးခုစလုံး ရလဒ်ထွက်ပေါ်လာပြီးချိန်တွင်
                        if result_0 and result_1 and result_2:
                            results_012 = [result_0, result_1, result_2]
                            
                            # ၎င်း 0, 1, 2 မိနစ်အတွဲထဲတွင် S (Small) လုံးဝ မပါဝင်ခဲ့လျှင်
                            if "S" not in results_012 and "Small" not in results_012:
                                no_s_combo_count += 1 # မှတ်ဉာဏ်တွင် ၁ ကြိမ် တိုးလိုက်မည်
                                print(f"🔥 မိနစ် 012 အတွဲတွင် S မပါဝင်မှု အောင်မြင် - အကြိမ်အရေအတွက်: {no_s_combo_count}/3")
                            else:
                                # အကယ်၍ S တစ်လုံးပဲဖြစ်ဖြစ် ပါသွားခဲ့လျှင် ဆက်တိုက်ဖြစ်စဉ် ပျက်သွားသဖြင့် Counter ကို 0 ပြန်စမည်
                                no_s_combo_count = 0
                                print(f"❌ မိနစ် 012 အတွဲတွင် S ပါဝင်သွားသဖြင့် အစက ပြန်စပါမည်။")
                            
                            # ဗျူဟာအတိုင်း 012 အတွဲကြီး ၃ ကြိမ် ဆက်တိုက် ဆင့်သွားပြီဆိုလျှင် စာပို့မည်
                            if no_s_combo_count >= 3:
                                msg = (
                                    "🚨🚨🚨 *TRX WIN - SUPER SNIPER ALERT! (အထူးအပိုင်ကွက်)* 🚨🚨🚨\n\n"
                                    "⚠️ *သတိပေးချက် အဆင့်မြင့် -* \n"
                                    f"မိနစ် `0`၊ `1`၊ `2` အတွဲလိုက်ကြီး **(၃) ကြိမ်ဆက်တိုက်** (စုစုပေါင်း ပွဲစဉ် ၉ ပွဲစာ) အတွင်း `S (Small)` ထွက်ခြင်း လုံးဝ မရှိသေးပါခင်ဗျာ။\n\n"
                                    f"📋 နောက်ဆုံးထွက်ခဲ့သည့် 012 ရလဒ်အတွဲ - `{results_012}`\n\n"
                                    "🎯 ဗျူဟာမြောက် ၃ ကြိမ်ဆင့် ပိတ်ထားခြင်းဖြစ်၍ ယခုလာမည့်အလှည့်များတွင် `S` ပြန်ထွက်ရန် အခွင့်အလမ်း အလွန်အမင်း မြင့်မားနေပါပြီ။ ဗျူဟာအတိုင်း လုံးဝ အပိုင်ဆွဲနိုင်ပါပြီဗျာ။"
                                )
                                send_telegram_alert(msg)
                                no_s_combo_count = 0 # စာပို့ပြီးလျှင် နောက်တစ်ကြိမ်တွက်ရန် 0 ပြန်စမည်
            
            time.sleep(15)
            
        except Exception as e:
            print("Error fetching data, retrying...", e)
            time.sleep(10)

if __name__ == "__main__":
    t = Thread(target=monitor_trx)
    t.daemon = True
    t.start()
    run_flask()
