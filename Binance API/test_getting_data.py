from http import client
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
import pandas as pd
import api_keys
import mplfinance as mpf

client = Client(api_keys.API_KEY, api_keys.SECRET)

tickers = client.get_all_tickers()      #to get all the pairs available on binance
print(tickers)             

tickers[0]              #to get the first ticker
tickers[1]              #to get the second ticker
tickers[0]['symbol']    #to get only the symbol
tickers[0]['price']     #to get only the price (it's a string, per convertirlo float(...))

ticker_df = pd.DataFrame(tickers)   #lo converto in un data frame su cui poter lavorare tramite pandas
ticker_df.head(18)                  #prendo i primi 18 elementi
ticker_df.tail(4)                   #prendo gli ultimi 4 elementi

ticker_df.set_index('symbol', inplace=True)    #uso il simbolo come indice per il data set, implace = true per modificare la lista esistente
ticker_df.loc['BTCUSDT']            #gli dico quale valore dell'indice voglio prendere
ticker_df.loc['BTCUSDT']['price']   #come prima ma prendo solo il prezzo

depth = client.get_order_book(symbol='ETHBTC')          #prendo l'order book

depth_df = pd.DataFrame(depth['bids'])      #visualizzo solo i bids
depth_df.columns = ['Price', 'Volume']      #formatto l'order book in una tabella
depth_df.head()

depth_df.dtypes         #mi dice che tipo sono gli oggetti

historical = client.get_historical_klines('ETHBTC', Client.KLINE_INTERVAL_1DAY, '1 Jan 2011')       #simbolo, time frame, punto di partenza (ci sono altri parametri che si possono mettere)

#Restituisce:
#orario di apertura
#apertura
#high giornaliero
#low giornaliero
#chiusura
#volume
#orario di chiusura
#quote asset number
#numero di trade
#taker buy base asset volume
#taker buy quote asset volume
#ignora

hist_df = pd.DataFrame(historical)
hist_df.head
hist_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time', 'Quote Asset Volume', 'Number Of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
hist_df.shape       #numero righe e numero colonne

hist_df.dtypes      #tipo dei dati (bisogna preprocessarli per poterli usare)
hist_df['Close Time'] = pd.to_datetime(hist_df['Close Time']/1000, unit = 's')
hist_df['Open Time'] = pd.to_datetime(hist_df['Open Time']/1000, unit = 's')
numeric_columns = [ 'Open', 'High', 'Low', 'Close', 'Volume', 'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
hist_df[numeric_columns] = hist_df[numeric_columns].apply(pd.to_numeric, axis=1)        #posso usare una lista per farli tutti insieme

hist_df.describe()      #restituisce delle statistiche
hist_df.info()          #restituisce altre informazioni sui dati

mpf.plot(hist_df.set_index('Close Time').tail(100))         #grafico con gli ultimi 100 dati ordinati per il tempo di chiusura
mpf.plot(hist_df.set_index('Close Time').tail(100), type='candle', style='charles')         #grafico con le candele 
mpf.plot(hist_df.set_index('Close Time').tail(100), type='candle', style='charles', volume=True)        #grafico con anche il volume
mpf.plot(hist_df.set_index('Close Time').tail(100), type='candle', style='charles', volume=True, title='ETHBTC Last 100 Days', mav=(10,20))     #aggiungo il titolo e le medie mobili a 10 e 20 giorni 