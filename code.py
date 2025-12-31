from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import random
import re

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = "YPCr7MhEn4lkeCTxzLIgMXoxxhXXkbWhw1QCZxpgetK/eJ+gU0GZjeY7cm3n2+fBSNt4UgxsqPeSdQxzmZ2lmHDSOc/IxUuaM7qVd540UHlmxRKtUopqRb7fJ9JExEFvAeNOBCt/DmGkJC+UEMEz1AdB04t89/1O/w1cDnyilFU="
LINE_CHANNEL_SECRET = "ba155109a9953d89484e46461c8c2df3"

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

    # make コマンド
    if text == "make":
        status = make_status()
        reply = "\n".join([f"{k}: {v}" for k, v in status.items()])

    # ダイス
    elif roll_dice(text):
        reply = roll_dice(text)

    # それ以外は無返信
    else:
        return

    # LINE に返す
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


def make_status():
    status = {
        "STR": 0, "SIZ": 0, "CON": 0, "DEX": 0,
        "APP": 0, "POW": 0, "INT": 0, "EDU": 0,
        "IDEA": 0, "LUCK": 0, "MOV": 0
    }

    # STR
    for _ in range(3):
        status["STR"] += random.randint(1, 6)
    status["STR"] *= 5

    # SIZ
    for _ in range(2):
        status["SIZ"] += random.randint(1, 6)
    status["SIZ"] = (status["SIZ"] + 6) * 5

    # CON
    for _ in range(3):
        status["CON"] += random.randint(1, 6)
    status["CON"] *= 5

    # DEX
    for _ in range(3):
        status["DEX"] += random.randint(1, 6)
    status["DEX"] *= 5

    # APP
    for _ in range(3):
        status["APP"] += random.randint(1, 6)
    status["APP"] *= 5

    # POW
    for _ in range(3):
        status["POW"] += random.randint(1, 6)
    status["POW"] *= 5

    # INT
    for _ in range(2):
        status["INT"] += random.randint(1, 6)
    status["INT"] = (status["INT"] + 6) * 5

    # IDEA
    status["IDEA"] = status["INT"]

    # EDU
    for _ in range(2):
        status["EDU"] += random.randint(1, 6)
    status["EDU"] = (status["EDU"] + 6) * 5

    # LUCK
    for _ in range(3):
        status["LUCK"] += random.randint(1, 6)
    status["LUCK"] *= 5

    return status

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




