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

# modifica per una migliore visualizzazione dei dati e creazione di una progress bar
pd.set_option("display.precision", 8)


def progress_bar(progress, total, color=colorama.Fore.YELLOW):
    percent = 100 * (progress / float(total))
    bar = '*' * int(percent) + '-' * (100 - int(percent))
    print(color + f"\r|{bar}| {percent:.2f}%", end="\r")
    if (progress == total):
        print(colorama.Fore.GREEN + f"\r|{bar}| {percent:.2f}%", end="\r")
        print(colorama.Fore.RESET)


# serie di parametri richiesti all'utente per poter generare l'elaborazione desiderata
type_storico = input("Quale storico vuoi usare (binance o coingecko)?\n")

direction = input("In che direzione voui calcolare i cumulativi?\n"
                  "0 -> Da oggi andando indietro\n"
                  "1 -> Da un giorno specifico in avanti\n")
direction = int(direction)

if (direction):
    start = input("Da che giorno vuoi partire?\n")
    start = int(start)
else:
    start = input("Fino a che giorno vuoi arrivare?\n")
    start = int(start)

all = input("Seleziona che tipo di cumulativi ti servono:\n"
            "0 -> Solo alcuni\n"
            "1 -> Tutti\n")
all = int(all)

if (all):
    cumulatives = list(range(start + 1))
    cumulatives.remove(0)
else:
    cumulatives = input("Inserisci il numero di giorni dei cumulativi che ti servono\n")
    cumulatives = cumulatives.split()
    for i in range(len(cumulatives)):
        cumulatives[i] = int(cumulatives[i])
totale = (len(cumulatives) * 5) - 3
progresso = 0

order = input('Li vuoi ordinati per Score o per performance?\n'
              '0 -> Performance\n'
              '1 -> Score\n')
order = int(order)

# viene caricato lo storico a seconda di quale fonte si desidera usare
if (type_storico == "binance"):
    df_principale = pd.read_excel('closes.xlsx', index_col=0)
    df_principale.set_index('Close time', inplace=True)
else:
    df_principale = pd.read_excel('storico.xlsx', index_col=0)
df_for_index = df_principale.tail(start)

# vengono caricati i dati dai file riguardanti le medie
df_SMA6 = pd.read_excel('above6.xlsx', index_col=0)
df_SMA6.set_index('Close time', inplace=True)
df_SMA11 = pd.read_excel('above11.xlsx', index_col=0)
df_SMA11.set_index('Close time', inplace=True)
df_SMA21 = pd.read_excel('above21.xlsx', index_col=0)
df_SMA21.set_index('Close time', inplace=True)
df_SMA6 = df_SMA6.T
df_SMA11 = df_SMA11.T
df_SMA21 = df_SMA21.T
df_SMA6 = df_SMA6.iloc[:, len(df_SMA6.columns) - start: len(df_SMA6.columns)].copy()
df_SMA11 = df_SMA11.iloc[:, len(df_SMA11.columns) - start: len(df_SMA11.columns)].copy()
df_SMA21 = df_SMA21.iloc[:, len(df_SMA21.columns) - start: len(df_SMA21.columns)].copy()

# dal file con lo storico vengono calcolate le performance giornaliere e creati i cumulativi
leaderboard = []
if not direction:
    for num in cumulatives:
        pd.set_option('display.float_format', lambda x: '%.7f' % x)
        df_24h_sum = df_principale.T
        df_24h_sum = ((df_24h_sum.iloc[:, len(df_24h_sum.columns) - 1] - df_24h_sum.iloc[:,
                                                                         len(df_24h_sum.columns) - num]) / df_24h_sum.iloc[
                                                                                                           :,
                                                                                                           len(df_24h_sum.columns) - num]) * 100
        df_24h_sum = df_24h_sum.sort_values(ascending=False)
        df_24h_sum = df_24h_sum.to_frame()
        df = df_24h_sum.copy()[[]]
        df_24h_sum.columns = ['Cumulative']
        df_24h_sum.reset_index(drop=True, inplace=True)
        ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
        ranking.columns = ['Rank']
        ranking['Cumulative'] = df_24h_sum['Cumulative']
        df_24h_sum = pd.concat([df_24h_sum, ranking], axis=1)
        df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']  # cambiare cumulative con la data
        df_24h_sum.drop('Trash', axis=1, inplace=True)
        df_24h_sum.index = df.index
        leaderboard.append(df_24h_sum)
        progresso += 1
        progress_bar(progresso, totale)
else:
    for num in cumulatives:
        pd.set_option('display.float_format', lambda x: '%.10f' % x)
        df_24h_sum = df_principale.T
        df_24h_sum = ((df_24h_sum.iloc[:, (len(df_24h_sum.columns) - 1 - start + num)] - df_24h_sum.iloc[:, (
                                                                                                                    len(df_24h_sum.columns) - 1 - start)]) / df_24h_sum.iloc[
                                                                                                                                                             :,
                                                                                                                                                             (
                                                                                                                                                                     len(df_24h_sum.columns) - 1 - start)]) * 100
        df_24h_sum = df_24h_sum.sort_values(ascending=False)
        df_24h_sum = df_24h_sum.to_frame()
        df = df_24h_sum.copy()[[]]
        df_24h_sum.columns = ['Cumulative']
        df_24h_sum.reset_index(drop=True, inplace=True)
        ranking = pd.DataFrame(range(1, 1 + len(df_24h_sum)))
        ranking.columns = ['Rank']
        ranking['Cumulative'] = df_24h_sum['Cumulative']
        df_24h_sum = pd.concat([df_24h_sum, ranking], axis=1)
        df_24h_sum.columns = ['Cumulative', 'Rank', 'Trash']
        df_24h_sum.drop('Trash', axis=1, inplace=True)
        df_24h_sum.index = df.index
        leaderboard.append(df_24h_sum)
        progresso += 1
        progress_bar(progresso, totale)

# i cumulativi vengono salvati in un file
cycles = leaderboard
with pd.ExcelWriter('leaderboards.xlsx') as writer:
    counter = 0
    for df in leaderboard:
        df.to_excel(writer, sheet_name=str(cumulatives[counter]) + 'd')
        counter += 1
        progresso += 1
        progress_bar(progresso, totale)

# ai cumulativi viene inizialmente aggiunta una colonna con il rank di ogni coin
df_totale = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[0]) + 'd')
titolo = str(cumulatives[0]) + 'd'
df_totale.columns = ['Coin', titolo, 'Rank']
df_totale.drop('Rank', inplace=True, axis=1)
df_totale.set_index('Coin', inplace=True)
for num in range(len(cumulatives)):
    if (cumulatives[num] != cumulatives[0]):
        second_df = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[num]) + 'd')
        titolo = str(cumulatives[num]) + 'd'
        second_df.columns = ['Coin', titolo, 'Rank']
        second_df.drop('Rank', inplace=True, axis=1)
        second_df.set_index('Coin', inplace=True)
        df_totale = df_totale.merge(second_df, on='Coin')
        df_totale = df_totale.copy()
        progresso += 1
        progress_bar(progresso, totale)

# creazione primo dati primo giorno su cui poi attaccare gli altri
first = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[0]) + 'd')
first.columns = ['Coin', 'Cumulative', 'Rank']
first.drop('Rank', inplace=True, axis=1)
first.set_index('Coin', inplace=True)
first_temp = first['Cumulative']
first_temp = first_temp.to_frame()
first_temp.columns = ['24h_change']
first_temp = first_temp.reset_index()
first_temp = first_temp.sort_values(by='24h_change', ascending=False)
conditions = [
    (first_temp.index < 10),
    (first_temp.index >= 10) & (first_temp.index < 15),
    (first_temp.index >= 15) & (first_temp.index < 20)
]
values = [3, 2, 1]
first_temp['Day_rank'] = np.select(conditions, values)
first_temp.drop('24h_change', inplace=True, axis=1)
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
df_first_day_SMA21 = df_SMA21[first_day_SMA21_index]
df_first_day_SMA21 = df_first_day_SMA21.to_frame()
df_first_day_SMA21.index.name = 'Coin'
df_first_day_SMA21.columns = ['Above SMA21']
first = first.merge(df_first_day_SMA6, on='Coin')
first = first.merge(df_first_day_SMA11, on='Coin')
first = first.merge(df_first_day_SMA21, on='Coin')

# ogni cumulativo viene aggiunto a quello del primo giorno
leaderboard = []
df_score_cum = first_temp.copy()
df_score_cum.set_index('Coin', inplace=True)
df_score_cum.columns = ['Score']
df_score_cum['Score'] = df_score_cum['Score'].astype(float)
df_score_temp = df_score_cum['Score'].copy()
df_score_temp = df_score_temp.to_frame()
for num in range(len(cumulatives) - 1):
    df_score_temp['Score'] = 0
    first_df = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[num]) + 'd')
    second_df = pd.read_excel('leaderboards.xlsx', sheet_name=str(cumulatives[num + 1]) + 'd')
    first_df.columns = ['Coin', 'Cumulative', 'Rank1']
    second_df.columns = ['Coin', 'Cumulative', 'Rank2']
    first_temp = first_df.copy()
    second_temp = second_df.copy()
    first_temp.drop('Rank1', inplace=True, axis=1)
    second_temp.drop('Rank2', inplace=True, axis=1)
    first_temp.set_index('Coin', inplace=True)
    second_temp.set_index('Coin', inplace=True)
    first_temp.columns = ['Cumulative1']
    second_temp.columns = ['Cumulative2']
    first_temp = first_temp.merge(second_temp, on='Coin')
    first_temp['24h_change'] = (first_temp['Cumulative2'] - first_temp['Cumulative1'])
    first_temp.drop(['Cumulative1', 'Cumulative2'], inplace=True, axis=1)
    first_temp = first_temp.sort_values(by='24h_change', ascending=False)
    first_temp = first_temp.reset_index()
    conditions = [
        (first_temp.index < 10),
        (first_temp.index >= 10) & (first_temp.index < 15),
        (first_temp.index >= 15) & (first_temp.index < 20)
    ]
    values = [3, 2, 1]
    first_temp['Day_rank'] = np.select(conditions, values)
    first_temp.drop('24h_change', inplace=True, axis=1)
    first_temp.set_index('Coin', inplace=True)
    first_df.drop('Cumulative', inplace=True, axis=1)
    df = second_df.merge(first_df, on='Coin')
    df['Change'] = (df['Rank1'] - df['Rank2']) / 10
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
    df.drop(['Rank1', 'Rank2'], inplace=True, axis=1)
    df.set_index('Coin', inplace=True)
    df_score_temp_change = df['Change'].copy()
    df_score_temp_change.index = df.index
    df_score_temp_type = df['Type of change'].copy()
    df_score_temp_type.index = df.index
    df_score_temp = df_score_temp_change  # .add(df_score_temp_type)
    first_day_SMA6_index = df_SMA6.columns[num + 1]
    df_first_day_SMA6 = df_SMA6[first_day_SMA6_index]
    df_first_day_SMA6 = df_first_day_SMA6.to_frame()
    df_first_day_SMA6.index.name = 'Coin'
    df_first_day_SMA6.columns = ['Above SMA6']
    first_day_SMA11_index = df_SMA11.columns[num + 1]
    df_first_day_SMA11 = df_SMA11[first_day_SMA11_index]
    df_first_day_SMA11 = df_first_day_SMA11.to_frame()
    df_first_day_SMA11.index.name = 'Coin'
    df_first_day_SMA11.columns = ['Above SMA11']
    first_day_SMA21_index = df_SMA21.columns[num + 1]
    df_first_day_SMA21 = df_SMA6[first_day_SMA21_index]
    df_first_day_SMA21 = df_first_day_SMA21.to_frame()
    df_first_day_SMA21.index.name = 'Coin'
    df_first_day_SMA21.columns = ['Above SMA21']
    df_day_rank = first_temp['Day_rank'].copy()
    df = df.merge(df_first_day_SMA6, on='Coin')
    df = df.merge(df_first_day_SMA11, on='Coin')
    df = df.merge(df_first_day_SMA21, on='Coin')
    df = df.merge(first_temp, on='Coin')
    df_score_temp_SMA6 = df['Above SMA6']
    df_score_temp_SMA11 = df['Above SMA11']
    df_score_temp_SMA21 = df['Above SMA21']
    df_score_temp_top10 = df['Top 10']
    df_score_temp_day_rank = df['Day_rank']
    df_score_temp = reduce(lambda a, b: a.add(b, fill_value=0),
                           [df_score_temp, df_score_temp_SMA6, df_score_temp_SMA11, df_score_temp_SMA21,
                            df_score_temp_top10, df_score_temp_day_rank])
    df_score_temp = df_score_temp.to_frame()
    df_score_temp.columns = ['Score']
    df_score_cum = df_score_cum.add(df_score_temp)
    df = df.merge(df_score_cum, on='Coin')
    if (order):
        df = df.sort_values(by='Score', ascending=False)
    leaderboard.append(df)
    progresso += 1
    progress_bar(progresso, totale)

# creo il file di base con i cumulativi suddivisi per giorno e un foglio con la performance delle coin giorno per giorno
if (start < 10):
    t.sleep(1)
if (direction):
    filename = 'leaderboard_forward.xlsx'
else:
    filename = 'leaderboard_backward.xlsx'
with pd.ExcelWriter(filename) as writer:
    df_totale.to_excel(writer, sheet_name='Aggregate')
    first.to_excel(writer, sheet_name=str(cumulatives[0]) + 'd')
    counter = 1
    for df in leaderboard:
        df.to_excel(writer, sheet_name=str(cumulatives[counter]) + 'd')
        counter += 1
        progresso += 1
        progress_bar(progresso, totale)

# creo il file finale aggregando tutti i cumulativi, i punteggi e lo score totale
list_cum = []
for cum in cumulatives:
    df_sheet = pd.read_excel(filename, sheet_name=str(cum) + 'd')
    df_sheet = df_sheet.rename(columns={'Change': 'Change ' + str(cum) + 'd'})
    df_sheet.drop(['Type of change', 'Top 10', 'Above SMA6', 'Above SMA11', 'Above SMA21', 'Day_rank'], inplace=True,
                  axis=1)
    list_cum.append(df_sheet)
df_cums = pd.concat(list_cum, axis=1)
if (direction):
    filename = 'cumulative_changes_forward.xlsx'
else:
    filename = 'cumulative_changes_backward.xlsx'
df_cums.to_excel(filename)

# unisco i due score
union = input('Vuoi combinare gli score? (occorre aver creato entrambi i file prima)\n'
              '0 -> No\n'
              '1 -> Sì\n')
union = int(union)
if (union):
    list_score = []
    for cum in cumulatives:
        if (cum != 1):
            df_sheet_backward = pd.read_excel('leaderboard_backward.xlsx', sheet_name=str(cum) + 'd')
            df_sheet_forward = pd.read_excel('leaderboard_forward.xlsx', sheet_name=str(cum) + 'd')
            df_sheet_forward.set_index('Coin', inplace=True)
            df_sheet_backward.set_index('Coin', inplace=True)
            df_sheet_forward = df_sheet_forward.rename(columns={'Score': 'Score_f'})
            df_sheet_backward.drop(
                ['Cumulative', 'Change', 'Type of change', 'Top 10', 'Above SMA6', 'Above SMA11', 'Above SMA21',
                 'Day_rank'], inplace=True, axis=1)
            df_sheet_forward.drop(
                ['Cumulative', 'Change', 'Type of change', 'Top 10', 'Above SMA6', 'Above SMA11', 'Above SMA21',
                 'Day_rank'], inplace=True, axis=1)
            df_sheet_tot = df_sheet_backward.merge(df_sheet_forward, on='Coin')
            df_sheet_tot['Score_tot_' + str(cum) + 'd'] = df_sheet_tot['Score'] + df_sheet_tot['Score_f']
            df_sheet_tot.drop(['Score', 'Score_f'], inplace=True, axis=1)
            df_sheet_tot = df_sheet_tot.sort_values(by=('Score_tot_' + str(cum) + 'd'), ascending=False)
            list_score.append(df_sheet_tot)
    df_score_tot = pd.concat(list_score, axis=1)
    df_score_tot.to_excel('score.xlsx')
