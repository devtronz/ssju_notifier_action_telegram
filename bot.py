import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# ================= CONFIG =================
URL = "https://www.ssju.ac.in/news-events"
STATE_FILE = "state.json"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

# ================= TELEGRAM =================
def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(
        url,
        data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        },
        timeout=20
    )

# ================= STATE =================
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "news": [],
        "last_heartbeat": ""
    }

def save_state(news, heartbeat):
    state = {
        "news": news,
        "last_heartbeat": heartbeat
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ================= SCRAPER =================
def fetch_news():
    r = requests.get(URL, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    news = []

    for a in soup.select("a"):
        text = a.get_text(strip=True)
        href = a.get("href", "")

        if text and "/news" in href.lower():
            if href.startswith("/"):
                href = "https://www.ssju.ac.in" + href
            news.append(f"{text}\n{href}")

    # remove duplicates, keep order
    return list(dict.fromkeys(news))

# ================= MAIN =================
def main():
    state = load_state()
    old_news = state["news"]
    last_heartbeat = state["last_heartbeat"]

    today = datetime.utcnow().strftime("%Y-%m-%d")

    # ---- STARTUP MESSAGE (only first time ever) ----
    if not old_news and not last_heartbeat:
        send_telegram(
            "✅ <b>SSJU News Bot started successfully</b>\n\n"
            "⏰ Monitoring SSJU website for updates."
        )

    # ---- DAILY HEARTBEAT ----
    if last_heartbeat != today:
        send_telegram(
            "❤️ <b>SSJU News Bot heartbeat</b>\n\n"
            "Bot is alive and checking for new updates."
        )
        last_heartbeat = today

    # ---- NEWS CHECK ----
    new_news = fetch_news()
    fresh = [n for n in new_news if n not in old_news]

    if fresh:
        for item in fresh[:5]:  # safety limit
            send_telegram(
                f"📰 <b>SSJU Update</b>\n\n{item}"
            )
        old_news = new_news
    else:
        print("No new updates")

    save_state(old_news, last_heartbeat)

if __name__ == "__main__":
    main()
