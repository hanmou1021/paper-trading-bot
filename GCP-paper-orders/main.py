import pandas as pd
import numpy as np
import requests
import yfinance
import json

### Basic account info 

API_KEY = "{add_secret}"
SECRET_KEY = "{add_secret}"
BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = BASE_URL + "/v2/account"
ORDERS_URL =  BASE_URL + "/v2/orders"
POSITIONS_URL = BASE_URL + "/v2/positions"
account = requests.get(ACCOUNT_URL, headers = {"APCA-API-KEY-ID": API_KEY, 
                                               "APCA-API-SECRET-KEY":  SECRET_KEY})
account_info=account.json()

### Interact with alpaca using API to create orders

def create_order(symbol, qty, side, type, time_in_force):
    data = {
            "symbol": symbol,
            "qty": qty,
            "side": side,
            "type": type,
            "time_in_force": time_in_force
            }
    r = requests.post(ORDERS_URL, json=data, headers = {"APCA-API-KEY-ID": API_KEY, 
                                                        "APCA-API-SECRET-KEY":  SECRET_KEY})

    return json.loads(r.content)

### This is the strategy function

def strategy(name):
  
    ### Strategy is mainly using exponential moving average upward break through as BUY, EMA/MACD downward break through as SELL.
    ### Strategy is mainly on hour lines. You could also try minute lines, but note api limitations. 

    stock=name
    ds = yfinance.download(stock,period="7d",interval = "1h")
    dsc = yfinance.download(stock,period="1d",interval = "1m")
    current_price=dsc['Close'][-1]
    equity=float(account_info['cash'])
    buy_amount=round((equity-20000)/current_price)

    ### Get account info
  
    position = requests.get(POSITIONS_URL, headers = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY":  SECRET_KEY})
    sell=position.json()
    if len(sell)>0:
        sell_quantity=sell[0]['qty']
    else:
        sell_quantity='0'
      
    ### Get signals info
  
    ema5 = ds["Close"].ewm(span=5, adjust=False, min_periods=5).mean()
    ema15 = ds["Close"].ewm(span=15, adjust=False, min_periods=15).mean()
    k = ds["Close"].ewm(span=12, adjust=False, min_periods=12).mean()
    d = ds["Close"].ewm(span=26, adjust=False, min_periods=26).mean()
    macd = k - d
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    macd_h = macd - macd_s

    ### Create oders upon signals, note that we want to capture upward trend more securely, so we set two exit conditions
    ### Note all orders are market
  
    if ema5[-3]-ema15[-3]<0 and ema5[-2]-ema15[-2]>0:
        create_order(name, buy_amount, "buy", "market", "gtc")
    elif (ema5[-3]-ema15[-3]>0 and ema5[-2]-ema15[-2]<0) or (ema5[-2]-ema15[-2]>0 and macd_h[-2]<0 and macd_h[-3]>0):
        create_order(name, sell_quantity, "sell", "market", "gtc")
    return {"status code":200}

### This is the triggerly function

def loopStrategy():
    list=['SPY','QQQ','DIA']
    
    ### Add error handling
  
    try:
        for i in list:
            strategy(i)
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
    else:
        message = 'Status code:200'
    
    return message

### Note that until you fill the secrets, there will be errors. Also Note that account status may lead to errors. 
### Note the API has different possibilities to cause errors.


