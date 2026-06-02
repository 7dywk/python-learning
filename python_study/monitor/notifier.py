import requests


BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_HERE"

def send_message(listings):
    for item in listings:
        text = f"🏠 {item['title']}\n💰 {item['price']}\n🔗 {item['link']}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text}
        )