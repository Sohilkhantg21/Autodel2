from flask import Flask, request
import requests, json, time
from threading import Thread

app = Flask(__name__)

BOT_TOKEN = "7742062959:AAHSV3_CkV7qHKgJr0iFuNPoTbTck8OlnmE"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
ADMIN_ID = "6411315434"  # Replace with your Telegram numeric ID

# Home route for webhook check
@app.route("/", methods=["GET"])
def home():
    return "Bot Running."

# Telegram webhook
@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        message = data["message"]
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        text = message.get("text", "")
        msg_id = message["message_id"]

        # Log & notify admin if new user
        log_new_user(user_id)

        # Admin commands
        if str(user_id) == str(ADMIN_ID):
            if text.startswith("/broadcast "):
                send_broadcast(text.split(" ", 1)[1])
            elif text == "/admin":
                send_admin_panel(chat_id)
        else:
            # Auto delete for regular user messages
            Thread(target=delete_after, args=(chat_id, msg_id, 10)).start()

    return "ok"

def delete_after(chat_id, msg_id, delay):
    time.sleep(delay)
    requests.post(f"{API_URL}/deleteMessage", json={"chat_id": chat_id, "message_id": msg_id})

def log_new_user(uid):
    try:
        with open("users.json", "r+") as f:
            users = json.load(f)
            if uid not in users:
                users.append(uid)
                f.seek(0)
                json.dump(users, f)
                f.truncate()
                requests.post(f"{API_URL}/sendMessage", json={"chat_id": ADMIN_ID, "text": f"New user joined: {uid}"})
    except:
        with open("users.json", "w") as f:
            json.dump([uid], f)

def send_broadcast(msg):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
            for uid in users:
                requests.post(f"{API_URL}/sendMessage", json={"chat_id": uid, "text": msg})
    except:
        pass

def send_admin_panel(chat_id):
    text = "Admin Panel:\n\n/broadcast <msg> - Send message to all users\n/admin - Show this panel"
    requests.post(f"{API_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

