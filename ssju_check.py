import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import date, datetime

# ================= CONFIG =================
URL = "https://www.ssju.ac.in/news-events"

STATE_FILE = "last_seen.json"
LOG_FILE = "run_logs.json"
STATS_FILE = "stats.json"

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
# =========================================


# ---------- TELEGRAM ----------
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


# ---------- FILE HELPERS ----------
def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


# ---------- COMMAND HANDLER ----------
def handle_commands():
    """
    Reads last update and responds to commands like /start, /stats
    """
    api = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    r = requests.get(api, timeout=20).json()

    if not r.get("result"):
        return

    last = r["result"][-1]
    msg = last.get("message")
    if not msg:
        return

    text = msg.get("text", "")
    chat_id = msg["chat"]["id"]

    if str(chat_id) != str(CHAT_ID):
        return  # ignore others

    if text == "/start":
        send_telegram(
            "✅ *SSJU Notifier Active*\n\n"
            "Commands:\n"
            "/stats – notification count\n"
            "/last – last run info",
        )

    elif text == "/stats":
        stats = load_json(STATS_FILE, {"total_notifications": 0})
        send_telegram(
            f"📊 *SSJU Stats*\n\n"
            f"Total notifications sent: {stats['total_notifications']}"
        )

    elif text == "/last":
        logs = load_json(LOG_FILE, [])
        if not logs:
            send_telegram("ℹ️ No run history yet.")
        else:
            last_run = logs[-1]
            send_telegram(
                "🕒 *Last Run*\n\n"
                f"Time: {last_run['time']}\n"
                f"New items: {last_run['new_items']}\n"
                f"Status: {last_run['status']}"
            )


# ---------- MAIN CHECK ----------
def check_ssju():
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    today = str(date.today())

    state = load_json(STATE_FILE, {"seen_items": [], "last_heartbeat": None})
    logs = load_json(LOG_FILE, [])
    stats = load_json(STATS_FILE, {"total_notifications": 0})

    # 💓 heartbeat once per day
    if state["last_heartbeat"] != today:
        send_telegram("💓 SSJU notifier is running")
        state["last_heartbeat"] = today

    new_count = 0
    status = "ok"

    try:
        r = requests.get(URL, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")

        items = soup.select(".view-content .views-row")

        new_items = []
        for item in items:
            a = item.find("a")
            if not a:
                continue

            title = a.get_text(strip=True)
            href = a.get("href")
            link = href if href.startswith("http") else "https://www.ssju.ac.in" + href

            key = title + link
            if key not in state["seen_items"]:
                new_items.append((title, link))
                state["seen_items"].append(key)

        if new_items:
            msg = "🆕 *SSJU New Notification(s)*\n\n"
            for t, l in new_items:
                msg += f"• {t}\n{l}\n\n"

            send_telegram(msg)
            new_count = len(new_items)
            stats["total_notifications"] += new_count

    except Exception as e:
        status = "error"
        send_telegram(f"⚠️ SSJU checker error:\n{e}")

    # 📝 log run
    logs.append({
        "time": now,
        "new_items": new_count,
        "status": status
    })

    save_json(STATE_FILE, state)
    save_json(LOG_FILE, logs)
    save_json(STATS_FILE, stats)


# ---------- ENTRY ----------
if __name__ == "__main__":
    handle_commands()
    check_ssju()
