import pandas as pd
import colorama
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()
cg.ping()

pd.set_option("display.precision", 8)
#creo i file con cumulativi e costraints
def progress_bar(progress, total, color = colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if (progress == total):
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r") 
        print(colorama.Fore.RESET)

direction = input("In che direzione voui calcolare i cumulativi?\n"
                    "0 -> Da oggi andando indietro\n"
                    "1 -> Da un giorno specifico in avanti\n")
direction = int(direction)

if(direction):
    start = input("Da che giorno vuoi partire?\n")
    start = int(start)
else:
    start = input("Fino a che giorno vuoi arrivare?\n")
    start = int(start)

all = input("Seleziona che tipo di cumulativi ti servono:\n"
            "0 -> Solo alcuni\n"
            "1 -> Tutti\n")
all = int(all)

if(all):
    cumulatives = list(range(start + 1))
    cumulatives.remove(0)
else:
    cumulatives = input("Inserisci il numero di giorni dei cumulativi che ti servono\n")
    cumulatives = cumulatives.split()
    for i in range(len(cumulatives)):
        cumulatives[i] = int(cumulatives[i])

totale = (len(cumulatives) * 5) - 3
progresso = 0

df_principale = pd.read_excel('storico.xlsx')
df_principale.set_index('day', inplace = True)

leaderboard = []
if(not direction):
    for num in cumulatives:
        pd.set_option('display.float_format', lambda x: '%.5f' % x)
        df_24h_sum = df_principale.T
        df_24h_sum = (df_24h_sum.iloc[:, len(df_24h_sum.columns)-1] - df_24h_sum.iloc[:, len(df_24h_sum.columns)-num]) / df_24h_sum.iloc[:, len(df_24h_sum.columns)-num]
        df_24h_sum = df_24h_sum.sort_values(ascending = False)
        df_24h_sum = df_24h_sum.to_frame()
        df = df_24h_sum.copy()[[]]
        df_24h_sum.columns = ['Cumulative']
        df_24h_sum.reset_index(drop=True, inplace = True)
        ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
        ranking.columns = ['Rank']
        ranking['Cumulative'] = df_24h_sum['Cumulative']
        df_24h_sum = pd.concat([df_24h_sum, ranking], axis = 1)
        df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']
        df_24h_sum.drop('Trash', axis = 1, inplace = True)
        df_24h_sum.index = df.index
        leaderboard.append(df_24h_sum)
        progresso += 1
        progress_bar(progresso, totale)
else:
    for num in cumulatives:
        pd.set_option('display.float_format', lambda x: '%.5f' % x)
        df_24h_sum = df_principale.T
        df_24h_sum = (df_24h_sum.iloc[:, (len(df_24h_sum.columns)-1-start + num)] - df_24h_sum.iloc[:, (len(df_24h_sum.columns)-1-start)]) / df_24h_sum.iloc[:, (len(df_24h_sum.columns)-1-start)]
        df_24h_sum = df_24h_sum.sort_values(ascending = False)
        df_24h_sum = df_24h_sum.to_frame()
        df = df_24h_sum.copy()[[]]
        df_24h_sum.columns = ['Cumulative']
        df_24h_sum.reset_index(drop=True, inplace = True)
        ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
        ranking.columns = ['Rank']
        ranking['Cumulative'] = df_24h_sum['Cumulative']
        df_24h_sum = pd.concat([df_24h_sum, ranking], axis = 1)
        df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']
        df_24h_sum.drop('Trash', axis = 1, inplace = True)
        df_24h_sum.index = df.index
        leaderboard.append(df_24h_sum)
        progresso += 1
        progress_bar(progresso, totale)

cycles = leaderboard
with pd.ExcelWriter('leaderboards.xlsx') as writer:  
    counter = 0
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(cumulatives[counter]) + 'd')
        counter += 1
        progresso += 1
        progress_bar(progresso, totale)

df_totale = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[0]) + 'd')
titolo = str(cumulatives[0]) + 'd'
df_totale.columns = ['Coin', titolo, 'Rank'] 
df_totale.drop('Rank', inplace = True, axis = 1)
df_totale.set_index('Coin', inplace = True)
for num in range(len(cumulatives)):
    if(cumulatives[num] != cumulatives[0]):
        second_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[num]) + 'd')
        titolo = str(cumulatives[num]) + 'd'
        second_df.columns = ['Coin', titolo, 'Rank']  
        second_df.drop('Rank', inplace = True, axis = 1)
        second_df.set_index('Coin', inplace = True)
        df_totale = df_totale.merge(second_df, on = 'Coin')
        progresso += 1
        progress_bar(progresso, totale)

first = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[0]) + 'd')
first.columns = ['Coin', 'Cumulative', 'Rank']
first.drop('Rank', inplace = True, axis = 1)
first.set_index('Coin', inplace = True)

leaderboard = []
for num in range(len(cumulatives)-1):
    first_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[num]) + 'd')
    second_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[num+1]) + 'd')
    first_df.columns = ['Coin', 'Cumulative', 'Rank1']
    second_df.columns = ['Coin', 'Cumulative', 'Rank2']
    first_df.drop('Cumulative', inplace = True, axis = 1)
    df = second_df.merge(first_df, on = 'Coin')
    df['Change'] = df['Rank1'] - df['Rank2']
    df.drop(['Rank1', 'Rank2'], inplace = True, axis = 1)
    df.set_index('Coin', inplace = True)
    leaderboard.append(df)
    progresso += 1
    progress_bar(progresso, totale)

with pd.ExcelWriter('leaderboards.xlsx') as writer:
    df_totale.to_excel(writer, sheet_name = 'Aggregate')
    first.to_excel(writer, sheet_name = str(cumulatives[0]) + 'd')
    counter = 1
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(cumulatives[counter]) + 'd')
        counter += 1
        progresso += 1
        progress_bar(progresso, totale)

'''constraints = input("Ti interessa sapere se delle coin si sono vincolate al rialzo?\n"
                    "0 -> No\n"
                    "1 -> Sì\n")
coins = df_principale.columns
if(int(constraints)):
    list = []
    list_test = []
    lenght_min = input("Qual è la durata minima del ciclo che stai cercando?\n")
    lenght_min = int(lenght_min)
    start_cycle = lenght_min//4
    for coin in coins:
        count_tot = 0
        count_rel = 0
        flag = 0
        for df in cycles:
            if(flag == 0 and count_tot < lenght_min):
                if(df['Cumulative'][coin] < 0):
                    count_rel += 1
                elif(df['Cumulative'][coin] > 0 and count_rel >= start_cycle):
                    list_test.append(coin)
                    list.append((coin, count_tot, df['Cumulative'][coin]))
                    flag = 1
                else:
                    count_rel = 0
                count_tot += 1
    df = df_totale.loc[df_totale.index.isin(list_test)]
    df.to_excel('constraints.xlsx')'''

list_cum = []
for cum in cumulatives:
    df_sheet = pd.read_excel('leaderboards.xlsx', sheet_name= str(cum) + 'd')
    df_sheet = df_sheet.rename(columns={'Change': 'Change ' + str(cum) + 'd'})
    list_cum.append(df_sheet)
df_cums = pd.concat(list_cum, axis = 1)
df_cums.to_excel('cumulatives_changes.xlsx')

#Calcolo volatilita', correlazione e creo i file con low e high
list_df = []
for num in range(2):
    if(num!=0):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 6, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins")

list_df = []
for num in range(3):
    if(num>1):
        complexPriceRequest = cg.get_coins_markets(vs_currency = 'btc', order = 'market_cap_desc', per_page = 6, page = num, price_change_percentage = '24h')
        list_df.append(pd.DataFrame(complexPriceRequest))
df = pd.concat(list_df)
list_columns = ['id', 'name', 'current_price', 'market_cap', 'high_24h', 'low_24h', 'price_change_percentage_24h']
df = df[list_columns]   
df.set_index("id", inplace = True)
df.to_csv("idcoins1")

df = pd.read_csv("idcoins")
df1 = pd.read_csv("idcoins1")
coins_id_list = df["id"].tolist() + df1["id"].tolist()

id_coin = 'bitcoin'
hist_data = cg.get_coin_ohlc_by_id(id = id_coin, vs_currency = 'usd', days = '30', interval = 'daily')
df = pd.DataFrame(hist_data)
df['day'] = df[[0]]
df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
df['close'] = df[[4]]
df['open'] = df[[1]]
df_with_first_row_per_day = df.groupby('day').first()
df_with_last_row_per_day = df.groupby('day').last()
df_giornaliero = df_with_last_row_per_day
df_giornaliero['24h_change'] = (df_with_last_row_per_day['close'] - df_with_first_row_per_day['open']) / df_with_first_row_per_day['open']
df['high'] = df[[2]]
df['low'] = df[[3]]
df_giornaliero['max_high'] = df.groupby(['day'], sort=False)['high'].max()
df_giornaliero['min_low'] = df.groupby(['day'], sort=False)['low'].min()
df_giornaliero['24h_volatility'] = (df_giornaliero['max_high'] - df_giornaliero['min_low']) / df_giornaliero['min_low']
df_giornaliero['correlation'] = df_giornaliero['24h_change'] / df_giornaliero['24h_change']
df_principale = df_giornaliero.drop(['close', 'open'], axis = 1, inplace = False)
df_principale = df_principale.drop([0, 1, 2, 3, 4], axis = 1, inplace = False)
columns = ['24h_change']
df_principale_24h = df_principale[columns]
columns = ['24h_volatility']
df_principale_volatility = df_principale[columns]
columns = ['correlation']
df_principale_correlation = df_principale[columns]
columns = ['max_high']
df_principale_high = df_principale[columns]
columns = ['min_low']
df_principale_low = df_principale[columns]
df_principale_24h.columns = [id_coin]
df_principale_volatility.columns = [id_coin]
df_principale_correlation.columns = [id_coin]
df_principale_low.columns = [id_coin]
df_principale_high.columns = [id_coin]

count = 0
i = 0
for id_coin in coins_id_list:
    if(id_coin != 'bitcoin'):
        if(count == 16):
            t.sleep(90)
            count = 0
        hist_data = cg.get_coin_ohlc_by_id(id = id_coin, vs_currency = 'btc', days = '30', interval = 'daily')
        df = pd.DataFrame(hist_data)
        df['day'] = df[[0]]
        df['day'] = pd.to_datetime(df['day']/1000, unit = 's').dt.date
        df['close'] = df[[4]]
        df['open'] = df[[1]]
        df_with_first_row_per_day = df.groupby('day').first()
        df_with_last_row_per_day = df.groupby('day').last()
        df_giornaliero = df_with_last_row_per_day
        df_giornaliero['24h_change'] = (df_with_last_row_per_day['close'] - df_with_first_row_per_day['open']) / df_with_first_row_per_day['open'] - df_principale_24h['bitcoin']
        df['high'] = df[[2]]
        df['low'] = df[[3]]
        df_giornaliero['max_high'] = df.groupby(['day'], sort=False)['high'].max()
        df_giornaliero['min_low'] = df.groupby(['day'], sort=False)['low'].min()
        df_giornaliero['24h_volatility'] = (df_giornaliero['max_high'] - df_giornaliero['min_low']) / df_giornaliero['min_low']
        df_giornaliero['correlation'] = df_giornaliero['24h_change'] / df_principale_24h['bitcoin']
        df_principale = df_giornaliero.drop(['close', 'open'], axis = 1, inplace = False)
        df_principale = df_principale.drop([0, 1, 2, 3, 4], axis = 1, inplace = False)
        columns = ['24h_change']
        df_24h = df_principale[columns]
        df_24h.columns = [id_coin]
        columns = ['24h_volatility']
        df_volatility = df_principale[columns]
        df_volatility.columns = [id_coin]
        columns = ['correlation']
        df_correlation = df_principale[columns]
        df_correlation.columns = [id_coin]
        columns = ['max_high']
        df_high = df_principale[columns]
        df_high.columns = [id_coin]
        columns = ['min_low']
        df_low = df_principale[columns]
        df_low.columns = [id_coin]
        df_principale_24h = pd.concat([df_principale_24h, df_24h], axis = 1)
        df_principale_volatility = pd.concat([df_principale_volatility, df_volatility], axis = 1)
        df_principale_correlation = pd.concat([df_principale_correlation, df_correlation], axis = 1)
        df_principale_low = pd.concat([df_principale_low, df_low], axis = 1)
        df_principale_high = pd.concat([df_principale_high, df_high], axis = 1)
        count += 1
        i += 1
        print(i)

df_24h = df_principale_24h
df_principale_24h = df_principale_24h.T
df_principale_24h['sum'] = df_principale_24h.sum(axis = 1)
df_principale_24h = df_principale_24h.sort_values('sum', ascending = False)
df_principale_volatility.to_excel('volatility.xlsx')
df_principale_correlation.to_excel('correlation.xlsx')
df_principale_high.to_excel('high.xlsx')
df_principale_low.to_excel('low.xlsx')
