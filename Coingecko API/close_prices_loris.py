import pandas as pd
import datetime as dt
from datetime import date
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

cg.ping()

#prendo il file excel e spezzo a metà gli indici e le coin per lavorarci in modo separato
df_close_prices = pd.read_excel(open('Master_Download_Prices.xlsx', 'rb'), sheet_name='Close_Usd') 
first_part_df = df_close_prices[['Data', 'EurUsd Curncy', 'MSDEWIN Index', 'MSDEEEMN Index', 'LGCPTREU Index', 'LGAGTREU Index', 'XAU Curncy Usd', 'BGCI Index Usd', 'SPCBDM Index Usd', 'XAU Curncy Eur', 'BGCI Index Eur', 'SPCBDM Index Eur']]
second_part_df = df_close_prices.drop(['Data', 'EurUsd Curncy', 'MSDEWIN Index', 'MSDEEEMN Index', 'LGCPTREU Index', 'LGAGTREU Index', 'XAU Curncy Usd', 'BGCI Index Usd', 'SPCBDM Index Usd', 'XAU Curncy Eur', 'BGCI Index Eur', 'SPCBDM Index Eur'], axis = 1, inplace = False)

#prendo il numero di giorni che sono passati dall'inizio dell'anno
begin = date(2021, 12, 30)
today = date.today()
days_from_begin = today - begin

#scarico per ogni coin lo storico dei prezzi, attacco le prime tre righe di default e le salvo in una lista per concatenarle dopo
second_part_df = second_part_df[second_part_df.loc[1].sort_values().index]
print(second_part_df)
coins_tickets = second_part_df.values.tolist()[1]
print(coins_tickets)
#second_part_df = second_part_df.sort_index(axis = 1)
id_coins = second_part_df.columns
list_prices = []
list_index = []
index = 13
count = 0
for id_c in id_coins:
    if(count == 18):
            t.sleep(90)
            count = 0
    print(id_c)
    df = pd.DataFrame(cg.get_coin_market_chart_by_id(id = id_c, vs_currency = 'usd', days = days_from_begin, interval = 'daily'))
    df.drop(df.tail(1).index,inplace=True)
    df['Data'] = df['prices'].str[0]
    df['Data'] = pd.to_datetime(df['Data']/1000, unit = 's').dt.date
    df[id_c] = df['prices'].str[1].astype(str)
    df[id_c] = df[id_c].str.replace(r'.', ',')
    columns = ['Data', id_c]
    df = df[columns]
    rows = df.shape[0]
    df.set_index('Data', inplace = True)
    list_prices_coin = df[id_c].to_list()
    if(rows < days_from_begin.days):
        missing = days_from_begin.days - rows
        for num in range(missing):
            list_prices_coin.insert(0, 0)
    list_prices_coin.insert(0, index)
    list_prices_coin.insert(0, coins_tickets[index - 13])
    list_prices_coin.insert(0, id_c)
    list_index.append(index)
    new_column = pd.DataFrame(list_prices_coin)
    list_prices.append(new_column)
    index += 1
    count += 1

#concateno i prezzi delle coin
second_part_df = pd.concat(list_prices, axis = 1)
second_part_df.columns = list_index
print(second_part_df)

#creo la prima colonna con le date
list_indexes = []
list_index = []
df = pd.DataFrame(cg.get_coin_market_chart_by_id(id = 'bitcoin', vs_currency = 'usd', days = days_from_begin, interval = 'daily'))
df.drop(df.tail(1).index,inplace=True)
df['Data'] = df['prices'].str[0]
df['Data'] = pd.to_datetime(df['Data']/1000, unit = 's').dt.date
df['bitcoin'] = df['prices'].str[1].astype(str)
df['bitcoin'] = df['bitcoin'].str.replace(r'.', ',')
columns = ['Data', 'bitcoin']
df = df[columns]
list_data = df['Data'].to_list()
list_data.insert(0, 'Data')
list_data.insert(0, 'Data')
list_data.insert(0, 1)
list_index.append(1)
new_column = pd.DataFrame(list_data)
list_indexes.append(new_column)

#scarico i prezzi degli indici
first_part_df = first_part_df.drop('Data', axis = 1, inplace = False)
id_indexes = first_part_df.columns
extended_id_indexes = first_part_df.values.tolist()[1]
num_index = 2
for index in id_indexes:
    list_prices = []
    #manca trovare come scaricare i dati degli indici
    list_prices.insert(0, num_index)
    list_prices.insert(0, extended_id_indexes[num_index - 2])
    list_prices.insert(0, index)
    list_index.append(num_index)
    new_column = pd.DataFrame(list_prices)
    list_indexes.append(new_column)
    num_index += 1

#concateno gli indici(sarà uguale alle coin fin qui)
first_part_df = pd.concat(list_indexes, axis = 1)
first_part_df.columns = list_index
'''first_part_df.columns = ['Data','EurUsd Curncy', 'MSDEWIN Index', 'MSDEEEMN Index', 'LGCPTREU Index',
       'LGAGTREU Index', 'XAU Curncy Usd', 'BGCI Index Usd',
       'SPCBDM Index Usd', 'XAU Curncy Eur', 'BGCI Index Eur',
       'SPCBDM Index Eur']'''

#concateno i due dataframe
df_principale = pd.concat([first_part_df, second_part_df], axis = 1)
print(df_principale)

#creo il dataframe per il secondo foglio
df_principale = df_principale.drop('Data', axis = 1)
df_coins_list = df_principale.iloc([0, 1])
df_coins_list = df_coins_list.T
num_list = df_coins_list[[0]]
num_list.insert(0, 1)  #manca cancellare l'ultimo numero
new_column = pd.DataFrame(num_list)
df_coins_list = pd.concat([new_column, df_coins_list], axis = 1)  #manca rinominare le colonne e riordinarle
