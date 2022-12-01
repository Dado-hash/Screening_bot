from binance import Client
import api_keys
import pandas as pd
import colorama
import numpy as np
from datetime import timedelta

pd.options.mode.chained_assignment = None


def progress_bar(progress, total, color=colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if progress == total:
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r")
        print(colorama.Fore.RESET)


# getting coins from binance
list_symbols = []
client = Client(api_keys.API_KEY, api_keys.SECRET)
exchange_info = client.get_exchange_info()
for s in exchange_info['symbols']:
    if s["quoteAsset"] == 'BTC':
        list_symbols.append(s['symbol'])

# getting BTC data
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY,
                                      "1 May, 2021")  # "1 Dec, 2017", "1 Jan, 2018" per un intervallo

# reformatting some columns and calculating Volatility and 24h change
df_klines = pd.DataFrame(klines)
df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time',
                     'trash1', 'trash2', 'trash3', 'trash4', 'trash5']

df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit='ms').dt.date
df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit='ms').dt.date
df_klines['Volatility'] = (df_klines['High price'].astype(float) - df_klines['Low price'].astype(float)) / df_klines[
    'Low price'].astype(float)
df_klines['24h change'] = (df_klines['Close price'].astype(float) - df_klines['Open price'].astype(float)) / df_klines[
    'Open price'].astype(float)

# calculating SMAs and if price is over these
df_klines['SMA6'] = df_klines['Close price'].rolling(6).mean()
df_klines['SMA11'] = df_klines['Close price'].rolling(11).mean()
df_klines['SMA21'] = df_klines['Close price'].rolling(21).mean()
df_klines['Above SMA6'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA6'], 1, 0)
df_klines['Above SMA11'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA11'], 1, 0)
df_klines['Above SMA21'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA21'], 1, 0)

df_klines_temp = df_klines[['High price', 'Low price', 'Close time']]

# Tenkan sen
high_9 = df_klines_temp['High price'].rolling(window=9).max()
low_9 = df_klines_temp['Low price'].rolling(window=9).min()
df_klines_temp['tenkan_sen'] = (high_9 + low_9) / 2

# Kijun sen
high_26 = df_klines_temp['High price'].rolling(window=26).max()
low_26 = df_klines_temp['Low price'].rolling(window=26).min()
df_klines_temp['kijun_sen'] = (high_26 + low_26) / 2

# this is to extend the 'df' in future for 26 days
# the 'df' here is numerical indexed df
last_index = df_klines_temp.iloc[-1:].index[0]
last_date = df_klines_temp['Close time'].iloc[-1]
for i in range(26):
    df_klines_temp.loc[last_index + 1 + i, 'Date'] = last_date + timedelta(days=i)

# Senkou span
df_klines_temp['senkou_span_a'] = ((df_klines_temp['tenkan_sen'] + df_klines_temp['kijun_sen']) / 2).shift(26)
high_52 = df_klines_temp['High price'].rolling(window=52).max()
low_52 = df_klines_temp['Low price'].rolling(window=52).min()
df_klines_temp['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

# Chikou span
df_klines_temp['chikou_span'] = df_klines_temp['Close time'].shift(-22)

df_klines_temp_close = df_klines_temp['Close time']
df_klines_temp_data = df_klines_temp['Date']
df_klines_temp_close_result = df_klines_temp_close.combine_first(df_klines_temp_data)

df_klines_temp.drop(['High price', 'Low price', 'Close time', 'Date'], axis=1, inplace=True)
df_klines_temp = pd.concat([df_klines_temp, df_klines_temp_close_result], axis=1)

df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis=1, inplace=True)

# separating the columns to prepare them to be attached to those of the other coins
df_principal_highs = df_klines[['Close time', 'High price']]
df_principal_lows = df_klines[['Close time', 'Low price']]
df_principal_closes = df_klines[['Close time', 'Close price']]
df_principal_volatility = df_klines[['Close time', 'Volatility']]
df_principal_correlation = df_klines[['Close time', '24h change']]
df_principal_SMA6 = df_klines[['Close time', 'SMA6']]
df_principal_SMA11 = df_klines[['Close time', 'SMA11']]
df_principal_SMA21 = df_klines[['Close time', 'SMA21']]
df_principal_above6 = df_klines[['Close time', 'Above SMA6']]
df_principal_above11 = df_klines[['Close time', 'Above SMA11']]
df_principal_above21 = df_klines[['Close time', 'Above SMA21']]
df_principal_tenkan = df_klines_temp[['Close time', 'tenkan_sen']]
df_principal_kijun = df_klines_temp[['Close time', 'kijun_sen']]
df_principal_senkou_a = df_klines_temp[['Close time', 'senkou_span_a']]
df_principal_senkou_b = df_klines_temp[['Close time', 'senkou_span_b']]
df_principal_chikou = df_klines_temp[['Close time', 'chikou_span']]

df_principal_highs.columns = ['Close time', 'BTCUSD']
df_principal_lows.columns = ['Close time', 'BTCUSD']
df_principal_closes.columns = ['Close time', 'BTCUSD']
df_principal_volatility.columns = ['Close time', 'BTCUSD']
df_principal_correlation.columns = ['Close time', 'BTCUSD']
df_principal_SMA6.columns = ['Close time', 'BTCUSD']
df_principal_SMA11.columns = ['Close time', 'BTCUSD']
df_principal_SMA21.columns = ['Close time', 'BTCUSD']
df_principal_above6.columns = ['Close time', 'BTCUSD']
df_principal_above11.columns = ['Close time', 'BTCUSD']
df_principal_above21.columns = ['Close time', 'BTCUSD']
df_principal_tenkan.columns = ['Close time', 'BTCUSD']
df_principal_tenkan = df_principal_tenkan.dropna()
df_principal_kijun.columns = ['Close time', 'BTCUSD']
df_principal_kijun = df_principal_kijun.dropna()
df_principal_senkou_a.columns = ['Close time', 'BTCUSD']
df_principal_senkou_a = df_principal_senkou_a.dropna()
df_principal_senkou_b.columns = ['Close time', 'BTCUSD']
df_principal_senkou_b = df_principal_senkou_b.dropna()
df_principal_chikou.columns = ['Close time', 'BTCUSD']
df_principal_chikou = df_principal_chikou.dropna()

# repeating for all the remaining coins
count_bar = 0
for coin in list_symbols:

    klines = client.get_historical_klines(coin, Client.KLINE_INTERVAL_1DAY, "1 May, 2021")
    df_klines = pd.DataFrame(klines)
    count_bar += 1

    if len(df_klines.columns) == 12:
        df_klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume',
                             'Close time', 'trash1', 'trash2', 'trash3', 'trash4', 'trash5']
        df_klines['Open time'] = pd.to_datetime(df_klines['Open time'].astype(float), unit='ms').dt.date
        df_klines['Close time'] = pd.to_datetime(df_klines['Close time'].astype(float), unit='ms').dt.date
        df_klines['Volatility'] = (df_klines['High price'].astype(float) - df_klines['Low price'].astype(float)) / \
                                  df_klines['Low price'].astype(float)
        df_klines['24h change'] = (df_klines['Close price'].astype(float) - df_klines['Open price'].astype(float)) / \
                                  df_klines['Open price'].astype(float)
        df_klines['Correlation'] = df_klines['24h change'].astype(float) / df_principal_correlation['BTCUSD'].astype(
            float)

        df_klines['SMA6'] = df_klines['Close price'].rolling(6).mean()
        df_klines['SMA11'] = df_klines['Close price'].rolling(11).mean()
        df_klines['SMA21'] = df_klines['Close price'].rolling(21).mean()
        df_klines['Above SMA6'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA6'], 1, -1)
        df_klines['Above SMA11'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA11'], 2, -2)
        df_klines['Above SMA21'] = np.where(df_klines['Close price'].astype(float) > df_klines['SMA21'], 3, -3)

        df_klines_temp = df_klines[['High price', 'Low price', 'Close time']]

        high_9 = df_klines_temp['High price'].rolling(window=9).max()
        low_9 = df_klines_temp['Low price'].rolling(window=9).min()
        df_klines_temp['tenkan_sen'] = (high_9 + low_9) / 2

        high_26 = df_klines_temp['High price'].rolling(window=26).max()
        low_26 = df_klines_temp['Low price'].rolling(window=26).min()
        df_klines_temp['kijun_sen'] = (high_26 + low_26) / 2

        last_index = df_klines_temp.iloc[-1:].index[0]
        last_date = df_klines_temp['Close time'].iloc[-1]
        for i in range(26):
            df_klines_temp.loc[last_index + 1 + i, 'Date'] = last_date + timedelta(days=i)

        df_klines_temp['senkou_span_a'] = ((df_klines_temp['tenkan_sen'] + df_klines_temp['kijun_sen']) / 2).shift(26)
        high_52 = df_klines_temp['High price'].rolling(window=52).max()
        low_52 = df_klines_temp['Low price'].rolling(window=52).min()
        df_klines_temp['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

        df_klines_temp['chikou_span'] = df_klines_temp['Close time'].shift(-22)

        df_klines_temp_close = df_klines_temp['Close time']
        df_klines_temp_data = df_klines_temp['Date']
        df_klines_temp_close_result = df_klines_temp_close.combine_first(df_klines_temp_data)

        df_klines_temp.drop(['High price', 'Low price', 'Close time', 'Date'], axis=1, inplace=True)
        df_klines_temp = pd.concat([df_klines_temp, df_klines_temp_close_result], axis=1)

        df_klines.drop(['trash1', 'trash2', 'trash3', 'trash4', 'trash5'], axis=1, inplace=True)

        # separating the columns
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
        df_tenkan = df_klines_temp[['Close time', 'tenkan_sen']]
        df_kijun = df_klines_temp[['Close time', 'kijun_sen']]
        df_senkou_a = df_klines_temp[['Close time', 'senkou_span_a']]
        df_senkou_b = df_klines_temp[['Close time', 'senkou_span_b']]
        df_chikou = df_klines_temp[['Close time', 'chikou_span']]

        # changing the name of the columns
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
        df_tenkan.columns = ['Close time', coin]
        df_tenkan = df_tenkan.dropna()
        df_kijun.columns = ['Close time', coin]
        df_kijun = df_kijun.dropna()
        df_senkou_a.columns = ['Close time', coin]
        df_senkou_a = df_senkou_a.dropna()
        df_senkou_b.columns = ['Close time', coin]
        df_senkou_b = df_senkou_b.dropna()
        df_chikou.columns = ['Close time', coin]
        df_chikou = df_chikou.dropna()

        # merging the data of the coin with those of all the others
        df_principal_highs = pd.merge(df_principal_highs, df_highs, on="Close time", how='left')
        # df_principal_highs = df_principal_highs.copy()
        df_principal_lows = pd.merge(df_principal_lows, df_lows, on="Close time", how='left')
        # df_principal_lows = df_principal_lows.copy()
        df_principal_closes = pd.merge(df_principal_closes, df_closes, on="Close time", how='left')
        # df_principal_closes = df_principal_closes.copy()
        df_principal_volatility = pd.merge(df_principal_volatility, df_volatility, on="Close time", how='left')
        # df_principal_volatility = df_principal_volatility.copy()
        df_principal_correlation = pd.merge(df_principal_correlation, df_correlation, on="Close time", how='left')
        # df_principal_correlation = df_principal_correlation.copy()
        df_principal_SMA6 = pd.merge(df_principal_SMA6, df_SMA6, on="Close time", how='left')
        # df_principal_SMA6 = df_principal_SMA6.copy()
        df_principal_SMA11 = pd.merge(df_principal_SMA11, df_SMA11, on="Close time", how='left')
        # df_principal_SMA11 = df_principal_SMA11.copy()
        df_principal_SMA21 = pd.merge(df_principal_SMA21, df_SMA21, on="Close time", how='left')
        # df_principal_SMA21 = df_principal_SMA21.copy()
        df_principal_above6 = pd.merge(df_principal_above6, df_above6, on="Close time", how='left')
        # df_principal_above6 = df_principal_above6.copy()
        df_principal_above11 = pd.merge(df_principal_above11, df_above11, on="Close time", how='left')
        # df_principal_above11 = df_principal_above11.copy()
        df_principal_above21 = pd.merge(df_principal_above21, df_above21, on="Close time", how='left')
        # df_principal_above21 = df_principal_above21.copy()
        df_principal_tenkan = pd.merge(df_principal_tenkan, df_tenkan, on="Close time", how='left')
        # df_principal_tenkan = df_principal_tenkan.copy()
        df_principal_kijun = pd.merge(df_principal_kijun, df_kijun, on="Close time", how='left')
        # df_principal_kijun = df_principal_kijun.copy()
        df_principal_senkou_a = pd.merge(df_principal_senkou_a, df_senkou_a, on="Close time", how='left')
        # df_principal_senkou_a = df_principal_senkou_a.copy()
        df_principal_senkou_b = pd.merge(df_principal_senkou_b, df_senkou_b, on="Close time", how='left')
        # df_principal_senkou_b = df_principal_senkou_b.copy()
        df_principal_chikou = pd.merge(df_principal_chikou, df_chikou, on="Close time", how='left')
        # df_principal_chikou = df_principal_chikou.copy()

        progress_bar(count_bar, len(list_symbols))

df_principal_highs.to_excel('highs.xlsx')
df_principal_lows.to_excel('lows.xlsx')
df_principal_closes.to_excel('closes.xlsx')
df_principal_volatility.to_excel('volatility.xlsx')
df_principal_correlation.to_excel('correlation.xlsx')
df_principal_SMA6.to_excel('SMA6.xlsx')
df_principal_SMA11.to_excel('SMA11.xlsx')
df_principal_SMA21.to_excel('SMA21.xlsx')
df_principal_above6.to_excel('above6.xlsx')
df_principal_above11.to_excel('above11.xlsx')
df_principal_above21.to_excel('above21.xlsx')
df_principal_tenkan.to_excel('tenkan.xlsx')
df_principal_kijun.to_excel('kijun.xlsx')
df_principal_senkou_a.to_excel('senkou_a.xlsx')
df_principal_senkou_b.to_excel('senkou_b.xlsx')
df_principal_chikou.to_excel('chikou.xlsx')
