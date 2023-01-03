from binance.client import Client
import json
from keys import api_key, private_key
import pandas as pd
import time
from time import sleep
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import traceback
import os
os.chdir('C:/Users/Kacper/Desktop/studia/Boty python projekt/Analiza/KNTB-bot-grid-old-data')


def get_balance():
    with open('balance.json', 'r') as f:
        balance = json.load(f)
    return balance

def dump_balance(balance):
    with open('balance.json', 'w') as outfile:
        json.dump(balance, outfile)

def get_transactions():
    with open('transactions.json', 'r') as f:
        transactions = json.load(f)
    return transactions

def dump_transactions(transactions):
    with open('transactions.json', 'w') as outfile:
        json.dump(transactions, outfile)

def get_local_balance():
    with open('local_balance.json', 'r') as f:
        local_balance = json.load(f)
    return local_balance

def dump_local_balance(local_balance):
    with open('local_balance.json', 'w') as outfile:
        json.dump(local_balance, outfile)

def create_grid_lines(bottom_limit, upper_limit, line_dist):
    grid_lines = []
    for i in range(bottom_limit, upper_limit, line_dist):
        grid_lines.append(i)
    return grid_lines

def get_current_position(current_price, grid_lines):
    for i in range(0, len(grid_lines) - 1):
        if(grid_lines[i] <= current_price and current_price < grid_lines[i+1]):
            lower_trigger = grid_lines[i]
            upper_trigger = grid_lines[i+1]
            return lower_trigger, upper_trigger
    return 0, 0

def find(lst, key, value): # do znajdowania waluty w słowniku słowników
    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return -1

def update_local_balance(local_balance, side, symbol, quantity, quote_quantity):
    if side == 'SELL':
        local_balance[find(local_balance, 'asset', symbol[0:3])]['free'] = float(local_balance[find(local_balance, 'asset', symbol[0:3])]['free']) - quantity
        local_balance[find(local_balance, 'asset', symbol[3:6])]['free'] = float(local_balance[find(local_balance, 'asset', symbol[3:6])]['free']) + float(quote_quantity)
        return local_balance
    elif side == 'BUY':
        local_balance[find(local_balance, 'asset', symbol[0:3])]['free'] = float(local_balance[find(local_balance, 'asset', symbol[0:3])]['free']) + quantity
        local_balance[find(local_balance, 'asset', symbol[3:6])]['free'] = float(local_balance[find(local_balance, 'asset', symbol[3:6])]['free']) - (quote_quantity)
        return local_balance

local_balance = get_local_balance()

client = Client(api_key,
                private_key,
                testnet=True) 

engine = create_engine('sqlite:///' + 'transactions.db') 
metadata = MetaData(engine)
metadata.reflect()

session_factory = sessionmaker(bind=engine)
session_scoped_factory = scoped_session(session_factory)
session = session_scoped_factory()

print(client.get_account()['balances'])

symbol = 'ETHUSDT'
upper_limit = 1190
bottom_limit = 0
line_dist = 1 # odległość między liniami
order_value = 10 # w USDT, ile chcemy za każdym razem kupić/sprzedać
grid_lines = create_grid_lines(bottom_limit, upper_limit, line_dist)

try:
    data = pd.DataFrame(client.get_ticker())
    lower_trigger, upper_trigger = get_current_position(float(data.loc[data['symbol'] == symbol]['openPrice'].values[0]), grid_lines)
    while True:
       

        data = pd.DataFrame(client.get_ticker())
        current_price = float(data.loc[data['symbol'] == symbol]['openPrice'].values[0])
        if current_price > upper_trigger:
            try:
                order = client.create_order(
                    symbol = symbol,
                    side = 'SELL',
                    type = 'MARKET',
                    quantity = round(order_value/current_price, 4)
                )
                transactions = get_transactions()
                balance = client.get_account()['balances']
                dump_balance(balance)
                local_balance = update_local_balance(local_balance, 'SELL', symbol, round(order_value/current_price, 4), float(order['cummulativeQuoteQty']))
                dump_local_balance(local_balance)
                transactions[time.time()] = {'Type': 'SELL', 'Symbol': symbol, 'Quantity': round(order_value/current_price, 4), 'Trigger Price': current_price, 
                'Transaction Price': order['fills'][0]['price'],'Quote quantity': order['cummulativeQuoteQty'], 'Binance Balance': balance, 'Local Balance': local_balance}
                dump_transactions(transactions)
               
                print('Type: ' + 'SELL' + ' Symbol: ' + symbol + ' Quantity: ' + str(round(order_value/current_price, 4)) + ' Trigger Price: ' + str(current_price) + 
                ' Transaction Price: ' + order['fills'][0]['price'] +   ' Quote quantity: '+ order['cummulativeQuoteQty'] + ' Binance Balance: ' + str(json.dumps(balance)) +
                ' Local Balance: ' + str(json.dumps(local_balance)) + ' Time: ' + str(datetime.now()))
            except:
                print('Failed to create a SELL order. TIME:' + str(datetime.now()))
                traceback.print_exc()
                with open('traceback.txt', 'w+') as f:
                        f.write('Failed to create a SELL order. TIME:' + str(datetime.now()) + '\n')
                        traceback.print_exc(file=f)
            lower_trigger, upper_trigger = get_current_position(current_price, grid_lines)
        elif current_price < lower_trigger:
            try:
                order = client.create_order(
                    symbol = symbol,
                    side = 'BUY',
                    type = 'MARKET',
                    quantity = round(order_value/current_price, 4)
                )
                transactions = get_transactions()
                balance = client.get_account()['balances']
                dump_balance(balance)
                local_balance = update_local_balance(local_balance, 'BUY', symbol, round(order_value/current_price, 4), float(order['cummulativeQuoteQty']))
                dump_local_balance(local_balance)
                transactions[time.time()] = {'Type': 'BUY', 'Symbol': symbol, 'Quantity': round(order_value/current_price, 4), 'Price': current_price, 
                'Transaction Price': order['fills'][0]['price'],'Quote quantity': order['cummulativeQuoteQty'], 'Binance Balance': balance, 'Local Balance': local_balance}
                dump_transactions(transactions)
            
                print('Type: ' + 'BUY' + ' Symbol: ' + symbol + ' Quantity: ' + str(round(order_value/current_price, 4)) + ' Trigger Price: ' + str(current_price) + 
                ' Transaction Price: ' + order['fills'][0]['price'] + ' Quote quantity: ' + order['cummulativeQuoteQty'] + ' Binance Balance: ' + str(json.dumps(balance)) +
                ' Local Balance: ' + str(json.dumps(local_balance)) + ' Time: ' + str(datetime.now()))
            except:
                print('Failed to create a BUY order. TIME:' + str(datetime.now()))
                traceback.print_exc()
                with open('traceback.txt', 'w+') as f:
                        f.write('Failed to create a BUY order. TIME:' + str(datetime.now()) + '\n')
                        traceback.print_exc(file=f)
            lower_trigger, upper_trigger = get_current_position(current_price, grid_lines)
        else:
            transactions = get_transactions()
            # balance = client.get_account()['balances']
            # dump_balance(balance)
            # local_balance = update_local_balance(local_balance, 'BUY', symbol, round(order_value/current_price, 4), order['cummulativeQuoteQty'])
            # dump_local_balance(local_balance)
            transactions[time.time()] = {'Type': 'NO TRANSACTION', 'Symbol': symbol, 'Price': current_price, 
            # 'Binance Balance': balance, 'Local Balance': local_balance
            }
            dump_transactions(transactions)

            print('No transaction. Current price = ' + str(current_price) + ' Time: ' + str(datetime.now()))
        sleep(30)
except KeyboardInterrupt:
    dump_balance(client.get_account()['balances'])
    with engine.begin() as connection:
        pd.read_json('transactions.json').transpose().to_sql('transactions', con=connection, if_exists='append')

    print('Zapis do bazy danych - start')
    session.commit()
    print('Zapis do bazy danych - koniec')
    print('Bot stopped working')
