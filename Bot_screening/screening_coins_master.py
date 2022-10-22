import pandas as pd
import colorama
import datetime as dt
import time as t
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI    
import numpy as np
from functools import reduce

cg = CoinGeckoAPI()
cg.ping()

#modifica per una migliore visualizzazione dei dati e creazione di una progress bar
pd.set_option("display.precision", 8)
def progress_bar(progress, total, color = colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if (progress == total):
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r") 
        print(colorama.Fore.RESET)

#serie di parametri richiesti all'utente per poter generare l'elaborazione desiderata
type_storico = input("Quale storico vuoi usare (binance o coingecko)?\n")

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

order = input('Li vuoi ordinati per Score o per performance\n'
              '0 -> Performance\n'
              '1 -> Score\n')
order = int(order)

#viene caricato lo storico a seconda di quale fonte si desidera usare
if(type_storico == "binance"):
    df_principale = pd.read_excel('closes.xlsx', index_col = 0)
    df_principale.set_index('Close time', inplace = True)
else:
    df_principale = pd.read_excel('storico.xlsx', index_col = 0)
df_for_index = df_principale.tail(start)

#vengono caricati i dati dai file riguardanti le medie
df_SMA6 = pd.read_excel('above6.xlsx', index_col = 0)
df_SMA6.set_index('Close time', inplace = True)
df_SMA11 = pd.read_excel('above11.xlsx', index_col = 0)
df_SMA11.set_index('Close time', inplace = True)
df_SMA21 = pd.read_excel('above21.xlsx', index_col = 0)
df_SMA21.set_index('Close time', inplace = True)
df_SMA6 = df_SMA6.T
df_SMA11 = df_SMA11.T
df_SMA21 = df_SMA21.T
df_SMA6 = df_SMA6.iloc[:, len(df_SMA6.columns) - start : len(df_SMA6.columns)].copy()
df_SMA11 = df_SMA11.iloc[:, len(df_SMA11.columns) - start : len(df_SMA11.columns)].copy()
df_SMA21 = df_SMA21.iloc[:, len(df_SMA21.columns) - start : len(df_SMA21.columns)].copy()

#dal file con lo storico vengono calcolate le performance giornaliere e creati i cumulativi
leaderboard = []
if(not direction):
    for num in cumulatives:
        pd.set_option('display.float_format', lambda x: '%.7f' % x)
        df_24h_sum = df_principale.T
        df_24h_sum = ((df_24h_sum.iloc[:, len(df_24h_sum.columns)-1] - df_24h_sum.iloc[:, len(df_24h_sum.columns)-num]) / df_24h_sum.iloc[:, len(df_24h_sum.columns)-num])*100
        df_24h_sum = df_24h_sum.sort_values(ascending = False)
        df_24h_sum = df_24h_sum.to_frame()
        df = df_24h_sum.copy()[[]]
        df_24h_sum.columns = ['Cumulative']
        df_24h_sum.reset_index(drop=True, inplace = True)
        ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
        ranking.columns = ['Rank']
        ranking['Cumulative'] = df_24h_sum['Cumulative']
        df_24h_sum = pd.concat([df_24h_sum, ranking], axis = 1)
        df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']    #cambiare cumulative con la data
        df_24h_sum.drop('Trash', axis = 1, inplace = True)     
        df_24h_sum.index = df.index
        leaderboard.append(df_24h_sum)
        progresso += 1
        progress_bar(progresso, totale)
else:
    for num in cumulatives:
        pd.set_option('display.float_format', lambda x: '%.10f' % x)
        df_24h_sum = df_principale.T
        df_24h_sum = ((df_24h_sum.iloc[:, (len(df_24h_sum.columns)-1-start + num)] - df_24h_sum.iloc[:, (len(df_24h_sum.columns)-1-start)]) / df_24h_sum.iloc[:, (len(df_24h_sum.columns)-1-start)]) * 100
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

#i cumulativi vengono salvati in un file
cycles = leaderboard
with pd.ExcelWriter('leaderboards.xlsx') as writer:  
    counter = 0
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(cumulatives[counter]) + 'd')
        counter += 1
        progresso += 1
        progress_bar(progresso, totale)

#ai cumulativi viene inizialmente aggiunta una colonna con il rank di ogni coin
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
        df_totale = df_totale.copy()
        progresso += 1
        progress_bar(progresso, totale)

#creazione primo dati primo giorno su cui poi attaccare gli altri
first = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[0]) + 'd')
first.columns = ['Coin', 'Cumulative', 'Rank']
first.drop('Rank', inplace = True, axis = 1)
first.set_index('Coin', inplace = True)
first_day_SMA6_index = df_SMA6.columns[0]
df_first_day_SMA6 = df_SMA6[first_day_SMA6_index]
df_first_day_SMA6 = df_first_day_SMA6.to_frame()
df_first_day_SMA6.index.name = 'Coin'
df_first_day_SMA6.columns = ['Above SMA6']
first_day_SMA11_index = df_SMA11.columns[0]
df_first_day_SMA11 = df_SMA11[first_day_SMA11_index]
df_first_day_SMA11 = df_first_day_SMA11.to_frame()
df_first_day_SMA11.index.name = 'Coin'
df_first_day_SMA11.columns = ['Above SMA11']
first_day_SMA21_index = df_SMA21.columns[0]
df_first_day_SMA21 = df_SMA6[first_day_SMA21_index]
df_first_day_SMA21 = df_first_day_SMA21.to_frame()
df_first_day_SMA21.index.name = 'Coin'
df_first_day_SMA21.columns = ['Above SMA21']
first = first.merge(df_first_day_SMA6, on = 'Coin')
first = first.merge(df_first_day_SMA11, on = 'Coin')
first = first.merge(df_first_day_SMA21, on = 'Coin')

#ogni cumulativo viene aggiunto a quello del primo giorno
leaderboard = []
df_score_cum = first['Cumulative']
df_score_cum = df_score_cum.to_frame()
df_score_cum.columns = ['Score']      
df_score_cum['Score'] = 0             
df_score_temp = df_score_cum['Score'] #dare un peso inferiore al cambio di posizione
df_score_temp = df_score_temp.to_frame()
for num in range(len(cumulatives)-1):
    df_score_temp['Score'] = 0
    first_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[num]) + 'd')
    second_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[num+1]) + 'd')
    first_df.columns = ['Coin', 'Cumulative', 'Rank1']
    second_df.columns = ['Coin', 'Cumulative', 'Rank2']
    first_df.drop('Cumulative', inplace = True, axis = 1)
    df = second_df.merge(first_df, on = 'Coin')
    df['Change'] = df['Rank1'] - df['Rank2']
    conditions = [
        (df['Change'].astype(float) > 0),
        (df['Change'].astype(float) < 0),
        (df['Change'].astype(float) == 0)
    ]
    values = [1, -1, 0]
    df['Type of change'] = np.select(conditions, values) 
    conditions = [
        (df.index < 10),
        (df.index >= 10) & (df.index < 15),
        (df.index >= 15) & (df.index < 20)
    ]
    values = [3, 2, 1]
    df['Top 10'] = np.select(conditions, values) 
    df.drop(['Rank1', 'Rank2'], inplace = True, axis = 1)
    df.set_index('Coin', inplace = True)
    df_score_temp_change = df['Change'].copy()
    df_score_temp_change.index = df.index
    df_score_temp_type = df['Type of change'].copy()
    df_score_temp_type.index = df.index
    df_score_temp = df_score_temp_change.add(df_score_temp_type)
    first_day_SMA6_index = df_SMA6.columns[num+1]
    df_first_day_SMA6 = df_SMA6[first_day_SMA6_index]
    df_first_day_SMA6 = df_first_day_SMA6.to_frame()
    df_first_day_SMA6.index.name = 'Coin'
    df_first_day_SMA6.columns = ['Above SMA6']
    first_day_SMA11_index = df_SMA11.columns[num+1]
    df_first_day_SMA11 = df_SMA11[first_day_SMA11_index]
    df_first_day_SMA11 = df_first_day_SMA11.to_frame()
    df_first_day_SMA11.index.name = 'Coin'
    df_first_day_SMA11.columns = ['Above SMA11']
    first_day_SMA21_index = df_SMA21.columns[num+1]
    df_first_day_SMA21 = df_SMA6[first_day_SMA21_index]
    df_first_day_SMA21 = df_first_day_SMA21.to_frame()
    df_first_day_SMA21.index.name = 'Coin'
    df_first_day_SMA21.columns = ['Above SMA21']
    df = df.merge(df_first_day_SMA6, on = 'Coin')
    df = df.merge(df_first_day_SMA11, on = 'Coin')
    df = df.merge(df_first_day_SMA21, on = 'Coin')
    df_score_temp_SMA6 = df['Above SMA6']
    df_score_temp_SMA11 = df['Above SMA11']
    df_score_temp_SMA21 = df['Above SMA21']
    df_score_temp_top10 = df['Top 10']
    df_score_temp = reduce(lambda a, b: a.add(b, fill_value=0), [df_score_temp, df_score_temp_SMA6, df_score_temp_SMA11, df_score_temp_SMA21, df_score_temp_top10])
    df_score_temp = df_score_temp.to_frame()
    df_score_temp.columns = ['Score']
    df_score_cum = df_score_cum.add(df_score_temp)
    df = df.merge(df_score_cum, on = 'Coin')
    if(order):
        df = df.sort_values(by = 'Score', ascending = False)
    leaderboard.append(df)
    progresso += 1
    progress_bar(progresso, totale)

#creo il file di base con i cumulativi suddivisi per giorno e un foglio con la performance delle coin giorno per giorno
with pd.ExcelWriter('leaderboards.xlsx') as writer:
    df_totale.to_excel(writer, sheet_name = 'Aggregate')
    first.to_excel(writer, sheet_name = str(cumulatives[0]) + 'd')
    counter = 1
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(cumulatives[counter]) + 'd')
        counter += 1
        progresso += 1
        progress_bar(progresso, totale)

#creo il file finale aggregando tutti i cumulativi, i punteggi e lo score totale
list_cum = []
for cum in cumulatives:
    df_sheet = pd.read_excel('leaderboards.xlsx', sheet_name= str(cum) + 'd')
    df_sheet = df_sheet.rename(columns={'Change': 'Change ' + str(cum) + 'd'})
    list_cum.append(df_sheet)
df_cums = pd.concat(list_cum, axis = 1)
df_cums.to_excel('cumulatives_changes.xlsx')