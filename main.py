import asyncio
import requests
import os
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode

# ================== Config ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

TRON_API = "https://api.trongrid.io/wallet/getnowblock"

TARGET_MINUTES = {"00","01","09","10","11","19","20","21","29","30","31","39","40","41","49","50","51","59"}

print("🚀 6Lottery TRX Bot (Fixed 54s Mode) Started...")

bot = Bot(token=TELEGRAM_TOKEN)

last_processed = None

async def main():
    global last_processed

    while True:
        now = datetime.now()
        minute = now.strftime("%M")
        second = now.second
        hour = now.strftime("%H")

        # 54 စက္ကန့်မှာ ပဲ စစ်မယ်
        if minute in TARGET_MINUTES and second == 54:
            check_key = f"{hour}{minute}{second}"

            if check_key != last_processed:
                last_processed = check_key
                
                print(f"📍 Checking at {now.strftime('%H:%M:%S')}")

                try:
                    resp = requests.get(TRON_API, timeout=8)
                    data = resp.json()
                    block_hash = data.get('block_header', {}).get('raw_data', {}).get('parentHash', '')
                    
                    if block_hash:
                        last_char = block_hash.strip()[-1].lower()
                        digit = int(last_char, 16) % 10
                        result = "B" if digit >= 5 else "S"
                        
                        print(f"🎯 RESULT → {digit} | {result}")

                        # 012 Cycle (00 နဲ့ 01 ပဲ)
                        if minute in ["00", "01"]:
                            print(f"   → 012 Check: {result}")
                except Exception as e:
                    print(f"API Error: {e}")

        await asyncio.sleep(0.2)

if __name__ == "__main__":
    asyncio.run(main())
