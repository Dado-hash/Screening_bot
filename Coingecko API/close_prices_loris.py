import pandas as pd
import datetime as dt
from datetime import date
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

cg.ping()

df_close_prices = pd.read_excel(open('Master_Download_Prices.xlsx', 'rb'), sheet_name='Close_Usd') 
print(df_close_prices)
first_part_df = df_close_prices[['Data', 'EurUsd Curncy', 'MSDEWIN Index', 'MSDEEEMN Index', 'LGCPTREU Index', 'LGAGTREU Index', 'XAU Curncy', 'BGCI Index', 'SPCBDM Index', 'XAU Curncy', 'BGCI Index', 'SPCBDM Index']]
print(first_part_df)

begin = date(2021, 12, 31)
today = date.today()
days_from_begin = today - begin  #capire come aggiungere 1
print(days_from_begin)

df = pd.DataFrame(cg.get_coin_market_chart_by_id(id = 'bitcoin', vs_currency = 'usd', days = days_from_begin, interval = 'daily'))
df.drop(df.tail(1).index,inplace=True)
df['Data'] = df['prices'].str[0]
df['Data'] = pd.to_datetime(df['Data']/1000, unit = 's').dt.date
df['bitcoin'] = df['prices'].str[1].astype(str)
df['bitcoin'] = df['bitcoin'].str.replace(r'.', ',')
columns = ['Data', 'bitcoin']
df = df[columns]
df.set_index('Data', inplace = True)

list = df['bitcoin'].to_list()
list.insert(0, 'n_columns+1')
list.insert(0, 'id_coin')
list.insert(0, 'id_coin')
new_column = pd.DataFrame(list)
print(new_column)