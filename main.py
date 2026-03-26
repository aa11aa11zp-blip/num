import requests
import time
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ---------------- CONFIG ----------------
API_URL = "http://147.135.212.197/crapi/st/viewstats"
TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="
params = {"token": TOKEN}

TELEGRAM_BOT_TOKEN = "8281944831:AAGrz2zrLVLwdDd2BKISYUndRnD6yLn8pEE"
TELEGRAM_GROUP_ID = -1003819384817

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# ---------------- ESCAPE ----------------
def escape_v2(text):
    chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in chars else c for c in str(text)])

# ---------------- FETCH ----------------
def fetch_sms():
    try:
        res = requests.get(API_URL, params=params, timeout=20)
        data = res.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print("API ERROR:", e)
        return []

# ---------------- TIME ----------------
def parse_time(t):
    try:
        return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
    except:
        return None

# ---------------- START ----------------
last_seen = None
print("🚀 Number Forwarder Started...")

while True:
    data = fetch_sms()

    if not data:
        time.sleep(30)
        continue

    new = []

    if last_seen is None:
        new = data[:5]  # first few entries if starting
        if new:
            last_seen = parse_time(new[0][3])
    else:
        for i in data:
            t = parse_time(i[3])
            if t and t > last_seen:
                new.append(i)

    if new:
        last_seen = parse_time(new[0][3])

    for entry in new[::-1]:
        try:
            app = entry[0]
            phone = entry[1]
            time_str = entry[3]

            # mask number if needed
            masked = phone[:5] + "**" + phone[-4:]

            text = f"""📱 *New Number Found*

⏰ Time: {escape_v2(time_str)}
🌐 Service: {escape_v2(app)}
📞 Number: `{escape_v2(masked)}`

──────────────"""

            keyboard = [
                [InlineKeyboardButton("📢 Join Channel", url="https://t.me/ProTech43")]
            ]

            bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=text,
                parse_mode="MarkdownV2",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

            print("✅ Sent Number:", phone)

        except Exception as e:
            print("SEND ERROR:", e)

    time.sleep(30) 
