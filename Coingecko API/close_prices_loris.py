import pandas as pd
import datetime as dt
import time as t
import plotly.graph_objects as go
from plotly.offline import plot
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

cg.ping()

df_close_prices = pd.read_excel(open('Master_Download_Prices.xlsx', 'rb'), sheet_name='Close_Usd') 

data = []
# always inserting new rows at the first position - last row will be always on top    
data.insert(0, {'n_columns+1': 'id_coin'})
data.insert(0, {'n_columns+1': 'id_coin'})
data.insert(0, {'n_columns+1': 'n_columns+1'})

new_column = pd.DataFrame(data)
#pd.concat([pd.DataFrame(data), df], ignore_index=True)



print(df_close_prices)