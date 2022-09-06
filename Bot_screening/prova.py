import pandas as pd

'''first_df = pd.read_excel('leaderboards.xlsx', sheet_name = '1d')
second_df = pd.read_excel('leaderboards.xlsx', sheet_name = '2d')
df_principale_24h = pd.read_excel('leaderboards.xlsx', sheet_name = '24h_change')
first_df.columns = ['Coin', 'Cumulative', 'Rank1']
second_df.columns = ['Coin', 'Cumulative', 'Rank2']
first_df.drop('Cumulative', inplace = True, axis = 1)
df = second_df.merge(first_df, on = 'Coin')
df['Change'] = df['Rank1'] - df['Rank2']
df.drop('Rank1', inplace = True, axis = 1)
print(df)'''

first = pd.read_excel('leaderboards.xlsx', sheet_name = '1d')
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
    df.set_index('Coin', inplace = True, axis = 1)
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