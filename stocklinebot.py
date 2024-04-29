# -*- coding: utf-8 -*-
"""StockLinebot.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1CmFaRvK1owOvmYfQbOajj6fvy35a-ZEz
"""
#pip install yfinance
#!pip install flask pyngrok flask-ngrok
#!pip install line-bot-sdk

#!ngrok authtoken 2fBIuRa6RZxUgFJF032HEXCYbES_4Kn5KsS5WbTUwZwzCkJvL #你自己的ngrok Token
#./ngrok authtoken 2fBIuRa6RZxUgFJF032HEXCYbES_4Kn5KsS5WbTUwZwzCkJvL
#StockBot_01
Line_Channel_Access_Token='YJIsZbfckdYHnzRky18KwXsUTG6BpuoW2CbTmMbN8d0mjOZVAgilQfzWjTn4jdfAc+gd1yYy1LKbfubnEYDB0phYOZdq93gjAfPanniTJSC29B/R9Gu9XuadTO+aT3KmZ/onslv+dirMClU72klXBgdB04t89/1O/w1cDnyilFU='
Line_Channel_Secret='d305cbeb1f356533d1db5ce07081cf27'

from flask import Flask, request, abort
from pyngrok import ngrok
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
import time
import threading
import yfinance as yf
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt

# 獲取股票數據
stock_symbol = 'AAPL'  # 這裡以蘋果公司為例
stock_symbol = '2645.TW'
start_date = '2023-04-11'
end_date = '2024-04-11'
#data = yf.download(stock_symbol, start=start_date, end=end_date)
data = yf.download(stock_symbol,period='5mo',interval='1d')

app = Flask(__name__)

ngrok_url=''
#自動更新WebhookURL
def auto_update_webhook_url():
  while(1):
    time.sleep(5) #等候5秒讓ngrok完成註冊新網址
    try:
      import json
      import requests
      #取得ngrok最新產生的url
      self_url = "http://localhost:4040/api/tunnels"
      res = requests.get(self_url)
      res_unicode = res.content.decode("utf-8")
      res_json = json.loads(res_unicode)
      ngrok_url = res_json["tunnels"][0]["public_url"]

      #開始更新
      line_put_endpoint_url = "https://api.line.me/v2/bot/channel/webhook/endpoint"
      data = {"endpoint": ngrok_url + '/callback'}
      headers = {
        "Authorization": "Bearer " + Line_Channel_Access_Token ,
        "Content-Type": "application/json"
      }
      print(data)
      res = requests.put(line_put_endpoint_url, headers=headers, json=data)
      # 檢查回應狀態碼
      if res.status_code == 200:
        print("WebhookURL更新成功！")
        break
        #強制關閉threading
        x._stop()
      else:
        print("WebhookURL更新失敗")
    except:
      pass
      #強制關閉threading
      break
      x._stop()

line_bot_api = LineBotApi(Line_Channel_Access_Token)
handler = WebhookHandler(Line_Channel_Secret)
#要在Webhook URL最後加上/callback
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        number = int(event.message.text)
        if len(event.message.text)==4:
          user_input = event.message.text
          response = stockclose_response(user_input)
        else:
          response = f"輸入的數字 {number} 的平方為 {number**2}"
    except ValueError:
        user_input = event.message.text
        response = generate_response(user_input)
        #response = "請輸入一個有效的數字。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )
'''
def handle_message(event):
    user_input = event.message.text
    response = generate_response(user_input)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=response)
    )
'''
def generate_response(user_input):
    # 在這裡實現你的回應邏輯
    # 這只是一個簡單的範例，你可以根據需要進行修改
    if user_input == "你好":
        return "你好！！！"
    elif user_input == "再見":
        return "再見！！！"
    else:
        #return "抱歉，我不太明白你說的是什麼。"
        return user_input
def stockclose_response(user_input):
    stock_symbol = user_input+'.TW'
    data = yf.download(stock_symbol,period='1d')
    todayPriceC=data['Close'].values[0]
    print(todayPriceC)
    return todayPriceC

if __name__ == "__main__":
  #public_url = ngrok.connect(5000, bind_tls=True)
  #print("Tracking URL:", public_url)
  #x = threading.Thread(target=auto_update_webhook_url)
  #x.start()
  app.run()