import pandas as pd

direction = input("In che direzione voui calcolare i cumulativi?\n"
                    "0 -> Da oggi andando indietro\n"
                    "1 -> Da un giorno specifico in avanti\n")
direction = int(direction)

if(direction):
    start = input("Da che giorno vuoi partire?\n")
    start = int(start)

all = input("Seleziona che tipo di cumulativi ti servono:\n"
            "0 -> Solo alcuni\n"
            "1 -> Tutti\n")

if(all):
    cumulatives = list(range(start + 1))
    cumulatives.remove(0)
else:
    cumulatives = input("Inserisci il numero di giorni dei cumulativi che ti servono\n")
    cumulatives = cumulatives.split()
    for i in range(len(cumulatives)):
        cumulatives[i] = int(cumulatives[i])

df_principale = pd.read_excel('storico.xlsx')
df_principale.set_index('day', inplace = True)

#creo i dataframe con le classifiche incrementali
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
        df_24h_sum = df_24h_sum.merge(ranking, on = 'Cumulative')
        df_24h_sum.index = df.index
        leaderboard.append(df_24h_sum)
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
        df_24h_sum = df_24h_sum.merge(ranking, on = 'Cumulative')
        df_24h_sum.index = df.index
        leaderboard.append(df_24h_sum)

with pd.ExcelWriter('leaderboards.xlsx') as writer:  
    counter = 0
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(cumulatives[counter]) + 'd')
        counter += 1

df_totale = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[0]) + 'd')
df_totale.columns = ['Coin', 'Cumulative', 'Rank']
df_totale.drop('Rank', inplace = True, axis = 1)
df_totale.set_index('Coin', inplace = True)
for num in range(len(cumulatives)):
    if(cumulatives[num] != cumulatives[0]):
        second_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(cumulatives[num]) + 'd')
        second_df.columns = ['Coin', 'Cumulative', 'Rank']
        second_df.drop('Rank', inplace = True, axis = 1)
        second_df.set_index('Coin', inplace = True)
        df_totale = df_totale.merge(second_df, on = 'Coin')

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
    df['Change'] = df['Rank2'] - df['Rank1']
    df.drop(['Rank1', 'Rank2'], inplace = True, axis = 1)
    df.set_index('Coin', inplace = True)
    leaderboard.append(df)

with pd.ExcelWriter('leaderboards.xlsx') as writer:
    df_totale.to_excel(writer, sheet_name = 'Aggregate')
    first.to_excel(writer, sheet_name = str(cumulatives[0]) + 'd')
    counter = 1
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(cumulatives[counter]) + 'd')
        counter += 1