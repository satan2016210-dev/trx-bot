import asyncio
import httpx
import os
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode

# ================== Config ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

TRON_API = "https://api.trongrid.io/wallet/getnowblock"

# သင်လိုချင်တဲ့ မိနစ်တွေ
TARGET_MINUTES = {"00","01","09","10","11","19","20","21","29","30","31","39","40","41","49","50","51","59"}

print("🚀 6Lottery TRX Bot (Final Clean Version) Started...")

bot = Bot(token=TELEGRAM_TOKEN)

async def get_latest_block_digit(client):
    try:
        resp = await client.get(TRON_API, timeout=10.0)
        data = resp.json()
        
        # Block Hash ကနေ နောက်ဆုံး ဂဏန်း (0-9) ကိုပဲ ယူမယ်
        block_hash = data.get('blockID', '') or data.get('block_header', {}).get('raw_data', {}).get('parentHash', '')
        
        if block_hash:
            # နောက်ဆုံး ဂဏန်း (0-9) ကို ရှာမယ်
            for char in reversed(block_hash):
                if char.isdigit():
                    digit = int(char)
                    print(f"✅ Found Last Digit: {digit} (from {block_hash[-8:]})")
                    return digit
            # ဂဏန်း မတွေ့ရင် fallback
            last_char = block_hash[-1].lower()
            digit = int(last_char, 16) % 10
            print(f"⚠️ Fallback Digit: {digit}")
            return digit
            
        return None
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

async def main():
    async with httpx.AsyncClient() as client:
        while True:
            now = datetime.now()
            minute = now.strftime("%M")
            second = now.second

            if minute in TARGET_MINUTES and second == 54:
                digit = await get_latest_block_digit(client)
                
                if digit is not None:
                    result = "B" if digit >= 5 else "S"
                    print(f"🎯 [{now.strftime('%H:%M:%S')}] Digit: {digit} → {result}")

                    # 012 Cycle (00 & 01)
                    if minute in ["00", "01"]:
                        print(f"   → 012 Check: {result}")

            await asyncio.sleep(0.25)

if __name__ == "__main__":
    asyncio.run(main())
