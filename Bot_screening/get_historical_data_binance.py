from binance import Client
from urllib.parse import urljoin, urlencode
import api_keys
import pandas as pd

#crea storico con le chiusure, volatilità, correlazione, high e lows

list_symbols = []
client = Client(api_keys.API_KEY, api_keys.SECRET)
exchange_info = client.get_exchange_info()
for s in exchange_info['symbols']:
    if(s["quoteAsset"] == 'BTC'):
        list_symbols.append(s['symbol'])

klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Jan, 2022")  #"1 Dec, 2017", "1 Jan, 2018" per un intervallo
df_klines = pd.DataFrame(klines)
df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time', 'trash1', 'trash2', 'trash3', 'trash4', 'trash5']
df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit = 'ms').dt.date
df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit = 'ms').dt.date
df_klines['Volatility'] = (df_klines['High price'] - df_klines['Low price']) / df_klines['Low price']
df_klines['24h change'] = (df_klines['Close price'] - df_klines['Open price']) / df_klines['Open price']
df_klines['Correlation'] = df_klines['24h change'] / df_klines['24h change']
df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis = 1, inplace = True)
df_principale_highs = df_klines[['Close time', 'High price']]
df_principale_lows = df_klines[['Close time', 'Low price']]
df_principale_closes = df_klines[['Close time', 'Close price']]
df_principale_volatility = df_klines[['Close time', 'Volatility']]
df_principale_correlation = df_klines[['Close time', 'Correlation']]
df_principale_highs.columns = ['Close time', 'BTCUSD']
df_principale_lows.columns = ['Close time', 'BTCUSD']
df_principale_closes.columns = ['Close time', 'BTCUSD']
df_principale_volatility.columns = ['Close time', 'BTCUSD']
df_principale_correlation.columns = ['Close time', 'BTCUSD']

for coin in list_symbols:
    print(coin)
    klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1DAY, "1 Jan, 2022")  
    df_klines = pd.DataFrame(klines)
    if(len(df_klines.columns) == 12):
        df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time', 'trash1', 'trash2', 'trash3', 'trash4', 'trash5']
        df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit = 'ms').dt.date
        df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit = 'ms').dt.date
        df_klines['Volatility'] = (df_klines['High price'] - df_klines['Low price']) / df_klines['Low price']
        df_klines['Correlation'] = df_klines['24h change'] / df_principale_closes['BTCUSD']
        df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis = 1, inplace = True)
        df_highs = df_klines[['Close time', 'High price']]
        df_lows = df_klines[['Close time', 'Low price']]
        df_closes = df_klines[['Close time', 'Close price']]
        df_volatility = df_klines[['Close time', 'Volatility']]
        df_correlation = df_klines[['Close time', 'Correlation']]
        df_highs.columns = ['Close time', coin]
        df_lows.columns = ['Close time', coin]
        df_closes.columns = ['Close time', coin]
        df_volatility.columns = ['Close time', coin]
        df_correlation.columns = ['Close time', coin]
        df_principale_highs = pd.merge(df_principale_highs, df_highs, on = "Close time", how = 'left')
        df_principale_highs = df_principale_highs.copy()
        df_principale_lows = pd.merge(df_principale_lows, df_lows, on = "Close time", how = 'left')
        df_principale_lows = df_principale_lows.copy()
        df_principale_closes = pd.merge(df_principale_closes, df_closes, on = "Close time", how = 'left')
        df_principale_closes = df_principale_closes.copy()
        df_principale_volatility = pd.merge(df_principale_volatility, df_volatility, on = "Close time", how = 'left')
        df_principale_volatility = df_principale_volatility.copy()
        df_principale_correlation = pd.merge(df_principale_correlation, df_correlation, on = "Close time", how = 'left')
        df_principale_correlation = df_principale_correlation.copy()

df_principale_highs.to_excel('highs.xlsx')
df_principale_lows.to_excel('lows.xlsx')
df_principale_closes.to_excel('closes.xlsx')
df_principale_volatility.to_excel('volatility.xlsx')
df_principale_correlation.to_excel('correlation.xlsx')