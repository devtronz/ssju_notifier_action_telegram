import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://www.ssju.ac.in/news-events"
STATE_FILE = "state.json"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return []

def save_state(data):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def fetch_news():
    r = requests.get(URL, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    news = []
    for item in soup.select("div.views-row"):
        title = item.get_text(strip=True)
        if title:
            news.append(title)
    return news

def main():
    old_news = load_state()
    new_news = fetch_news()

    fresh = [n for n in new_news if n not in old_news]

    if fresh:
        for n in fresh[:5]:
            send_telegram(f"📰 <b>SSJU Update</b>\n\n{n}")
        save_state(new_news)
    else:
        print("No new updates")

if __name__ == "__main__":
    main()