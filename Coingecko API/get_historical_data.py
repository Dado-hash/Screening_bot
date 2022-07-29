import pandas as pd
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

cg.ping()

#creo il file mettendo i prezzi di bitcoin
id_coin = 'bitcoin'
hist_data = cg.get_coin_market_chart_by_id(id = id_coin, vs_currency = 'usd', days = 'max')
df = pd.DataFrame(hist_data)
df['day'] = df['prices'].str[0]
df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
df[id_coin] = df['prices'].str[1]
columns = ['day', id_coin]
df_principale = df[columns]
df_principale.set_index('day', inplace = True)
df_principale.drop(df_principale.tail(1).index,inplace=True)
print(df_principale)

#aggiungo le alt (capire come allineare)
id_coin = 'ethereum'
hist_data = cg.get_coin_market_chart_by_id(id = id_coin, vs_currency = 'usd', days = 'max')
df = pd.DataFrame(hist_data)
df['day'] = df['prices'].str[0]
df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
df[id_coin] = df['prices'].str[1]
columns = ['day', id_coin]
df = df[columns]
df.set_index('day', inplace = True)
df = pd.merge(df_principale, df, on="day", how = 'left')
print(df)