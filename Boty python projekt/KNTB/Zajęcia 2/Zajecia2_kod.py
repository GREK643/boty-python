#Install libraries
#pip install python-binance
#pip install pandas
#pip install plotly

from binance.client import Client
import plotly.graph_objects as go
import pandas as pd

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
                close=df['Close'])])
fig.show()
