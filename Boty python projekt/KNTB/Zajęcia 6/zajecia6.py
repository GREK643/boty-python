import time
import json
import hmac
import hashlib
import requests
from urllib.parse import urljoin, urlencode
import pandas as pd
from keys import api_key, secret_key
import pprint

API_KEY = api_key
SECRET_KEY = secret_key
BASE_URL = 'https://api.binance.com'

headers = {
    'X-MBX-APIKEY': API_KEY
}


##################GET PRICE###########################
PATH = '/api/v3/ticker/price'
params = {
    'symbol': 'ETHUSDT'
}

url = urljoin(BASE_URL, PATH)
r = requests.get(url, headers=headers, params=params)
output = r.json()

###################ORDERBOOK##########################

PATH = '/api/v1/depth'
params = {
    'symbol': 'BTCUSDT',
    'limit': 10
}

url = urljoin(BASE_URL, PATH)
r = requests.get(url, headers=headers, params=params)
output = r.json()
################LIMIT ORDER#############################

PATH = '/api/v3/order'
timestamp = int(time.time() * 1000)
params = {
    'symbol': 'ETHUSDT',
    'side': 'BUY',
    'type': 'LIMIT',
    'timeInForce': 'GTC',
    'quantity': 0.005,
    'price': 2000.0,
    'timestamp': timestamp
}

query_string = urlencode(params)
params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = urljoin(BASE_URL, PATH)
r = requests.post(url, headers=headers, params=params)

r.json()
#################DELETE ORDER##############################
PATH = '/api/v3/order'
timestamp = int(time.time() * 1000)
params = {
    'symbol': 'ETHUSDT',
    'orderId': '8432809024',
    'timestamp': timestamp
}

query_string = urlencode(params)
params['signature'] = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

url = urljoin(BASE_URL, PATH)
r = requests.delete(url, headers=headers, params=params)
r.json()
#################COINMARKETCAP#######################

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=5000'
headers = {
'Accept': 'application/json',
'Accept-Encoding': 'deflate, gzip',
'X-CMC_PRO_API_KEY': 'API_KEY_CMC',
}
r = requests.get(url, headers=headers)
response = r.json()

numb_of_coins = response['status']['total_count'] #Number of scaped coins

pprint.pprint(response['data'])

table=[]
#Scrap data about coins
for i in response['data']:
    name = response['name']
    market_cap = response['quote']['USD']['market_cap']
    price = response['quote']['USD']['price']
    percent_change_1h = response['quote']['USD']['percent_change_1h']
    percent_change_24h = response['quote']['USD']['percent_change_24h']
    percent_change_7d = response['quote']['USD']['percent_change_7d']
    volume_24h = response['quote']['USD']['volume_24h']
    num_market_pairs = response['num_market_pairs']
    symbol = response['symbol']
    table.append([name, price, percent_change_1h, percent_change_24h, percent_change_7d, market_cap, volume_24h, num_market_pairs, symbol ])
    i+=1

#create table from list
df = pd.DataFrame(table, columns=['Name', 'Price', '1H', '24H', '7D', 'MarketCap', 'Volume24H', 'Pairs', 'Symbol']).dropna()
df['1H'] = df['1H'].round(2)
df['24H'] = df['24H'].round(2)
df['7D'] = df['7D'].round(2)
df = df.loc[(df['24H'] >= 15) & (df['7D'] >= 15) & (df['MarketCap'] >= 10000000) & (df['Pairs'] >= 7)]


import requests

url = "https://api.binance.com/api/v3/ticker/price?symbol=ETHBTC"

payload={} 
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
