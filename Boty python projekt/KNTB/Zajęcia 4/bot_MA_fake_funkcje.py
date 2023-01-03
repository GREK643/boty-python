from binance.client import Client
from binance.enums import *
import plotly.graph_objects as go
import pandas as pd
import pprint
import numpy as np
import requests
import time
import kntb
#Client definition
client = Client('','') 


#pętla, żeby kod ciągle chodził z odstępami 60 sekund (time.sleep na końcu)
while True:

    candles = client.get_klines(symbol='DOGEUSDT', interval='1m', limit=50)

    df = pd.DataFrame(candles, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 
                                        'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 
                                        'Taker buy quote asset volume', 'Ignore'])


    df['MA5'] = df['Close'].rolling(window=5).mean()
    df['MA20'] = df['Close'].rolling(window=10).mean()

    #cuts

    df['Signal'] = 0.0
    df['Signal'] = np.where(df['MA5'] > df['MA20'], 1.0, 0.0)
    df['Position'] = df['Signal'].diff()


    #pobranie salda walut na koncie, to jest podpięte pod real, więc teraz nie pójdzie.Funkcje na testowanie będą w czwartek.
    #Na razie możecie podstawić jakieś swoje wartości 
    balance_USDT = kntb.get_symbol_balance('USDT')
    balance_DOGE = kntb.get_symbol_balance('DOGE')

    #pobieranie tickera dla DOGEUSDT
    ticker = requests.get('https://www.binance.com/api/v3/ticker/price?symbol=DOGEUSDT')

    #cena z tickera
    price = float(ticker.json()['price'])


    #to taki przykład z 1000 doge, można pokombinować, zeby dało się sprzedać wszystkie coiny



    #warunki - jeśli pozycja w ostatnim wierszu dataframe = 1 (przecięcie na kupno zdefiniowane wyżej) i mamy 
    #w przeliczeniu środki żeby kupić ponad 1000 DOGE to kupujemy 
    if df.iloc[-1]['Position'] == 1 and balance_USDT/price > 1000 :
        #kupno 1000 DOGE
        buy = kntb.market_order_buy('DOGE-USDT', 1000)
        print('BUY {} {} for {}'.format(buy[1], buy[0], buy[2]))
    #sprzedaż jeśli ostatnia pozycja = -1 oraz mamy więcej niż 1000 DOGE na koncie, możemy też np w tym miejscu podstawić za 1000 zmienna balance_DOGE, żeby sprzedać całość
    elif df.iloc[-1]['Position'] == -1 and balance_DOGE > 1000:
            #sprzedaż 1000 doge
        sell = kntb.market_order_sell('DOGE-USDT', 1000)
        print('SELL {} {} for {}'.format(sell[1], sell[0], sell[2]))
            

    else:
        pass

    time.sleep(60) #wrzucamy time sleepa na kolejną świecę, bo działamy na 1h (3600 sekund)
    #z drugiej strony jakbyśmy odpalali na serwerze, zamiast pętli i time sleep, można ustawić harmonogram
    #zadań, żeby odpalało skrypt co godzinę, zaoszczędzi to mocy obliczeniowej
