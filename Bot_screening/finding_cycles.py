import pandas as pd
import csv
#caricare storico!
#aggiungere una colonna con conteggio incrementale!
#separare le colonne corrispondenti alle varie coin creando una lista e prendendo coin e conteggio!
#tagliare il df prendendo gli ultimi n giorni (n = lunghezza massima ciclo)!
#cercare i valori che corrispondono ai massimi imponendo le condizioni di inizio e fine ciclo e swing
#annidare la ricerca con cicli di ordini diversi

df = pd.read_excel('storico.xlsx')
df.set_index('day', inplace = True)

max_days = 336
start = 48
end = 24

df_last_days = df.iloc[-max_days:]
df_last_days['days'] = pd.DataFrame(range(1, 1 + len(df_last_days)))
'''list_storico = []
for coin in df.columns:
    df_temp = df_last_days[coin, 'days']
    list_storico.append(df_temp)'''

file = open('demo.csv', 'w')
writer = csv.writer(file)
for coin in df_last_days:
    list_prices = df_last_days[coin].tolist()
    list_days = [coin]
    list_max = [coin]
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
    writer.writerow(list_days)
    writer.writerow(list_max)
file.close()
