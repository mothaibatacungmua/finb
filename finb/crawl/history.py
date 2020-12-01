import requests
import pandas as pd
from datetime import datetime, timedelta
import json
import math

HISTORY_API = "https://api.vietstock.vn/ta/history"


def generate_payload(symbol, _from, to, resolution="D"):
    return (("symbol", symbol),("from", str(int(_from))),("to", str(int(to))),("resolution", resolution))


def get_history_price(symbol, _from, to, resolution="D"):
    headers = {
      'Connection': 'keep-alive',
      'Accept': '*/*',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
      'Content-Type': 'text/plain',
      'Origin': 'https://ta.vietstock.vn',
      'Sec-Fetch-Site': 'same-site',
      'Sec-Fetch-Mode': 'cors',
      'Sec-Fetch-Dest': 'empty',
      'Accept-Language': 'en-US,en;q=0.9'
    }
    payload = generate_payload(symbol, _from, to, resolution="D")
    r = requests.get(HISTORY_API, params=payload, headers=headers)
    
    history_dict = json.loads(json.loads(r.text))

    if resolution == "D":
        offset = timedelta(hours=7)
    if resolution == "60":
        offset = timedelta(hours=8)
    if resolution == "120":
        offset = timedelta(hours=9)

    df = pd.DataFrame(columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])

    ts = history_dict['t']
    os = history_dict['o']
    hs = history_dict['h']
    ls = history_dict['l']
    cs = history_dict['c']
    vs = history_dict['v']

    for t,o,h,l,c,v in reversed(list(zip(ts, os, hs, ls, cs, vs))):
        t = pd.Timestamp(datetime.fromtimestamp(t)-offset)
        if symbol not in {"VNINDEX", "VN30"}:
            o = round(o/1000, 2)
            h = round(h/1000, 2)
            l = round(l/1000, 2)
            c = round(c/1000, 2)
        else:
            o = round(o, 2)
            h = round(h, 2)
            l = round(l, 2)
            c = round(c, 2)

        row = [t, o, h, l, c, v]
        df.loc[-1] = row
        df.index = df.index + 1
        df = df.sort_index()
    df = df.set_index('Date')
    df['Volume'] = df['Volume'].astype(int)
    return df

from finb.utils.date import str_to_ts
if __name__ == "__main__":

    start_date = "2008-01-01"

    end_date = datetime.now().strftime("%Y-%m-%d")
    df = get_history_price(
        "SAM",
        _from=str_to_ts(start_date),
        to=str_to_ts(end_date))

    print(df.head())