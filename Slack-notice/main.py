import pandas as pd
import numpy as np
import requests
import yfinance
import json
import slack
from datetime import datetime

now = datetime.now()
dscp=yfinance.download("QQQ",period="1hour",interval = "1m")
current_price=str(dscp['Close'][-1])

ds = yfinance.download("QQQ",period="7d",interval = "1h")

slack_token='xoxp-5130203815986-5142830602273-5115876156183-55f103180df997bac2563377609fa0ff'
client=slack.WebClient(token=slack_token)

def stra(request):

    ema5 = ds["Close"].ewm(span=5, adjust=False, min_periods=5).mean()
    ema15 = ds["Close"].ewm(span=15, adjust=False, min_periods=15).mean()


    k = ds["Close"].ewm(span=12, adjust=False, min_periods=12).mean()
    d = ds["Close"].ewm(span=26, adjust=False, min_periods=26).mean()

    macd = k - d
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    macd_h = macd - macd_s
    if ema5[-3]-ema15[-3]<0 and ema5[-2]-ema15[-2]>0:
        #####################################create_order("SPY", 2490, "buy", "market", "gtc")
        
        notice=str(now)+'  '+'QQQ BUY '+ current_price
        client.chat_postMessage(channel='#qqq-hour-line',text=notice)
        
        
    elif (ema5[-3]-ema15[-3]>0 and ema5[-2]-ema15[-2]<0) or (ema5[-2]-ema15[-2]>0 and macd_h[-2]<0 and macd_h[-3]>0):
        ########################################create_order("SPY", 2490, "sell", "market", "gtc")
        
        notice=str(now)+'  '+'QQQ SELL '+ current_price
        client.chat_postMessage(channel='#qqq-hour-line',text=notice)
        
    return {"status code":200}
