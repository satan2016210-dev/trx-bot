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

print("🚀 6Lottery TRX Bot (Last Digit Only) Started...")

bot = Bot(token=TELEGRAM_TOKEN)

def get_latest_block_digit():
    try:
        resp = requests.get(TRON_API, timeout=10)
        data = resp.json()
        
        # Block Hash ကို ယူမယ်
        block_hash = data.get('block_header', {}).get('raw_data', {}).get('parentHash', '')
        if not block_hash:
            block_hash = data.get('blockID', '')
        
        if block_hash:
            # နောက်ဆုံး ဂဏန်း (0-9) ကိုပဲ ရှာမယ်
            for char in reversed(block_hash.strip()):
                if char.isdigit():
                    digit = int(char)
                    print(f"✅ Last Digit Found: '{char}' → {digit}")
                    return digit
            # ဂဏန်း မတွေ့ရင် နောက်ဆုံး စာလုံး ယူမယ်
            last_char = block_hash.strip()[-1].lower()
            digit = int(last_char, 16) % 10
            print(f"✅ Fallback Digit: {digit}")
            return digit
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

async def main():
    while True:
        now = datetime.now()
        minute = now.strftime("%M")
        second = now.second

        if minute in TARGET_MINUTES and second == 54:
            last_digit = get_latest_block_digit()
            if last_digit is not None:
                result = "B" if last_digit >= 5 else "S"
                print(f"🎯 FINAL RESULT → {last_digit} | {result}")

        await asyncio.sleep(0.25)

if __name__ == "__main__":
    asyncio.run(main())
