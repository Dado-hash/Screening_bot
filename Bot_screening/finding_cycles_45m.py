from binance import Client
import api_keys
import pandas as pd
from datetime import datetime, timedelta
import csv

client = Client(api_keys.API_KEY, api_keys.SECRET)
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE, "1 Sep, 2022")
klines = pd.DataFrame(klines)
klines.columns = ['Open time', 'Open price', 'High price', 'Low price', 'Close price', 'Volume', 'Close time', 'Trash', 'Trades', 'Trash2', 'Trash3', 'Trash4']
klines.drop(['Trash', 'Trash2', 'Trash3', 'Trash4'], axis = 1, inplace = True)
klines['Open time'] = klines['Open time'].astype(float)
klines['Open time'] = klines['Open time']*1000000 
klines['Open time'] = pd.to_datetime(klines['Open time'])
klines['Close time'] = klines['Close time'].astype(float)
klines['Close time'] = klines['Close time']*1000000 
klines['Close time'] = pd.to_datetime(klines['Close time'])

klines_grouped_principale = klines.iloc[0:3]
klines_grouped_principale['group'] = 0
count = 1
for num in range(1, len(klines)//3):
    klines_grouped = klines.iloc[num*3:(num+1)*3]    
    klines_grouped['group'] = count
    klines_grouped_principale = pd.concat([klines_grouped_principale, klines_grouped])
    count += 1
if(count*3 < len(klines)):
    missing = len(klines) - count*3
    klines_grouped = klines.iloc[-missing:]
    klines_grouped['group'] = count
    klines_grouped_principale = pd.concat([klines_grouped_principale, klines_grouped])

df_with_first_row = klines_grouped_principale.groupby('group').first()
df_with_last_row = klines_grouped_principale.groupby('group').last()
df_45m = df_with_first_row[['Open time', 'Trades']]
df_45m['Open price'] = df_with_first_row['Open price']
df_45m['Close price'] = df_with_last_row['Close price']
df_45m.drop('Trades', axis = 1, inplace = True)
df_45m['High price'] = klines_grouped_principale.groupby(['group'], sort=False)['High price'].max()
df_45m['Low price'] = klines_grouped_principale.groupby(['group'], sort=False)['Low price'].min()
df_45m.set_index('Open time', inplace = True)

min_date = str(input('Inserisci data e ora di un minimo (yyyy-mm-dd hh:mm:ss): '))
min_date = datetime.strptime(min_date, "%Y-%m-%d %H:%M:%S")
min = df_45m.loc[min_date]
print(min)
df_ultimate = df_45m.tail(len(df_45m) - df_45m.index.get_loc(min_date))
print(df_ultimate)

max_lenght = 44
min_lenght = 24
start = 6
end = 3

file = open('45m min.csv', 'w')
writer = csv.writer(file)
list_prices = df_ultimate['Low price'].tolist()
list_days = ['Candela in cui è avvenuto il minimo']
list_max = ['Prezzo raggiunto durante il minimo']
list_costraints = ['Candela in cui si è vincolato al rialzo']
list_price_costraints = ['Prezzo con il quale si è vincolato al rialzo']
for n in range(len(df_ultimate)):
    flag = 1
    if(n >= end and n <= len(df_ultimate) - start):
        for back in range(end):
            if(list_prices[n] < list_prices[n - back -1]):
                flag = 0
        if(flag):
            for forward in range(start):
                if(list_prices[n] < list_prices[n + forward]):
                    flag = 0
        if(flag):
            list_days.append(n)
            list_max.append(list_prices[n])
            flag = 1
            for day in range(min_lenght):
                if(n + day < len(df_ultimate) and flag):
                    if(list_prices[n + day] > list_prices[n]):
                        flag = 0
                        list_costraints.append(n + day)
                        list_price_costraints.append(list_prices[n + day])
    i = min_date + timedelta(minutes=45)
writer.writerow(list_days)
writer.writerow(list_max)
writer.writerow(list_costraints)
writer.writerow(list_price_costraints)
file.close()