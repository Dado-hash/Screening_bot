import api_keys_arcadia
import pandas as pd
from datetime import timezone, datetime
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
                                                            
client = Client(api_keys_arcadia.API_KEY, api_keys_arcadia.SECRET)
klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_1DAY, "1 Gen, 2022", "31 Gen, 2022")
klines = pd.DataFrame(klines)
klines = klines[[4]]
klines["Giorni"] = 5
klines.rename(columns = {4:'Gen'}, inplace = True)
for num in range(31):
    klines.iloc[num, 1] = num
klines.set_index("Giorni", inplace=True)   
print(klines)                                                                
klines.to_csv("btc_prices")                                                  