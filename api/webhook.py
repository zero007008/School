import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "")

def telegram(method, payload):
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))

def send_message(chat_id, text, with_app=False):
    keyboard = None
    if with_app and MINI_APP_URL:
        keyboard = {
            "inline_keyboard": [[
                {"text": "🎮 Open School Mini App", "web_app": {"url": MINI_APP_URL}}
            ]]
        }
    payload = {"chat_id": chat_id, "text": text}
    if keyboard:
        payload["reply_markup"] = keyboard
    return telegram("sendMessage", payload)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if WEBHOOK_SECRET:
            supplied = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
            if supplied != WEBHOOK_SECRET:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"forbidden")
                return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            update = json.loads(self.rfile.read(length) or b"{}")
            message = update.get("message") or update.get("edited_message") or {}
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            text = (message.get("text") or "").strip()
            if chat_id and text:
                if text.startswith("/start"):
                    send_message(
                        chat_id,
                        "🏫 Welcome to School!\n\nOpen the Mini App to explore the 3D school and start playing.",
                        with_app=True
                    )
                elif text.startswith("/game") or text.startswith("/app"):
                    send_message(chat_id, "🎮 Tap below to open School.", with_app=True)
                elif text.startswith("/help"):
                    send_message(chat_id, "/start — Open School\n/game — Launch the Mini App\n/help — Show help")
                else:
                    send_message(chat_id, "Use /game to open the School Mini App.")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
        except Exception:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true,"service":"School Telegram Bot"}')
