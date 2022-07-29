import pandas as pd
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

cg.ping()

#creo 2 file per avere l'id di 1000 coins
list_df = []
for num in range(6):
    if(num!=0):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
print(df)
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
print(df)
df.to_csv("idcoins1")


#creo i file con i dati aggiornati
df = pd.read_csv("idcoins")
coins_id_list = df["id"].tolist()
complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', ids = coins_id_list)
df = pd.DataFrame(complexPriceRequest)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)

df1 = pd.read_csv("idcoins1")
coins_id_list = df1["id"].tolist()
complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', ids = coins_id_list)
df1 = pd.DataFrame(complexPriceRequest)
list_columns = ['id', 'name', 'current_price', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df1 = df1[list_columns]   
df1.set_index("id", inplace = True)
df = pd.concat([df, df1])
print(df)
df.to_csv("df_principale")


#creo il file per avere i prezzi attuali
df_principale = pd.read_csv("df_principale")
list_columns = ['id', 'current_price']
df_current_price = df_principale[list_columns]
df_current_price.set_index('id', inplace = True)
df_current_price.to_csv("current_price")
print(df_current_price)

#creo il file per avere le variazioni gironaliere
df_principale = pd.read_csv("df_principale")
list_columns = ['id', 'price_change_percentage_24h']
df_24h_change = df_principale[list_columns]
df_24h_change.set_index('id', inplace = True)
df_24h_change.to_csv("price_change_percentage_24h")
print(df_24h_change)

#creo il file per avere la volaitilità
df_principale = pd.read_csv("df_principale")
df_principale['volatility'] = (df_principale['high_24h'] - df_principale['low_24h'])/df_principale['low_24h']
list_columns = ['id', 'volatility']
volatility = df_principale[list_columns]
volatility.set_index('id', inplace = True)
volatility.to_csv("volatility")
print(volatility)