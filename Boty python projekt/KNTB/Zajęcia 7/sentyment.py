from psaw import PushshiftAPI
import pandas as pd
import datetime as dt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
from binance.client import Client
import kntb
import time
from keys import secret_key, api_key

analyzer= SentimentIntensityAnalyzer()


# jesli:
#compound >= 0.05 - pozytywna wiadomosc
#compound <= -0.05 - negatywna wiadomosc
#pomiedzy -0.05 i 0.05 neutralny wydzwiek 

df = pd.DataFrame(['BTC to the moon'], columns=['body'])
df['compound'] = [analyzer.polarity_scores(v)['compound'] for v in df['body']]

df = pd.DataFrame(['BTC to the moon :)'], columns=['body'])
df['compound'] = [analyzer.polarity_scores(v)['compound'] for v in df['body']]

df = pd.DataFrame(['BTC to the moon :) SHIT'], columns=['body'])
df['compound'] = [analyzer.polarity_scores(v)['compound'] for v in df['body']]


df = pd.DataFrame(['BTC to the moon :('], columns=['body'])
df['compound'] = [analyzer.polarity_scores(v)['compound'] for v in df['body']]

client = Client(api_key,secret_key)

#kupno po 25 
buy_for=25



coin_list = {
    'BTC': ['BTC', 'Bitcoin'],
    'LTC': ['LTC','Litecoin'],
    'DOGE': ['DOGE', 'Dogecoin'],
    'XRP': ['XRP', 'Ripple'],
    'ETH': ['ETH', 'Ethereum'],
}

api = PushshiftAPI()


while True:

    for coin in list(coin_list.keys()):

        hour = dt.datetime.now() - timedelta(hours=1)
        now = dt.datetime.now()

        start_epoch=int(hour.timestamp())
        end_epoch=int(now.timestamp())

        search = str('(' + coin_list[coin][0] + ')' + '|' + '(' + coin_list[coin][1] + ')')

        api_request_generator = api.search_comments(q=search, after = start_epoch, before=end_epoch,subreddit=['wallstreetbets','wallstreetbetsOGs','cryptocurrency'] ,filter=['author', 'date', 'title', 'body', 'url', 'subreddit', 'score'])

        df=pd.DataFrame([comment.d_ for comment in api_request_generator])

        df['compound'] = [analyzer.polarity_scores(v)['compound'] for v in df['body']]

        #jesli średnia z wiadomości ma wydźwięk pozytywny, mamy powyej 25 USDT oraz nie mamy tego coina w portfelu to kupuje
        #(moga być jakieś grosze, więc na testnet i live trzeba też to uwzgędnić, dla jsonów będzie 0, bo sprzedajemy fake'owe liczby)

        if df['compound'].mean() > 0 and kntb.get_balance()['USDT'] > 25 and kntb.get_balance()[coin] == 0:
            quant = round(buy_for/float(client.get_orderbook_ticker(symbol=coin+'USDT')['askPrice']),8)
            kntb.market_order_buy(coin+'-USDT', quantity=quant)
            print('BUY', coin)

        #jesli średnia jest negatywna i posiadamy tego coina to go sprzedajemy
        if df['compound'].mean() < 0 and kntb.get_balance()[coin] > 0:
            quant = kntb.get_balance()[coin]*float(client.get_orderbook_ticker(symbol=coin+'-USDT')['bidPrice'])
            kntb.market_order_sell(coin+'-USDT', quantity=quant)
            print('SELL', coin)

    #time sleep na godzine
    time.sleep(3600)



