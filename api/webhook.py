from http.server import BaseHTTPRequestHandler
import json, os, urllib.request

BOT_TOKEN=os.environ.get("BOT_TOKEN","")
WEBHOOK_SECRET=os.environ.get("TELEGRAM_WEBHOOK_SECRET","")
MINI_APP_URL=os.environ.get("MINI_APP_URL","")

def tg(method,payload):
    if not BOT_TOKEN: raise RuntimeError("BOT_TOKEN missing")
    req=urllib.request.Request("https://api.telegram.org/bot"+BOT_TOKEN+"/"+method,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=10) as r: return json.loads(r.read().decode())

def send(chat_id,msg,app=False):
    p={"chat_id":chat_id,"text":msg}
    if app and MINI_APP_URL:p["reply_markup"]={"inline_keyboard":[[{"text":"🎮 Open School Mini App","web_app":{"url":MINI_APP_URL}}]]}
    tg("sendMessage",p)

class TelegramWebhook(BaseHTTPRequestHandler):
    def do_POST(self):
        if WEBHOOK_SECRET and self.headers.get("X-Telegram-Bot-Api-Secret-Token")!=WEBHOOK_SECRET:
            self.send_response(403);self.end_headers();return
        try:
            u=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))) or b"{}")
            m=u.get("message") or {}; cid=(m.get("chat") or {}).get("id"); t=(m.get("text") or "").strip()
            if cid and t:
                if t.startswith("/start"):send(cid,"🏫 Welcome to School!\nOpen the 3D campus using the button below.",True)
                elif t.startswith(("/game","/app")):send(cid,"🎮 Launch School Mini App:",True)
                elif t.startswith("/help"):send(cid,"/start — Open School\n/game — Launch Mini App\n/help — Help")
                else:send(cid,"Use /game to open School.")
            self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(b'{"ok":true}')
        except Exception:
            self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(b'{"ok":true}')
    def do_GET(self):
        self.send_response(200);self.send_header("Content-Type","application/json");self.end_headers();self.wfile.write(b'{"ok":true,"service":"School Telegram Bot"}')

handler=TelegramWebhook
