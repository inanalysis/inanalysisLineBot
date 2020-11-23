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
    MessageEvent, TextMessage, TextSendMessage, FollowEvent, ImageSendMessage
)

line_bot_api = LineBotApi('tdvAI79PokntER3cHHf/hYXyiBUjh+3xXnN58j8HUI1GvBxZ2Dg08rBekpvTUbind9k+K45I351W4HcIscGl9CJu//BiMY65PbVnFycJyzkX6YTta5FuxFY+tEBAxn1VFmmTnrUZdp6SL7mjF4I03QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('f04e554110231e0e4e14fc88e362421e')

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
        if request.values.get('status') == 'success':
            line_bot_api.push_message(request.values.get('lineID'), TextSendMessage(text='使用資料視覺化模組進行預覽'))
            line_bot_api.push_message(request.values.get('lineID'), ImageSendMessage(original_content_url=f"{request.values.get('imgUrl')}",
            preview_image_url=f"{request.values.get('imgUrl')}"))
            #line_bot_api.push_message(request.values.get('lineID'), TextSendMessage(text=f"{request.values.get('imgUrl')}"))
    return 'success'

@app.route("/test",methods=['POST'])
def test():
    return 'success'

if __name__ == '__main__':
   app.run(host='0.0.0.0', port='8005',ssl_context=('bundle.crt','private.key'))
