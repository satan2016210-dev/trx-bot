async def main():
    global current_cycle_key, cycle_results
    print("🚀 6Lottery TRX Bot (54 Second Mode) Started...")
    
    last_processed_minute = None  # ✅ Cycle tracking အတွက် အသစ်ထည့်

    while True:
        now = datetime.now()
        minute = now.strftime("%M")
        second = now.second
        hour = now.strftime("%H")

        if second == 54:
            check_key = f"{hour}{minute}{second}"

            if check_key != current_cycle_key:
                current_cycle_key = check_key

                print(f"📍 Checking at {now.strftime('%H:%M:%S')} (54s)")
                last_digit = get_latest_block_digit()

                if last_digit is not None:
                    result = "B" if last_digit >= 5 else "S"
                    print(f"🎯 RESULT → {last_digit} | {result}")

                    if minute in ["00", "01", "02"]:
                        # ✅ Cycle အသစ် စတဲ့အချိန် clear လုပ်
                        if minute == "00" and last_processed_minute != "00":
                            cycle_results = []
                            print("🔄 Cycle Reset at minute 00")

                        last_processed_minute = minute
                        cycle_results.append(result)

                        if minute == "02" and len(cycle_results) >= 3:
                            cycle_str = "".join(cycle_results[-3:])
                            print(f"   012 Cycle: {cycle_str}")

                            if cycle_str == "BBB":
                                cycle_history.append("BBB")
                                # ✅ Exactly 4 ကြိမ်မှ alert
                                if len(cycle_history) == 4:
                                    alert = f"""
🔥 <b>6LOTTERY BIG ALERT</b> 🔥
🕒 အချိန်: {now.strftime('%Y-%m-%d %H:%M:%S')}
📊 012 Cycle: <b>BBBB</b> (4 ခါ ဆက်တိုက်)
⚠️ သတိထားပါ!
                                    """
                                    await bot.send_message(
                                        chat_id=CHAT_ID,
                                        text=alert,
                                        parse_mode=ParseMode.HTML
                                    )
                                    print("✅ ALERT SENT!")
                                    cycle_history.clear()  # ✅ Alert ပို့ပြီး reset
                            else:
                                cycle_history.clear()

                            cycle_results = []  # ✅ Cycle ပြီးရင် clear

        await asyncio.sleep(0.2)
