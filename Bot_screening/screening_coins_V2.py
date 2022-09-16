import pandas as pd

number_coins = int(input("Quante coin ti servono?\n"))
if(number_coins > 100):
    range1 = (number_coins//200) + 1
    range2 = (number_coins//100) + 1
    print(range1)
    print(range2)

direction = input ("In che direzione voui calcolare i cumulativi?\n"
                    "0 -> Da oggi andando indietro\n"
                    "1 -> Viceversa\n")

cumulatives = []
cumulatives = input("Inserisci il numero di giorni dei cumulativi che ti servono\n")

df_principale = pd.read_excel('storico.xlsx')

#creo i dataframe con le classifiche incrementali
leaderboard = []
for num in cumulatives:
    df_24h_sum = df_24h.iloc[(31-num) : 31].sum()
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
    df_principale_24h.to_excel(writer, sheet_name = '24h_change')
    counter = 1
    for df in leaderboard:
        df.to_excel(writer, sheet_name = str(counter) + 'd')
        counter += 1

first = pd.read_excel('leaderboards.xlsx', sheet_name = '1d')
first.columns = ['Coin', 'Cumulative', 'Rank']
first.drop('Rank', inplace = True, axis = 1)
first.set_index('Coin', inplace = True)
df_principale_24h = pd.read_excel('leaderboards.xlsx', sheet_name = '24h_change')

leaderboard = []
for num in range(1, 30):
    first_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(num) + 'd')
    second_df = pd.read_excel('leaderboards.xlsx', sheet_name = str(num+1) + 'd')
    first_df.columns = ['Coin', 'Cumulative', 'Rank1']
    second_df.columns = ['Coin', 'Cumulative', 'Rank2']
    first_df.drop('Cumulative', inplace = True, axis = 1)
    df = second_df.merge(first_df, on = 'Coin')
    df['Change'] = df['Rank1'] - df['Rank2']
    df.drop(['Rank1', 'Rank2'], inplace = True, axis = 1)
    df.set_index('Coin', inplace = True)
    leaderboard.append(df)

with pd.ExcelWriter('leaderboards.xlsx') as writer:  
    df_principale_24h.to_excel(writer, sheet_name = '24h_change')
    counter = 1
    for df in leaderboard:
        if(counter == 1):
            first.to_excel(writer, sheet_name = '1d')
            counter += 1
        else:
            df.to_excel(writer, sheet_name = str(counter) + 'd')
            counter += 1