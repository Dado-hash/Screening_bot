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

df_principale = pd.read_excel('closes.xlsx')
df_principale.set_index('Close time', inplace = True)

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

list_cum = []
for cum in cumulatives:
    df_sheet = pd.read_excel('leaderboards.xlsx', sheet_name= str(cum) + 'd')
    df_sheet = df_sheet.rename(columns={'Change': 'Change ' + str(cum) + 'd'})
    list_cum.append(df_sheet)
df_cums = pd.concat(list_cum, axis = 1)
df_cums.to_excel('cumulatives_changes.xlsx')

