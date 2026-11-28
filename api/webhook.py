from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "")

def tg(method, payload):
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in Vercel environment")
    req = urllib.request.Request(
        "https://api.telegram.org/bot" + BOT_TOKEN + "/" + method,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

def send(chat_id, msg, app=False):
    p = {"chat_id": chat_id, "text": msg}
    if app and MINI_APP_URL:
        p["reply_markup"] = {"inline_keyboard": [[{
            "text": "🎮 Open School Mini App",
            "web_app": {"url": MINI_APP_URL}
        }]]}
    tg("sendMessage", p)

class TelegramWebhook(BaseHTTPRequestHandler):
    def do_POST(self):
        if WEBHOOK_SECRET and self.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            self.send_response(403)
            self.end_headers()
            return
        try:
            update = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))) or b"{}")
            message = update.get("message") or {}
            chat_id = (message.get("chat") or {}).get("id")
            text = (message.get("text") or "").strip()
            if chat_id and text:
                if text.startswith("/start"):
                    send(chat_id, "🏫 Welcome to School!\nOpen the 3D campus using the button below.", True)
                elif text.startswith(("/game", "/app")):
                    send(chat_id, "🎮 Launch School Mini App:", True)
                elif text.startswith("/help"):
                    send(chat_id, "/start — Open School\n/game — Launch Mini App\n/help — Help")
                else:
                    send(chat_id, "Use /game to open School.")
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
        # Use the already-confirmed /api/webhook route for one-step bot setup.
        try:
            if not MINI_APP_URL:
                raise RuntimeError("MINI_APP_URL missing")
            webhook_url = MINI_APP_URL.rsplit("/miniapp/", 1)[0] + "/api/webhook"
            webhook = tg("setWebhook", {
                "url": webhook_url,
                "secret_token": WEBHOOK_SECRET,
                "allowed_updates": ["message"]
            })
            commands = tg("setMyCommands", {"commands": [
                {"command": "start", "description": "Open School"},
                {"command": "game", "description": "Launch School Mini App"},
                {"command": "help", "description": "Show help"}
            ]})
            menu = tg("setChatMenuButton", {"menu_button": {
                "type": "web_app", "text": "Open School",
                "web_app": {"url": MINI_APP_URL}
            }})
            body = json.dumps({
                "ok": True, "webhook": webhook.get("ok"),
                "commands": commands.get("ok"), "menu": menu.get("ok"),
                "service": "School Telegram Bot configured"
            }).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            body = json.dumps({"ok": False, "error": str(e)}).encode()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

handler = TelegramWebhook
