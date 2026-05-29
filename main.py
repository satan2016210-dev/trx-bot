import asyncio
import requests
import os
from datetime import datetime
from collections import deque
from telegram import Bot
from telegram.constants import ParseMode

# ================== Config ==================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
TRON_API = "https://api.trongrid.io/wallet/getnowblock"

TARGET_MINUTES = {
    "00","01","09","10","11","19","20","21",
    "29","30","31","39","40","41","49","50","51","59"
}

cycle_history = deque(maxlen=4)
current_cycle_key = None
cycle_results = []
last_reset_key = None
# ===========================================
bot = Bot(token=TELEGRAM_TOKEN)

def get_latest_block_digit():
    try:
        resp = requests.get(TRON_API, timeout=8)
        data = resp.json()

        # ✅ blockID = Block Hash အပြည့်အစုံ (6Lottery နဲ့ ကိုက်ညီတယ်)
        block_id = data.get('blockID', '')

        if block_id:
            last_char = block_id.strip()[-1].lower()
            digit = int(last_char, 16) % 10
            print(f"✅ Block Hash Last: '{last_char}' → Digit: {digit}")
            return digit
        return None
    except Exception as e:
        print(f"API Error: {e}")
        return None

async def main():
    global current_cycle_key, cycle_results, last_reset_key
    print("🚀 6Lottery TRX Bot (54s Mode) Started...")

    while True:
        try:
            now = datetime.now()
            minute = now.strftime("%M")
            second = now.second
            hour = now.strftime("%H")

            # ✅ 54 စက္ကန့်မှာပဲ စစ်မယ်
            if minute in TARGET_MINUTES and second == 54:
                check_key = f"{hour}{minute}"

                if check_key != current_cycle_key:
                    current_cycle_key = check_key

                    print(f"📍 Checking at {now.strftime('%H:%M:%S')}")
                    last_digit = get_latest_block_digit()

                    if last_digit is not None:
                        result = "B" if last_digit >= 5 else "S"
                        print(f"🎯 RESULT → {last_digit} | {result}")

                        if minute in ["00", "01"]:
                            # ✅ Minute "00" မှာ cycle အသစ်စတိုင်း reset
                            reset_key = f"{hour}00"
                            if minute == "00" and last_reset_key != reset_key:
                                cycle_results = []
                                last_reset_key = reset_key
                                print("🔄 Cycle Reset")

                            cycle_results.append(result)
                            print(f"   cycle_results: {cycle_results}")

                            # ✅ Minute "01" မှာ cycle စစ်မယ်
                            if minute == "01" and len(cycle_results) >= 2:
                                cycle_str = "".join(cycle_results[-2:])
                                print(f"   01 Cycle: {cycle_str}")

                                if cycle_str == "BB":
                                    cycle_history.append("BB")
                                    print(f"   History: {list(cycle_history)}")

                                    if len(cycle_history) == 4:
                                        alert = f"""🔥 <b>6LOTTERY BIG ALERT</b> 🔥
🕒 အချိန်: {now.strftime('%Y-%m-%d %H:%M:%S')}
📊 01 Cycle: <b>BBBB</b> (4 ခါ ဆက်တိုက်)
⚠️ သတိထားပါ!"""
                                        await bot.send_message(
                                            chat_id=CHAT_ID,
                                            text=alert,
                                            parse_mode=ParseMode.HTML
                                        )
                                        print("✅ ALERT SENT!")
                                        cycle_history.clear()
                                else:
                                    cycle_history.clear()

                                cycle_results = []

        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(5)

        await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(main())
