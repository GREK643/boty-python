#Połączenie z testnetem

from binance.client import Client
import pprint

client = Client('n4lwdo0AfSYFoRc4NC9PN9NTuXR2pSN3OoSBD6Ftxnx0IbGn05lutkMojcQgF79G',
                '10M42R4fZ9TT1scWJE9jhlgeMYAZpUB7DPj5rATr59ZVD0lpFzPsCfn38w2lvNvt',
                 testnet=True) 

##############ZLECENIA MARKET####################

client.get_asset_balance('ETH')
client.get_asset_balance('USDT')

##MARKET##
order = client.create_order(
    symbol='RIFUSDT',
    side='BUY',
    type='MARKET',
    quantity=100)


pprint.pprint(order)
orders = client.get_all_orders(symbol='RIFUSDT')
pprint.pprint(orders)

#################INNE ZLECENIA MARKET###################

order = client.create_order(
    symbol='BNBBTC',
    side='SELL',
    type='MARKET',
    quoteOrderQty=0.5)

###STOP-LOSS##
order = client.create_order(
    symbol = 'BTCUSDT', 
    side = 'SELL', 
    type = 'STOP_LOSS', 
    quantity = 0.03, 
    stopPrice = 2000)


##TAKE-PROFIT## 

order = client.create_order(
    symbol = 'RIFUSDT', 
    side = 'SELL', 
    type = 'TAKE_PROFIT', 
    quantity = 0.03, 
    stopPrice = 3000)


############################LIMIT##########################

order = client.create_order(
    symbol='RIFUSDT',
    side='SELL',
    type='LIMIT',
    timeInForce='GTC',
    quantity='100',
    price='0.1634')

orders = client.get_open_orders(symbol='ETHUSDT')
pprint.pprint(orders)

##################FILTRY###############################

info = client.get_symbol_info('ETHUSDT')
depth = client.get_order_book(symbol='ETHUSDT')
lower_price = float(depth['asks'][0][0]) - float(info['filters'][0]['tickSize'])

pprint.pprint(info)

order = client.create_order(
    symbol='ETHUSDT',
    side='SELL',
    type='LIMIT',
    timeInForce='GTC',
    quantity=str(round(0.01*4/3,4)),
    price='800')

pprint.pprint(info)

###########################INNE ZLECENIA LIMIT##########################

##STOP-LIMIT##
order = client.create_order(
    symbol = 'ETHUSDT', 
    side = 'SELL', 
    type = 'STOP_LOSS_LIMIT', 
    timeInForce = 'GTC', 
    quantity = 0.01, 
    price = 2850, 
    stopPrice = 2800)

##TAKE-PROFIT-LIMIT##
order = client.create_order(
    symbol = 'ETHUSDT', 
    side = 'SELL', 
    type = 'TAKE_PROFIT_LIMIT', 
    timeInForce = 'GTC', 
    quantity = 0.01, 
    price = 2900, 
    stopPrice = 3000)

#############################TRICKOWE ZLECENIA###################

##oco (One-cancels-the-other)##
order = client.create_oco_order(
    symbol='BTCUSDT',
    side='SELL',
    quantity=2,
    stopPrice='2011',
    price='2100')

##FOK##
order = client.create_order(
    symbol='ETHUSDT',
    side='BUY',
    type='LIMIT',
    timeInForce='FOK',
    quantity=2,
    price=2000)

##IOC##
order = client.create_order(
    symbol='ETHUSDT',
    side='BUY',
    type='LIMIT',
    timeInForce='IOC',
    quantity=2,
    price=2000)

##############POZOSTAŁE OPERACJE NA ORDERACH####################

#Order status
order = client.get_order(symbol='RIFUSDT',orderId='52422775')

#Cancel order
result = client.cancel_order(symbol='MLNUSDT',orderId='35276317')

client.cancel_order()
##############ENDPOINTY####################

info = client.get_account()
pprint.pprint(info)


####################FEES##########################

from keys import api_key, secret_key
client = Client(api_key,secret_key) 

# get fees for all symbols
fees = client.get_trade_fee()
pprint.pprint(fees)

# get fee for one symbol
fees = client.get_trade_fee(symbol='BNBBTC')
pprint.pprint(fees)

#Details 
details = client.get_asset_details()
pprint.pprint(details)


pprint.pprint(client.get_symbol_info('ETHUSDT'))
