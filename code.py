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

import re
import random

def roll_dice(text):
    # 成功判定 1d100<=50 のような形式
    match_check = re.match(r"1d(\d+)<=(\d+)", text)
    if match_check:
        men = int(match_check.group(1))
        atai = int(match_check.group(2))

        deme = random.randint(1, men)
        if deme <= atai:
            return f"{deme} → 成功"
        else:
            return f"{deme} → 失敗"

    # 通常のダイス XdY
    match_normal = re.match(r"(\d+)d(\d+)", text)
    if match_normal:
        kosu = int(match_normal.group(1))
        men = int(match_normal.group(2))

        results = []
        for _ in range(kosu):
            results.append(random.randint(1, men))

        total = sum(results)
        return f"{text} → {results} = {total}"

    # どれにも当てはまらない → 無視
    return None

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
#ここ大事！！！
def handle_message(event):
    text = event.message.text

    # make 
    if text == "make":
        status = make_status()
        reply = "\n".join([f"{k}: {v}" for k, v in status.items()])
        
    elif text == "コマンド":
        reply = command_list()

    # 技能ロール（例：目星.75）
    elif skill_check(text):
        reply = skill_check(text)
    
    # 対抗ロール（例：対抗60→40）
    elif tai_kou(text):
        reply = tai_kou(text)
        
    # 一時的狂気
    elif ichiji_kyouki(text):
        reply = ichiji_kyouki(text)
        
    # 不定の狂気
    elif futei_kyouki(text):
        reply = futei_kyouki(text)     
        
    # ダイスロール（例：3d6, 1d100<=50）
    elif roll_dice(text):
        reply = roll_dice(text)

    # それ以外は無視
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
    
    # --- MOV 計算 --- 
    if status["DEX"] < status["SIZ"] and status["STR"] < status["SIZ"]:
        status["MOV"] = 7 
    elif status["DEX"] < status["SIZ"] or status["STR"] < status["SIZ"]:
        status["MOV"] = 8 
    elif status["DEX"] > status["SIZ"] and status["STR"] > status["SIZ"]:
        status["MOV"] = 9 
    else: status["MOV"] = 8
    # 念のための保険（通常ここには来ない）
    return status
    
#技能ロール
def skill_check(text):
    match = re.match(r"(.+)\.(\d+)", text)
    if not match:
        return None

    name = match.group(1)
    skill = int(match.group(2))
    roll = random.randint(1, 100)

    # クリティカル
    if roll <= 5:
        return f"{name} {roll} → クリティカル"

    # ファンブル
    if roll >= 96:
        return f"{name} {roll} → ファンブル"

    # 成功段階
    if roll <= skill / 5:
        return f"{name} {roll} → イクストリーム成功"
    elif roll <= skill / 2:
        return f"{name} {roll} → ハード成功"
    elif roll <= skill:
        return f"{name} {roll} → 成功"
    else:
        return f"{name} {roll} → 失敗"
        
def tai_kou(text):
    match = re.match(r"対抗(\d+)→(\d+)", text)
    if not match:
        return None

    me = int(match.group(1))
    you = int(match.group(2))

    atai = 50 + (me - you)

    # 結果メッセージをまとめる
    msg = f"対抗 {me} → {you}\n成功率：{atai}%\n"

    if atai <= 0:
        msg += "結果：強制失敗"
        return msg

    elif atai >= 100:
        msg += "結果：確定成功"
        return msg

    else:
        deme = random.randint(1, 100)
        msg += f"出目：{deme}\n"

        if atai < deme:
            msg += "結果：失敗"
        else:
            msg += "結果：成功"

        return msg

def ichiji_kyouki(text):
    if not re.match(r"一時的狂気", text):
        return None

    hyou = [
        "気絶or金切り声","オウム返しor多弁症","健忘症",
        "殺人癖or自殺癖","幻覚or妄想or難聴","過信","逃亡癖or自己愛",
        "不信","偏執病or偏食症","体調不良"
    ]

    deme = random.randint(1, 10)
    time = random.randint(1, 6) * 10 + 30
    turn = random.randint(1, 10) + 4

    msg = f"一時的狂気\n持続：{time}分 or {turn}ラウンド\n症状：{hyou[deme-1]}"
    return msg


def futei_kyouki(text):
    if not re.match(r"不定の狂気", text):
        return None

    hyou2 = [
        "失語症","奇妙な性的趣向","○○恐怖症",
        "幼児退行","依存","心因性難聴","手or脚の機能障害",
        "強迫観念に迫られる","人格改変","記憶改変"
    ]

    deme = random.randint(1, 10)
    day = random.randint(1, 10) + 3

    msg = f"不定の狂気\n持続：{day}日\n症状：{hyou2[deme-1]}"
    return msg
#コマンド表
def command_list():
    return (
        "📘 使用できるコマンド一覧\n"
        "\n"
        "● 能力値生成\n"
        "　make\n"
        "\n"
        "● 技能ロール\n"
        "（技能名.値）\n"
        "\n"
        "● 対抗ロール\n"
        "　対抗○○→○○\n"
        "\n"
        "● ダイスロール\n"
        "　3d6 / 1d100<=50\n"
        "\n"
        "● 狂気表\n"
        "　一時的狂気\n"
        "　不定の狂気\n"
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)















