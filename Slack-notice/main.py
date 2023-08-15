import pandas as pd
import numpy as np
import requests
import yfinance
import json
import slack
from datetime import datetime

### Notice function

def SlackNotice(name):
    stock=name

    ### Set up Slack Workspace Bot client

    slack_token='slack-secret'
    client=slack.WebClient(token=slack_token)
    now = datetime.now()

    ### Use this minute line dataframe if you want to do minute level trades
    
    dscp=yfinance.download(stock,period="1hour",interval = "1m")
    current_price=str(dscp['Close'][-1])
    ds = yfinance.download(stock,period="7d",interval = "1h")
    
    ### Build signals
    
    ema5 = ds["Close"].ewm(span=5, adjust=False, min_periods=5).mean()
    ema15 = ds["Close"].ewm(span=15, adjust=False, min_periods=15).mean()
    k = ds["Close"].ewm(span=12, adjust=False, min_periods=12).mean()
    d = ds["Close"].ewm(span=26, adjust=False, min_periods=26).mean()
    macd = k - d
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    macd_h = macd - macd_s

    ### Build Conditions 
    
    if ema5[-3]-ema15[-3]<0 and ema5[-2]-ema15[-2]>0:
        #####################################create_order("SPY", 2490, "buy", "market", "gtc")
        ChannelText='#'+stock+'-hour-line'
        notice=str(now)+'  '+stock+' BUY '+ current_price
        client.chat_postMessage(channel=ChannelText,text=notice)
        
    elif (ema5[-3]-ema15[-3]>0 and ema5[-2]-ema15[-2]<0) or (ema5[-2]-ema15[-2]>0 and macd_h[-2]<0 and macd_h[-3]>0):
        ########################################create_order("SPY", 2490, "sell", "market", "gtc")
        ChannelText='#'+stock+'-hour-line'
        notice=str(now)+'  '+stock+' SELL '+ current_price
        client.chat_postMessage(channel=ChannelText,text=notice)
        
    return {"status code":200}

### Triggered function

def SendNotice(request):
    list=['SPY','QQQ','DIA']
    
    ### Add error handling
    
    try:
        for i in list:
            SlackNotice(i)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
    else:
        message='status code:200'

    return message
   
    
