import api_keys_arcadia
import pandas as pd
from datetime import timezone, datetime
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager

df_old = pd.read_csv("btc_prices")                                          
df_old.set_index('Giorni', inplace = True)                                                           
client = Client(api_keys_arcadia.API_KEY, api_keys_arcadia.SECRET)
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Apr, 2022", "30 Apr, 2022")
klines = pd.DataFrame(klines)
klines = klines[[4]]
klines["Giorni"] = 5
klines.rename(columns = {4:'Apr'}, inplace = True)
for num in range(30):
    klines.iloc[num, 1] = num
klines.set_index("Giorni", inplace=True)
df_old = pd.concat([df_old, klines], ignore_index = True, axis = 1)    
print(df_old)                                                                
df_old.to_csv("btc_prices")                                                  