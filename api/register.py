from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

TOKEN = os.environ.get("BOT_TOKEN", "")
SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
APP = os.environ.get("MINI_APP_URL", "")

def api(method, payload):
    req = urllib.request.Request(
        "https://api.telegram.org/bot" + TOKEN + "/" + method,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

class Register(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if not TOKEN:
                raise RuntimeError("BOT_TOKEN missing in Vercel Environment Variables")
            if not APP:
                raise RuntimeError("MINI_APP_URL missing in Vercel Environment Variables")
            webhook_url = APP.rsplit("/miniapp/", 1)[0] + "/api/webhook"
            webhook = api("setWebhook", {
                "url": webhook_url,
                "secret_token": SECRET,
                "allowed_updates": ["message"]
            })
            commands = api("setMyCommands", {"commands": [
                {"command": "start", "description": "Open School"},
                {"command": "game", "description": "Launch School Mini App"},
                {"command": "help", "description": "Show help"}
            ]})
            menu = api("setChatMenuButton", {"menu_button": {
                "type": "web_app",
                "text": "Open School",
                "web_app": {"url": APP}
            }})
            body = json.dumps({
                "ok": True,
                "webhook": webhook.get("ok"),
                "commands": commands.get("ok"),
                "menu": menu.get("ok"),
                "message": "School bot registered. Open Telegram and send /start."
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

handler = Register
