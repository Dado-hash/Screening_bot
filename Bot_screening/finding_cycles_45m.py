from binance import Client
from urllib.parse import urljoin, urlencode
import api_keys
import pandas as pd
import colorama
import numpy as np

client = Client(api_keys.API_KEY, api_keys.SECRET)
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Sep, 2022")
klines = pd.DataFrame(klines)
klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time', 'Trash', 'Trades', 'Trash2', 'Trash3', 'Trash4']
klines.drop(['Trash', 'Trash2', 'Trash3', 'Trash4'], axis = 1, inplace = True)
klines['Open time'] = klines['Open time'].astype(float)
klines['Open time'] = klines['Open time']*1000000 
klines['Open time'] = pd.to_datetime(klines['Open time'])
klines['Close time'] = klines['Close time'].astype(float)
klines['Close time'] = klines['Close time']*1000000 
klines['Close time'] = pd.to_datetime(klines['Close time'])

print(klines)