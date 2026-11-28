import json
import os
import urllib.request

token = os.environ["BOT_TOKEN"]
base = os.environ["APP_BASE_URL"].rstrip("/")
secret = os.environ["TELEGRAM_WEBHOOK_SECRET"]

def call(method, payload):
    url = f"https://api.telegram.org/bot{token}/{method}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode())
    if not result.get("ok"):
        raise SystemExit(f"Telegram API error: {result}")
    print(method, "OK")

call("setWebhook", {
    "url": base + "/api/webhook",
    "secret_token": secret,
    "allowed_updates": ["message"]
})
call("setMyCommands", {
    "commands": [
        {"command": "start", "description": "Open School"},
        {"command": "game", "description": "Launch School Mini App"},
        {"command": "help", "description": "Show help"}
    ]
})
call("setChatMenuButton", {
    "menu_button": {
        "type": "web_app",
        "text": "Open School",
        "web_app": {"url": base + "/miniapp/"}
    }
})
print("Bot webhook and Mini App menu are configured.")
