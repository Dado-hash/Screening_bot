from binance import Client
import api_keys
import pandas as pd
import colorama
import numpy as np

#crea storico con le chiusure, volatilità, correlazione, high e lows

def progress_bar(progress, total, color = colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if (progress == total):
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r") 
        print(colorama.Fore.RESET)

list_symbols = []
client = Client(api_keys.API_KEY, api_keys.SECRET)
exchange_info = client.get_exchange_info()
for s in exchange_info['symbols']:
    if(s["quoteAsset"] == 'BTC'):
        list_symbols.append(s['symbol'])

klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 May, 2021")  #"1 Dec, 2017", "1 Jan, 2018" per un intervallo
df_klines = pd.DataFrame(klines)
df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time', 'trash1', 'trash2', 'trash3', 'trash4', 'trash5']

df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit = 'ms').dt.date
df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit = 'ms').dt.date
df_klines['Volatility'] = (df_klines['High price'].astype(float) - df_klines['Low price'].astype(float)) / df_klines['Low price'].astype(float)
df_klines['24h change'] = (df_klines['Close price'].astype(float) - df_klines['Open price'].astype(float)) / df_klines['Open price'].astype(float)
df_klines['SMA6'] = df_klines['Close price'].rolling(6).mean()
df_klines['SMA11'] = df_klines['Close price'].rolling(11).mean()
df_klines['SMA21'] = df_klines['Close price'].rolling(21).mean()
df_klines['Above SMA6'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA6'], 1, 0)
df_klines['Above SMA11'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA11'], 1, 0)
df_klines['Above SMA21'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA21'], 1, 0)
df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis = 1, inplace = True)

df_principale_highs = df_klines[['Close time', 'High price']]
df_principale_lows = df_klines[['Close time', 'Low price']]
df_principale_closes = df_klines[['Close time', 'Close price']]
df_principale_volatility = df_klines[['Close time', 'Volatility']]
df_principale_correlation = df_klines[['Close time', '24h change']]
df_principale_SMA6 = df_klines[['Close time', 'SMA6']]
df_principale_SMA11 = df_klines[['Close time', 'SMA11']]
df_principale_SMA21 = df_klines[['Close time', 'SMA21']]
df_principale_above6 = df_klines[['Close time', 'Above SMA6']]
df_principale_above11 = df_klines[['Close time', 'Above SMA11']]
df_principale_above21 = df_klines[['Close time', 'Above SMA21']]

df_principale_highs.columns = ['Close time', 'BTCUSD']
df_principale_lows.columns = ['Close time', 'BTCUSD']
df_principale_closes.columns = ['Close time', 'BTCUSD']
df_principale_volatility.columns = ['Close time', 'BTCUSD']
df_principale_correlation.columns = ['Close time', 'BTCUSD']
df_principale_SMA6.columns = ['Close time', 'BTCUSD']
df_principale_SMA11.columns = ['Close time', 'BTCUSD']
df_principale_SMA21.columns = ['Close time', 'BTCUSD']
df_principale_above6.columns = ['Close time', 'BTCUSD']
df_principale_above11.columns = ['Close time', 'BTCUSD']
df_principale_above21.columns = ['Close time', 'BTCUSD']

count_bar = 0
for coin in list_symbols:

    klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1DAY, "1 May, 2021")  
    df_klines = pd.DataFrame(klines)
    count_bar += 1

    if(len(df_klines.columns) == 12):
        df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time', 'trash1', 'trash2', 'trash3', 'trash4', 'trash5']
        df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit = 'ms').dt.date
        df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit = 'ms').dt.date
        df_klines['Volatility'] = (df_klines['High price'].astype(float) - df_klines['Low price'].astype(float)) / df_klines['Low price'].astype(float)
        df_klines['24h change'] = (df_klines['Close price'].astype(float) - df_klines['Open price'].astype(float)) / df_klines['Open price'].astype(float)
        df_klines['Correlation'] = df_klines['24h change'].astype(float) / df_principale_correlation['BTCUSD'].astype(float)
        df_klines['SMA6'] = df_klines['Close price'].rolling(6).mean()
        df_klines['SMA11'] = df_klines['Close price'].rolling(11).mean()
        df_klines['SMA21'] = df_klines['Close price'].rolling(21).mean()
        df_klines['Above SMA6'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA6'], 1, 0)
        df_klines['Above SMA11'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA11'], 1, 0)
        df_klines['Above SMA21'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA21'], 1, 0)
        df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis = 1, inplace = True)

        df_highs = df_klines[['Close time', 'High price']]
        df_lows = df_klines[['Close time', 'Low price']]
        df_closes = df_klines[['Close time', 'Close price']]
        df_volatility = df_klines[['Close time', 'Volatility']]
        df_correlation = df_klines[['Close time', 'Correlation']]
        df_SMA6 = df_klines[['Close time', 'SMA6']]
        df_SMA11 = df_klines[['Close time', 'SMA11']]
        df_SMA21 = df_klines[['Close time', 'SMA21']]
        df_above6 = df_klines[['Close time', 'Above SMA6']]
        df_above11 = df_klines[['Close time', 'Above SMA11']]
        df_above21 = df_klines[['Close time', 'Above SMA21']]

        df_highs.columns = ['Close time', coin]
        df_lows.columns = ['Close time', coin]
        df_closes.columns = ['Close time', coin]
        df_volatility.columns = ['Close time', coin]
        df_correlation.columns = ['Close time', coin]
        df_SMA6.columns = ['Close time', coin]
        df_SMA11.columns = ['Close time', coin]
        df_SMA21.columns = ['Close time', coin]
        df_above6.columns = ['Close time', coin]
        df_above11.columns = ['Close time', coin]
        df_above21.columns = ['Close time', coin]

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
        df_principale_SMA6 = pd.merge(df_principale_SMA6, df_SMA6, on = "Close time", how = 'left')
        df_principale_SMA6 = df_principale_SMA6.copy()
        df_principale_SMA11 = pd.merge(df_principale_SMA11, df_SMA11, on = "Close time", how = 'left')
        df_principale_SMA11 = df_principale_SMA11.copy()
        df_principale_SMA21 = pd.merge(df_principale_SMA21, df_SMA21, on = "Close time", how = 'left')
        df_principale_SMA21 = df_principale_SMA21.copy()
        df_principale_above6 = pd.merge(df_principale_above6, df_above6, on = "Close time", how = 'left')
        df_principale_above6 = df_principale_above6.copy()
        df_principale_above11 = pd.merge(df_principale_above11, df_above11, on = "Close time", how = 'left')
        df_principale_above11 = df_principale_above11.copy()
        df_principale_above21 = pd.merge(df_principale_above21, df_above21, on = "Close time", how = 'left')
        df_principale_above21 = df_principale_above21.copy()

        progress_bar(count_bar, len(list_symbols))

df_principale_highs.to_excel('highs.xlsx')
df_principale_lows.to_excel('lows.xlsx')
df_principale_closes.to_excel('closes.xlsx')
df_principale_volatility.to_excel('volatility.xlsx')
df_principale_correlation.to_excel('correlation.xlsx')
df_principale_SMA6.to_excel('SMA6.xlsx')
df_principale_SMA11.to_excel('SMA11.xlsx')
df_principale_SMA21.to_excel('SMA21.xlsx')
df_principale_above6.to_excel('above6.xlsx')
df_principale_above11.to_excel('above11.xlsx')
df_principale_above21.to_excel('above21.xlsx')

#per plottare
#reliance[['Close', 'SMA30']].plot(label='RELIANCE', figsize=(16, 8))