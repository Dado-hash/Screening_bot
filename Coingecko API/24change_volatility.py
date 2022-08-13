import pandas as pd
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

cg.ping()

#prendo l'id delle prime 1000 coin per market cap
list_df = []
for num in range(2):
    if(num!=0):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h', 'volume']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins")

list_df = []
for num in range(7):
    if(num>5):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h', 'volume']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins1")

df = pd.read_csv("idcoins")
df1 = pd.read_csv("idcoins1")
coins_id_list = df["id"].tolist() + df1["id"].tolist()

#creo il file inizializzandolo con i dati di bitcoin
id_coin = 'bitcoin'
hist_data = cg.get_coin_ohlc_by_id(id = id_coin, vs_currency = 'usd', days = '30', interval = 'daily')
df = pd.DataFrame(hist_data)
df['day'] = df[[0]]
df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
df['close'] = df[[4]]
df['open'] = df[[1]]
df['24h_change'] = (df['close'] - df['open']) / df['open']
df['high'] = df[[2]]
df['low'] = df[[3]]
df['24h_volatility'] = (df['high'] - df['low']) / df['low']
columns = ['day', '24h_change', '24h_volatility', 'volume']
df_principale = df[columns]
df_principale = df_principale.groupby('day').sum()
columns = ['24h_change']
df_principale_24h = df_principale[columns].astype(str)
columns = ['24h_volatility']
df_principale_volatility = df_principale[columns].astype(str)
columns = ['volume']
df_principale_volume = df_principale[columns].astype(str)
df_principale_24h.columns = [id_coin]
df_principale_volatility.columns = [id_coin]
df_principale_volume.columns = [id_coin]
df_principale_24h[id_coin] = df_principale_24h[id_coin].str.replace(r'.', ',')
df_principale_volatility[id_coin] = df_principale_volatility[id_coin].str.replace(r'.', ',')
df_principale_volume[id_coin] = df_principale_volume[id_coin].str.replace(r'.', ',')

#aggiungo le alt
count = 0
for id_coin in coins_id_list:
    if(id_coin != 'bitcoin'):
        if(count == 30):
            t.sleep(70)
            count = 0
        hist_data = cg.get_coin_ohlc_by_id(id = id_coin, vs_currency = 'bitcoin', days = '30', interval = 'daily')
        df = pd.DataFrame(hist_data)
        df['day'] = df[[0]]
        df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
        df['close'] = df[[4]]
        df['open'] = df[[1]]
        df['24h_change'] = (df['close'] - df['open']) / df['open']
        df['high'] = df[[2]]
        df['low'] = df[[3]]
        df['24h_volatility'] = (df['high'] - df['low']) / df['low']
        columns = ['day', '24h_change', '24h_volatility']
        df = df[columns]
        df = df.groupby('day').sum()
        columns = ['24h_change']
        df_24h = df[columns].astype(str)
        df_24h.columns = [id_coin]
        df_24h[id_coin] = df_24h[id_coin].str.replace(r'.', ',')
        columns = ['24h_volatility']
        df_volatility = df[columns].astype(str)
        df_volatility.columns = [id_coin]
        df_volatility[id_coin] = df_volatility[id_coin].str.replace(r'.', ',')
        columns= ['volume']
        df_volume = df[columns].astype(str)
        df_volume.columns = [id_coin]
        df_volume[id_coin] = df_volume[id_coin].str.replace(r'.', ',')
        df_principale_24h = pd.merge(df_principale_24h, df_24h, on = "day", how = 'left')
        df_principale_volatility = pd.merge(df_principale_volatility, df_volatility, on = "day", how = 'left')
        df_principale_volume = pd.merge(df_principale_volume, df_volume, on = 'day', how = 'left')
        count += 1

#salvo i due file con 24h_change e volatility
df_principale_24h.to_cvs('24h_change.csv')
df_principale_volatility.to_csv('volatility.csv')
df_principale_volume.to_csv('volume.csv')

#creo i dataframe con le classifica a 3 giorni
df_principale_24h = df_principale_24h.drop('day')
df_3d_change = df_principale_24h.tail(3).sum()                                     #1

df_3d_positive = df_principale_24h.tail(3)
for id in df_3d_positive.columns:
    df_3d_positive[id] = df_3d_positive[id].apply(lambda x: 1 if x > 0 else 0)
df_3d_positive = df_3d_positive.sum()                                              #2

df_30d_volume_mean = df_principale_volume.describe().loc('mean')
df_3d_volume_check = df_principale_24h.tail(3)
for id in df_3d_volume_check:
    mean = df_30d_volume_mean[id]
    df_3d_volume_check[id] = df_3d_volume_check[id].apply(lambda x: 1 if x > mean else 0)
df_3d_volume_check = df_3d_volume_check.sum()                                      #3

df_30d_volatility_mean = df_principale_volatility.describe().loc('mean')
df_3d_volatility_check = df_3d_change
for id in df_3d_volatility_check:
    mean = df_30d_volatility_mean[id]
    df_3d_volatility_check[id] = df_3d_volatility_check[id].apply(lambda x: 1 if x < mean else 0)
df_3d_volatility_check = df_3d_volatility_check.sum()                            #4

#creo il dataframe con la classifica a 7 giorni
df_7d_change = df_principale_24h.tail(7).sum()
df_7d_pos = df_principale_24h.tail(7)
for id in df_7d_pos.columns:
    df_7d_pos[id] = df_7d_pos[id].apply(lambda x: 1 if x > 0 else 0)
df_7d_pos = df_7d_pos.sum()   

#creo il dataframe con la classifica a 14 giorni
df_14d_change = df_principale_24h.tail(14).sum()

#creo il dataframe con la classifica a 30 giorni
df_30d_change = df_principale_24h.tail(14).sum()
