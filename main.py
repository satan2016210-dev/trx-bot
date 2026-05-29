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

print("🚀 6Lottery TRX Bot (BlockID Mode) Started...")

bot = Bot(token=TELEGRAM_TOKEN)

async def main():
    while True:
        now = datetime.now()
        minute = now.strftime("%M")
        second = now.second

        if minute in TARGET_MINUTES and second == 54:
            try:
                resp = requests.get(TRON_API, timeout=10)
                data = resp.json()
                
                # BlockID ကို အဓိက သုံး (Game နဲ့ ပိုကိုက်နိုင်တယ်)
                block_id = data.get('blockID', '')
                if block_id:
                    last_char = block_id.strip()[-1].lower()
                    digit = int(last_char, 16) % 10
                    result = "B" if digit >= 5 else "S"
                    
                    print(f"[{now.strftime('%H:%M:%S')}] BlockID Last: '{last_char}' → {digit} | {result}")
                else:
                    print("No blockID found")
                    
            except Exception as e:
                print(f"API Error: {e}")

        await asyncio.sleep(0.25)

if __name__ == "__main__":
    asyncio.run(main())
