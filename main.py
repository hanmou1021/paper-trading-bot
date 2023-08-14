import pandas as pd
import numpy as np
import requests
import yfinance
import json

API_KEY = "PK9I7EVKYN7MD58ODVPP"
SECRET_KEY = "jBHr3rj8cyCAuX2jWUEgUR9HkWvKuj3CQYzmeqf4"
BASE_URL = "https://paper-api.alpaca.markets"
ACCOUNT_URL = BASE_URL + "/v2/account"
ORDERS_URL =  BASE_URL + "/v2/orders"
POSITIONS_URL = BASE_URL + "/v2/positions"


account = requests.get(ACCOUNT_URL, headers = {"APCA-API-KEY-ID": API_KEY, 
                                               "APCA-API-SECRET-KEY":  SECRET_KEY})
account_info=account.json()

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

def stra(request):
    
    ds = yfinance.download("SPY",period="7d",interval = "1h")
    dsc = yfinance.download("SPY",period="1d",interval = "1m")
    current_price=dsc['Close'][-1]
    equity=float(account_info['cash'])
    buy_amount=round((equity-20000)/current_price)
    
    
    position = requests.get(POSITIONS_URL, headers = {"APCA-API-KEY-ID": API_KEY, "APCA-API-SECRET-KEY":  SECRET_KEY})
    sell=position.json()
    if len(sell)>0:
        sell_quantity=sell[0]['qty']
    else:
        sell_quantity='0'

    ema5 = ds["Close"].ewm(span=5, adjust=False, min_periods=5).mean()
    ema15 = ds["Close"].ewm(span=15, adjust=False, min_periods=15).mean()


    k = ds["Close"].ewm(span=12, adjust=False, min_periods=12).mean()
    d = ds["Close"].ewm(span=26, adjust=False, min_periods=26).mean()

    macd = k - d
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    macd_h = macd - macd_s
    if ema5[-3]-ema15[-3]<0 and ema5[-2]-ema15[-2]>0:
        create_order("SPY", buy_amount, "buy", "market", "gtc")
    elif (ema5[-3]-ema15[-3]>0 and ema5[-2]-ema15[-2]<0) or (ema5[-2]-ema15[-2]>0 and macd_h[-2]<0 and macd_h[-3]>0):
        create_order("SPY", sell_quantity, "sell", "market", "gtc")
    return {"status code":200}
