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
for num in range(6):
    if(num!=0):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins")

list_df = []
for num in range(11):
    if(num>5):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
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
columns = ['day', '24h_change', '24h_volatility']
df_principale = df[columns]
df_principale = df_principale.groupby('day').sum()
columns = ['24h_change']
df_principale_24h = df_principale[columns].astype(str)
columns = ['24h_volatility']
df_principale_volatility = df_principale[columns].astype(str)
df_principale_24h.columns = [id_coin]
df_principale_volatility.columns = [id_coin]
df_principale_24h[id_coin] = df_principale_24h[id_coin].str.replace(r'.', ',')
df_principale_volatility[id_coin] = df_principale_volatility[id_coin].str.replace(r'.', ',')
print(df_principale_24h)
print(df_principale_volatility)

#aggiungo le alt
count = 0
for id_coin in coins_id_list:
    if(id_coin != 'bitcoin'):
        if(count == 30):
            t.sleep(70)
            count = 0
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
        df_principale_24h = pd.merge(df_principale_24h, df_24h, on="day", how = 'left')
        df_principale_volatility = pd.merge(df_principale_volatility, df_volatility, on="day", how = 'left')
        print(df_principale_volatility)
        print(df_principale_24h)
        count += 1

#salvo i due file con 24h_change e volatility
df_principale_24h.to_cvs('24h_change.csv')
df_principale_volatility.to_csv('volatility.csv')