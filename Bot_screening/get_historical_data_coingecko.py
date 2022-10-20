import pandas as pd
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI
import colorama
import numpy as np

cg = CoinGeckoAPI()

cg.ping()

def progress_bar(progress, total, color = colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if (progress == total):
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r")
        print(colorama.Fore.RESET)

number_coins = int(input("Inserisci il numero di coin -> "))
if(number_coins > 100):
    range1 = (int(number_coins)//200) + 1
    range2 = (int(number_coins)//100) + 1

if(number_coins > 100):
    list_df = []
    for num in range(range1):
        if(num!=0):
            complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 100, page = num, price_change_percentage = '24h')
            list_df.append(pd.DataFrame(complexPriceRequest))
    df = pd.concat(list_df)
    list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
    df = df[list_columns]   
    df.set_index("id", inplace = True)
    df.to_csv("idcoins")

    list_df = []
    for num in range(range2):
        if(num>range2//2):
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
else:
    list_df = []
    complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = number_coins, page = 1, price_change_percentage = '24h')
    list_df.append(pd.DataFrame(complexPriceRequest))
    df = pd.concat(list_df)
    list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
    df = df[list_columns]   
    df.set_index("id", inplace = True)
    df.to_csv("idcoins1")
    df = pd.read_csv("idcoins")
    coins_id_list = df["id"].tolist()

#creo il file mettendo i prezzi di bitcoin
id_coin = 'bitcoin'
hist_data = cg.get_coin_market_chart_by_id(id = id_coin, vs_currency = 'usd', days = 'max', interval = 'daily')
df = pd.DataFrame(hist_data)
df.drop(df.tail(1).index,inplace=True)
df['day'] = df['prices'].str[0]
df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
df[id_coin] = df['prices'].str[1]
df[id_coin] = df[id_coin]
columns = ['day', id_coin]
df_principale = df[columns]
df_principale['SMA6'] = df_principale[id_coin].rolling(6).mean()
df_principale['SMA11'] = df_principale[id_coin].rolling(11).mean()
df_principale['SMA21'] = df_principale[id_coin].rolling(21).mean()
df_principale['Above SMA6'] = np.where(df_principale[id_coin].astype(float) > df_principale['SMA6'], 1, 0)
df_principale['Above SMA11'] = np.where(df_principale[id_coin].astype(float) > df_principale['SMA11'], 1, 0)
df_principale['Above SMA21'] = np.where(df_principale[id_coin].astype(float) > df_principale['SMA21'], 1, 0)
df_principale_SMA6 = df_principale[['day', 'SMA6']]
df_principale_SMA11 = df_principale[['day', 'SMA11']]
df_principale_SMA21 = df_principale[['day', 'SMA21']]
df_principale_above6 = df_principale[['day', 'Above SMA6']]
df_principale_above11 = df_principale[['day', 'Above SMA11']]
df_principale_above21 = df_principale[['day', 'Above SMA21']]
df_principale_SMA6.columns = ['day', id_coin]
df_principale_SMA11.columns = ['day', id_coin]
df_principale_SMA21.columns = ['day', id_coin]
df_principale_above6.columns = ['day', id_coin]
df_principale_above11.columns = ['day', id_coin]
df_principale_above21.columns = ['day', id_coin]
df_principale.set_index('day', inplace = True)
df_principale.drop(['SMA6', 'SMA11', 'SMA21', 'Above SMA6', 'Above SMA11', 'Above SMA21'], inplace = True, axis = 1)
print(df_principale)

#aggiungo le alt
count = 0
count_bar = 0
for id_coin in coins_id_list:
    if(id_coin != 'bitcoin'):
        if(count == 16):
            t.sleep(80)
            count = 0
        hist_data = cg.get_coin_market_chart_by_id(id = id_coin, vs_currency = 'btc', days = 'max', interval = 'daily')
        df = pd.DataFrame(hist_data)
        df.drop(df.tail(1).index,inplace=True)
        df['day'] = df['prices'].str[0]
        df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
        df[id_coin] = df['prices'].str[1]
        df[id_coin] = df[id_coin]
        columns = ['day', id_coin]
        df = df[columns]
        df['SMA6'] = df[id_coin].rolling(6).mean()
        df['SMA11'] = df[id_coin].rolling(11).mean()
        df['SMA21'] = df[id_coin].rolling(21).mean()
        df['Above SMA6'] = np.where(df[id_coin].astype(float) > df['SMA6'], 1, 0)
        df['Above SMA11'] = np.where(df[id_coin].astype(float) > df['SMA11'], 1, 0)
        df['Above SMA21'] = np.where(df[id_coin].astype(float) > df['SMA21'], 1, 0)
        df_SMA6 = df[['day', 'SMA6']]
        df_SMA11 = df[['day', 'SMA11']]
        df_SMA21 = df[['day', 'SMA21']]
        df_above6 = df[['day', 'Above SMA6']]
        df_above11 = df[['day', 'Above SMA11']]
        df_above21 = df[['day', 'Above SMA21']]
        df_SMA6.columns = ['day', id_coin]
        df_SMA11.columns = ['day', id_coin]
        df_SMA21.columns = ['day', id_coin]
        df_above6.columns = ['day', id_coin]
        df_above11.columns = ['day', id_coin]
        df_above21.columns = ['day', id_coin]
        df.set_index('day', inplace = True)
        df.drop(['SMA6', 'SMA11', 'SMA21', 'Above SMA6', 'Above SMA11', 'Above SMA21'], inplace = True, axis = 1)
        df_principale = pd.merge(df_principale, df, on="day", how = 'left')
        df_principale = df_principale.copy()
        df_principale_SMA6 = pd.merge(df_principale_SMA6, df_SMA6, on="day", how = 'left')
        df_principale_SMA6 = df_principale_SMA6.copy()
        df_principale_SMA11 = pd.merge(df_principale_SMA11, df_SMA11, on="day", how = 'left')
        df_principale_SMA11 = df_principale_SMA11.copy()
        df_principale_SMA21 = pd.merge(df_principale_SMA21, df_SMA21, on="day", how = 'left')
        df_principale_SMA21 = df_principale_SMA21.copy()
        df_principale_above6 = pd.merge(df_principale_above6, df_above6, on="day", how = 'left')
        df_principale_above6 = df_principale_above6.copy()
        df_principale_above11 = pd.merge(df_principale_above11, df_above11, on="day", how = 'left')
        df_principale_above11 = df_principale_above11.copy()
        df_principale_above21 = pd.merge(df_principale_above21, df_above21, on="day", how = 'left')
        df_principale_above21 = df_principale_above21.copy()
        count += 1
        count_bar += 1
        progress_bar(count_bar, number_coins-1)
        
#salvo lo storico
df_principale.to_excel('storico.xlsx')
df_principale_SMA6.to_excel('SMA6.xlsx')
df_principale_SMA11.to_excel('SMA11.xlsx')
df_principale_SMA21.to_excel('SMA21.xlsx')
df_principale_above6.to_excel('above6.xlsx')
df_principale_above11.to_excel('above11.xlsx')
df_principale_above21.to_excel('above21.xlsx')