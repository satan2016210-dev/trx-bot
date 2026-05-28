import asyncio
import requests
import os
from datetime import datetime
from collections import deque
from telegram import Bot
from telegram.constants import ParseMode

# ================== Config ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID_STR = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID_STR:
    print("❌ ERROR: Missing Token or Chat ID!")
    exit()

CHAT_ID = int(CHAT_ID_STR.strip())

TRON_API = "https://api.trongrid.io/wallet/getnowblock"

cycle_history = deque(maxlen=4)
current_cycle_key = None
cycle_results = []
# ===========================================

bot = Bot(token=TELEGRAM_TOKEN)

def get_latest_block_digit():
    try:
        resp = requests.get(TRON_API, timeout=8)
        data = resp.json()
        block_hash = data.get('block_header', {}).get('raw_data', {}).get('parentHash', '')
        
        if block_hash:
            last_char = block_hash.strip()[-1].lower()
            digit = int(last_char, 16) % 10
            print(f"Hash Last: '{last_char}' → Digit: {digit}")
            return digit
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

async def main():
    global current_cycle_key, cycle_results
    print("🚀 6Lottery TRX Bot (58-59s Mode) Started...")

    while True:
        now = datetime.now()
        minute = now.strftime("%M")
        second = now.second
        hour = now.strftime("%H")

        # 58 နဲ့ 59 စက္ကန့်မှာ စစ်မယ်
        if second in [58, 59]:
            check_key = hour + minute + str(second)
            if check_key != current_cycle_key:
                current_cycle_key = check_key
                
                print(f"📍 Checking at {now.strftime('%H:%M:%S')} (58-59s mode)")
                
                last_digit = get_latest_block_digit()
                
                if last_digit is not None:
                    result = "B" if last_digit >= 5 else "S"
                    print(f"🎯 RESULT → {last_digit} | {result}")

                    # 012 Cycle စစ်ဆေးမှု
                    if minute in ["00", "01", "02"]:
                        cycle_results.append(result)

                        if minute == "02" and len(cycle_results) >= 3:
                            cycle_str = "".join(cycle_results[-3:])
                            print(f"   012 Cycle: {cycle_str}")

                            if cycle_str == "BBB":
                                cycle_history.append("BBB")
                                if len(cycle_history) >= 4:
                                    alert = f"""
🔥 <b>6LOTTERY BIG ALERT</b> 🔥

🕒 အချိန်: {now.strftime('%Y-%m-%d %H:%M:%S')}
📊 012 Cycle: <b>BBBB</b> (4 ခါ ဆက်တိုက်)

⚠️ သတိထားပါ!
                                    """
                                    await bot.send_message(chat_id=CHAT_ID, text=alert, parse_mode=ParseMode.HTML)
                                    print("✅ ALERT SENT!")
                            else:
                                cycle_history.clear()
                            
                            cycle_results = []

        await asyncio.sleep(0.3)

if __name__ == "__main__":
    asyncio.run(main())
