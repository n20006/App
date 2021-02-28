import os

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (AudioMessage, FollowEvent, ImageMessage,
                            ImageSendMessage, MessageEvent, TextMessage,
                            TextSendMessage)

app = Flask(__name__)

# 環境変数取得

line_bot_api = LineBotApi("YOUR_CHANNEL_ACCESS_TOKEN")
handler = WebhookHandler("YOUR_CHANNEL_SERCRET")
QR_url = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data="


@app.route("/")
def Hello_World():
    return "hello world"


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


@handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="友だち追加ありがとう！\n文字を送るとQRコードを作るよ！！"),
    )


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text_message = event.message.text
    img_message = ImageSendMessage(
        original_content_url=QR_url + text_message,
        preview_image_url=QR_url + text_message,
    )
    line_bot_api.reply_message(event.reply_token, img_message),


@handler.add(MessageEvent, message=(ImageMessage, AudioMessage))
def handle_image_message(event):
    line_bot_api.reply_message(
        event.reply_token, TextSendMessage(event.reply_token, "QRコードを作成できませんでした")
    )


if __name__ == "__main__":
    #    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
