import asyncio
import httpx
import os
from datetime import datetime
from telegram import Bot

# ================== Config ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))

TRON_API = "https://trongrid.io"

# သတ်မှတ်ထားသော မိနစ်များ
TARGET_MINUTES = {"00","01","09","10","11","19","20","21","29","30","31","39","40","41","49","50","51","59"}

print("🚀 6Lottery TRX Bot (Fixed Delay & Block Check) Started...")
bot = Bot(token=TELEGRAM_TOKEN)

async def get_latest_block_digit(client):
    try:
        # Async စနစ်ဖြင့် Tron API သို့ လှမ်းခေါ်ခြင်း
        resp = await client.get(TRON_API, timeout=10)
        data = resp.json()
        
        # Block Number နှင့် Block Hash (ID) ကို ယူခြင်း
        block_header = data.get('block_header', {}).get('raw_data', {})
        block_number = block_header.get('number', 'Unknown')
        block_hash = data.get('blockID', '')
        
        if block_hash:
            # ၎င်း Block Hash ၏ နောက်ဆုံး ဂဏန်း (0-9) ကို ရှာခြင်း
            for char in reversed(block_hash.strip()):
                if char.isdigit():
                    digit = int(char)
                    print(f"✅ Block #{block_number} | Digit Found: '{char}' → {digit}")
                    return digit, block_number
            
            # ဂဏန်း လုံးဝမတွေ့ပါက နောက်ဆုံး Hex စာလုံးကို ယူခြင်း (ဒိုင်ခံအဆင့်)
            last_char = block_hash.strip()[-1].lower()
            digit = int(last_char, 16) % 10
            print(f"⚠️ Fallback Used | Block #{block_number} | Digit: {digit}")
            return digit, block_number
            
        return None, None
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None, None

async def main():
    async with httpx.AsyncClient() as client:
        last_processed_minute = ""

        while True:
            now = datetime.now()
            minute = now.strftime("%M")
            second = now.second

            # ဂိမ်းက ၁၇:၄၁:၅၄ မှာပြီးရင်၊ ၅၆ သို့မဟုတ် ၅၇ စက္ကန့်ရောက်မှ API ခေါ်ရန် ညှိထားပါသည်
            if minute in TARGET_MINUTES and (second == 56 or second == 57) and minute != last_processed_minute:
                last_processed_minute = minute  # တစ်မိနစ်လျှင် တစ်ကြိမ်သာ အလုပ်လုပ်စေရန်
                
                # Block ထွက်လာသည်အထိ သေချာစေရန် ၀.၅ စက္ကန့် ထပ်စောင့်ခြင်း
                await asyncio.sleep(0.5)
                
                last_digit, block_num = await get_latest_block_digit(client)
                
                if last_digit is not None:
                    # ရလဒ် သတ်မှတ်ခြင်း (၅ နှင့် အထက် Big၊ ၄ နှင့် အောက် Small)
                    result = "B" if last_digit >= 5 else "S"
                    
                    # Telegram သို့ ပို့မည့် Message ပုံစံ
                    msg = (
                        f"🎯 <b>6Lottery TRX RESULT</b>\n\n"
                        f"📦 Block: <code>#{block_num}</code>\n"
                        f"🔢 Last Digit: <b>{last_digit}</b>\n"
                        f"📊 Result: <b>{'🔴 BIG' if result == 'B' else '🔵 SMALL'}</b>"
                    )
                    
                    print(f"Result Sent: Block #{block_num} -> {last_digit} ({result})")
                    
                    # Telegram ထံသို့ Message လှမ်းပို့ခြင်း
                    try:
                        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="HTML")
                    except Exception as e:
                        print(f"❌ Telegram Send Error: {e}")

            # CPU ပေါ်ဝန်မပိစေရန် ၀.၃ စက္ကန့် တစ်ကြိမ်သာ Loop ပတ်စေခြင်း
            await asyncio.sleep(0.3)

if __name__ == "__main__":
    asyncio.run(main())
