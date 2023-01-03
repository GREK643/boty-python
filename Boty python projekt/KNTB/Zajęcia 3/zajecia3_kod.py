#Install libraries
#pip install python-binance
#pip install pandas
#pip install plotly

from binance.client import Client
import plotly.graph_objects as go
import pandas as pd
import pprint
import numpy as np

#Client definition
client = Client('','') 

#Download last 500 candlesticks for DOGEUSDT on 30 minutes interval - other intervals can be for example 1h/1d/5m etc.
candles = client.get_klines(symbol='DOGEUSDT', interval='30m')


df = pd.DataFrame(candles, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 
									'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 
									'Taker buy quote asset volume', 'Ignore'])
									

#Plot candlesticks

fig = go.Figure(data=[go.Candlestick(x=df['Close time'],
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close']),
                go.Scatter(x=df['Close time'], y=df['MA5'], line={'color':'blue'}),
                go.Scatter(x=df['Close time'], y=df['MA20'], line={'color':'violet'})])
fig.show()

#MA
df['MA5'] = df['Close'].rolling(window=5).mean()
df['MA20'] = df['Close'].rolling(window=20).mean()

#cuts

df['Signal'] = 0.0
df['Signal'] = np.where(df['MA5'] > df['MA20'], 1.0, 0.0)
df['Position'] = df['Signal'].diff()
df.loc[df['Signal']==1.0]


#timestamp to datetime
df['Data'] = pd.to_datetime(df['Close time'], unit='ms')

#Get Orderbook
orderbook = client.get_order_book(symbol='DOGEUSDT')

pd.DataFrame(orderbook['bids'], columns=['Price', 'Quantity'])

#24 tickers
tickers = client.get_ticker()

prices = client.get_all_tickers()

#Get first bid and ask entry in the order book for all markets.
tickers = client.get_orderbook_tickers()

#ticker for symbol
symbol_ticker = client.get_symbol_ticker(symbol='DOGEUSDT')
pprint.pprint(tickers)
