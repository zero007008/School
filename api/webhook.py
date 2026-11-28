from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.request

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "")

def telegram(method, payload):
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is not configured")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=8) as response:
        return json.loads(response.read().decode())

def send_message(chat_id, message, app=False):
    payload = {"chat_id":chat_id,"text":message}
    if app and MINI_APP_URL:
        payload["reply_markup"]={"inline_keyboard":[[{"text":"🎮 Open School Mini App","web_app":{"url":MINI_APP_URL}}]]}
    telegram("sendMessage", payload)

class TelegramWebhook(BaseHTTPRequestHandler):
    def do_POST(self):
        if WEBHOOK_SECRET and self.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            self.send_response(403); self.end_headers(); return
        try:
            update=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}")
            msg=update.get("message") or {}
            chat_id=(msg.get("chat") or {}).get("id")
            command=(msg.get("text") or "").strip()
            if chat_id and command:
                if command.startswith("/start"):
                    send_message(chat_id,"🏫 Welcome to School!\nOpen the 3D School Mini App below.",True)
                elif command.startswith(("/game","/app")):
                    send_message(chat_id,"🎮 Launch School:",True)
                elif command.startswith("/help"):
                    send_message(chat_id,"/start — Open School\n/game — Launch the Mini App\n/help — Help")
                else:
                    send_message(chat_id,"Use /game to open School.")
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b'{"ok":true}')
        except Exception:
            self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b'{"ok":true}')
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b'{"ok":true,"service":"School Telegram Bot"}')

handler = TelegramWebhook
