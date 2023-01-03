import json
import time
import requests


def get_balance():
    with open('balance.json', 'r') as f:
        data = json.load(f)
    return data

def get_symbol_balance(symbol):
    with open('balance.json', 'r') as f:
        data = json.load(f)[symbol]
    return data

def get_transactions():
    with open('transactions.json', 'r') as f:
        transactions = json.load(f)    
    return transactions
    
    
def market_order_buy(symbol, quantity):
    
    with open('balance.json', 'r') as f:
        data = json.load(f)
    
    asks = requests.get('https://api.binance.com/api/v3/depth?limit=100&symbol={}'.format(symbol.replace('-', ''))).json()['asks']
    
    have = 0
    transaction = 0
    missing = quantity
    i=0
    while have < quantity:
        if float(asks[i][1]) >= missing:
            transaction+=missing*float(asks[i][0])
            have=quantity
        else:
            transaction+= float(asks[i][0])*float(asks[i][1])
            missing = missing-float(asks[i][1])
            have = float(asks[i][1])
            i+=1
    if transaction > data[symbol.split('-')[1]]:
        return 'There is not that much money in the account'
    else:
        
        data[symbol.split('-')[1]] = data[symbol.split('-')[1]] - transaction
        data[symbol.split('-')[0]] += quantity
        
        with open('balance.json', 'w') as outfile:
            json.dump(data, outfile)
            
        with open('transactions.json', 'r') as f:
            transactions = json.load(f)
            
        transactions[time.time()] = {'Type': 'BUY', 'Symbol': symbol, 'Quantity' : quantity, 'Price': transaction}
        
        with open('transactions.json', 'w') as outfile:
            json.dump(transactions, outfile)

        return [symbol, quantity, transaction]



def market_order_sell(symbol, quantity):
    
    with open('balance.json', 'r') as f:
        data = json.load(f)
        
    
    if data[symbol.split('-')[0]] < quantity:
        return 'Za malo kryptowalut'
    
    bids = requests.get('https://api.binance.com/api/v3/depth?limit=100&symbol={}'.format(symbol.replace('-', ''))).json()['bids']

    have = 0
    transaction = 0
    missing = quantity
    i=0
    while have < quantity:
        if float(bids[i][1]) >= missing:
            transaction+=missing*float(bids[i][0])
            have=quantity
        else:
            transaction+= float(bids[i][0])*float(bids[i][1])
            missing = missing-float(bids[i][1])
            have = float(bids[i][1])
            i+=1
    if transaction > data[symbol.split('-')[1]]:
        return 'Nie ma tyle srodkow na koncie'
    else:
        
        data[symbol.split('-')[1]] = data[symbol.split('-')[1]] + transaction
        data[symbol.split('-')[0]] = data[symbol.split('-')[0]] - quantity
        
        with open('balance.json', 'w') as outfile:
            json.dump(data, outfile)
            
            
        with open('transactions.json', 'r') as f:
            transactions = json.load(f)
        transactions[time.time()] = {'Type': 'SELL', 'Symbol': symbol, 'Quantity' : quantity, 'Price': transaction}
        
        with open('transactions.json', 'w') as outfile:
            json.dump(transactions, outfile)
        
        return [symbol, quantity, transaction]