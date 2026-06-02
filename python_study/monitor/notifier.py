import requests


BOT_TOKEN = "8861495057:AAHft2PCpdZjhgj19GpSGazTt0ysQEToVHs"
CHAT_ID = "952886910"

def send_message(listings):
    for item in listings:
        text = f"🏠 {item['title']}\n💰 {item['price']}\n🔗 {item['link']}"
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text}
        )