import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.ssju.ac.in/news-events"
STATE_FILE = "last_seen.json"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram(text):
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        api,
        data={
            "chat_id": CHAT_ID,
            "text": text,
            "disable_web_page_preview": True
        },
        timeout=20
    )

def load_seen():
    if not os.path.exists(STATE_FILE):
        return []
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_seen(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def check_ssju():
    r = requests.get(URL, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")

    items = soup.select(".view-content .views-row")
    seen = load_seen()
    new_items = []

    for item in items:
        a = item.find("a")
        if not a:
            continue

        title = a.get_text(strip=True)
        href = a.get("href")
        link = href if href.startswith("http") else "https://www.ssju.ac.in" + href

        key = title + link
        if key not in seen:
            new_items.append((title, link))
            seen.append(key)

    if new_items:
        msg = "🆕 SSJU New Notification(s)\n\n"
        for t, l in new_items:
            msg += f"• {t}\n{l}\n\n"

        send_telegram(msg)
        save_seen(seen)

if __name__ == "__main__":
    check_ssju()
