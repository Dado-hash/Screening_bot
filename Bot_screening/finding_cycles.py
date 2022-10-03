import pandas as pd
import csv

#annidare la ricerca con cicli di ordini diversi

df = pd.read_excel('storico.xlsx')
df.set_index('day', inplace = True)

max_lenght = 336  #408
min_lenght = 192
start = 48
end = 24
max_days = max_lenght + start + end

df_last_days = df.iloc[-max_days:]
df_last_days['days'] = pd.DataFrame(range(1, 1 + len(df_last_days)))

file = open('demo.csv', 'w')
writer = csv.writer(file)
for coin in df_last_days:
    list_prices = df_last_days[coin].tolist()
    list_days = ['Giorno in cui è avvenuto il massimo di ' + coin]
    list_max = ['Prezzo raggiunto durante il massimo di ' + coin]
    list_costraints = ['Giorno in cui ' + coin + ' si è vincolato al rialzo']
    list_price_costraints = ['Prezzo con il quale ' + coin + ' si è vincolato al rialzo']
    for n in range(len(df_last_days)):
        flag = 1
        if(n >= end and n <= len(df_last_days) - start):
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
                    if(n + day < len(df_last_days) and flag):
                        if(list_prices[n + day] > list_prices[n]):
                            flag = 0
                            list_costraints.append(n + day)
                            list_price_costraints.append(list_prices[n + day])
    writer.writerow(list_days)
    writer.writerow(list_max)
    writer.writerow(list_costraints)
    writer.writerow(list_price_costraints)
file.close()