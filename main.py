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

print("🚀 6Lottery TRX Bot Started...")

bot = Bot(token=TELEGRAM_TOKEN)

def get_digit():
    try:
        r = requests.get(TRON_API, timeout=10)
        data = r.json()
        hash_str = data.get('block_header', {}).get('raw_data', {}).get('parentHash', '')
        if hash_str:
            last = hash_str[-1].lower()
            digit = int(last, 16) % 10
            return digit
        return None
    except:
        return None

async def main():
    while True:
        now = datetime.now()
        minute = now.strftime("%M")
        second = now.second

        if second == 54:   # 54 စက္ကန့်မှာ စစ်မယ်
            digit = get_digit()
            if digit is not None:
                result = "B" if digit >= 5 else "S"
                print(f"[{now.strftime('%H:%M:%S')}] Digit: {digit} → {result}")

                # 012 မိနစ်တွေမှာ ပဲ စစ်မယ်
                if minute in ["00","01","02"]:
                    print(f"   012 Cycle Check: {result}")

        await asyncio.sleep(0.3)

if __name__ == "__main__":
    asyncio.run(main())
