from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import random
import re

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = "あなたのアクセストークン"
LINE_CHANNEL_SECRET = "あなたのシークレット"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def roll_dice(text):
    match = re.match(r"(\d+)d(\d+)", text)
    if not match:
        return None

    count = int(match.group(1))
    sides = int(match.group(2))

    rolls = [random.randint(1, sides) for _ in range(count)]
    total = sum(rolls)

    return f"{text} → {rolls} = {total}"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    result = roll_dice(text)

    if result:
        reply = result
    else:
        reply = "例: 2d6 のように入力してね"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
