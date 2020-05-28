import os
from flask import Flask, request, abort
from flask_restful import Api
from flask_cors import CORS
from utils import sql
import logging
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent
)

line_bot_api = LineBotApi('2bgWsnCNsHxgZ84kQC8OUY/1Xnw1g3cKM4q8L7bOUqi4a3qgr80p8uY/2C0ynPZ/zbS3+vLpGT3zvNbESL+cQbkTY7vVlygpQ4wa/P6aHIbONoZLrI55oRAB4gftkPKk/rWiag0gGwGRTdJ3xQCulQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fc6da215620b26fb6c6336537233c0b9')

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        db = sql()
        db.cursor.execute(f"select * from user where `user_email`='{event.message.text}'")
        result = db.cursor.fetchone()
        if(result == None):
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="查無此Email, 請重新確認!"))
        else:
            db.cursor.execute(f"update user set `user_line`='{event.source.user_id}' where `user_id`='{result[0]}'")
            db.conn.commit()
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="綁定成功!"))
    except Exception as e:
        db.conn.rollback()

@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.push_message(event.source.user_id, TextSendMessage(text='歡迎加入InAnalysis Line Bot!\n欲使用本系統功能請回覆註冊Email!'))

@app.route("/sendMessage", methods=['POST'])
def submit():
    if request.method == 'POST':
        line_bot_api.push_message(request.values.get('lineID'), TextSendMessage(text=f"您的RPA流程已完成\n狀態: {request.values.get('status')}"))
        return 'success'

if __name__ == '__main__':
   app.run(port=8005)