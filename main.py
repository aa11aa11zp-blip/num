import requests
import time
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ---------------- CONFIG ----------------
API_URL = "http://147.135.212.197/crapi/st/viewstats"  # ستاسو API
API_TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="

TELEGRAM_BOT_TOKEN = "8604072281:AAGvz-xBuV9_Fljc2ceD7GbfoP0tHXx0Zvo"
TELEGRAM_GROUP_ID = -5154192080  # ستاسو ټیلیګرام چټ / ګروپ

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# ---------------- HELPERS ----------------
def escape_markdown(text):
    """Escape special MarkdownV2 characters"""
    chars = r'_*[]()~`>#+-=|{}.!'
    return ''.join(['\\' + c if c in chars else c for c in str(text)])

def fetch_numbers():
    """Fetch new numbers from API"""
    try:
        res = requests.get(API_URL, params={"token": API_TOKEN}, timeout=20)
        res.raise_for_status()
        data = res.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print("API ERROR:", e)
        return []

def parse_time(timestr):
    """Parse timestamp string"""
    try:
        return datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    except:
        return None

# ---------------- MAIN LOOP ----------------
last_seen_time = None
print("🚀 Number Forwarder Started...")

while True:
    entries = fetch_numbers()

    if not entries:
        time.sleep(30)
        continue

    new_entries = []

    if last_seen_time is None:
        new_entries = entries[:5]  # first batch on start
        if new_entries:
            last_seen_time = parse_time(new_entries[0][3])
    else:
        for entry in entries:
            ts = parse_time(entry[3])
            if ts and ts > last_seen_time:
                new_entries.append(entry)

    if new_entries:
        last_seen_time = parse_time(new_entries[0][3])

    for entry in new_entries[::-1]:
        try:
            service_name = entry[0]
            phone_number = entry[1]
            timestamp = entry[3]

            # Mask number if you want, or leave full
            masked_number = phone_number[:5] + "**" + phone_number[-4:] if len(phone_number) >= 10 else phone_number

            message_text = f"""📱 *New Number Found*

⏰ Time: {escape_markdown(timestamp)}
🌐 Service: {escape_markdown(service_name)}
📞 Number: `{escape_markdown(masked_number)}`

─────────────────"""

            # Inline button for your channel
            keyboard = [[InlineKeyboardButton("📢 Join Channel", url="https://t.me/ProTech43")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send message
            bot.send_message(
                chat_id=TELEGRAM_GROUP_ID,
                text=message_text,
                parse_mode="MarkdownV2",
                reply_markup=reply_markup
            )
            print("✅ Sent:", phone_number)

        except Exception as e:
            print("SEND ERROR:", e)

    time.sleep(30) 
