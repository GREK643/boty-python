from binance.client import Client
import json
from keys import api_key, private_key
import pandas as pd
import time
from time import sleep
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime

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

symbol = 'BTCUSDT'
upper_limit = 50000
bottom_limit = 30000
line_dist = 100 # odległość między liniami
order_value = 500 # w USDT, ile chcemy za każdym razem kupić/sprzedać
grid_lines = create_grid_lines(bottom_limit, upper_limit, line_dist)

try:
    data = pd.DataFrame(client.get_ticker())
    lower_trigger, upper_trigger = get_current_position(float(data.loc[data['symbol'] == symbol]['openPrice'].values[0]), grid_lines)
    while True:
        data = pd.DataFrame(client.get_ticker())
        current_price = float(data.loc[data['symbol'] == symbol]['openPrice'].values[0])
        if current_price > upper_trigger:
            # try:
            order = client.create_order(
                symbol = symbol,
                side = 'SELL',
                type = 'MARKET',
                quantity = round(order_value/current_price, 4)
            )
            transactions = get_transactions()
            transactions[time.time()] = {'Type': 'SELL', 'Symbol': symbol, 'Quantity': round(order_value/current_price, 4), 'Price': current_price}
            dump_transactions(transactions)
            dump_balance(client.get_account()['balances'])
            print('Type: ' + 'SELL' + 'Symbol: ' + symbol + ' Quantity: ' + round(order_value/current_price, 4) + ' Price: ' + current_price + 
            ' Time: ' + str(datetime.now()))
            # except:
            #     print('Failed to create a SELL order')
            lower_trigger, upper_trigger = get_current_position(current_price, grid_lines)
        elif current_price < lower_trigger:
            # try:
            order = client.create_order(
                symbol = symbol,
                side = 'BUY',
                type = 'MARKET',
                quantity = round(order_value/current_price, 4)
            )
            transactions = get_transactions()
            transactions[time.time()] = {'Type': 'BUY', 'Symbol': symbol, 'Quantity': round(order_value/current_price, 4), 'Price': current_price}
            dump_transactions(transactions)
            dump_balance(client.get_account()['balances'])
            print('Type: ' + 'BUY' + 'Symbol: ' + symbol + ' Quantity: ' + round(order_value/current_price, 4) + ' Price: ' + current_price + 
            ' Time: ' + str(datetime.now()))
            # except:
            #    print('Failed to create a BUY order')
            lower_trigger, upper_trigger = get_current_position(current_price, grid_lines)
        else:
            transactions = get_transactions()
            transactions[time.time()] = {'Type': 'NO TRANSACTION', 'Symbol': symbol, 'Price': current_price}
            dump_transactions(transactions)
            print('No transaction. Current price = ' + str(current_price) + 
                ' Time: ' + str(datetime.now()))
        sleep(60)
except KeyboardInterrupt:
    dump_balance(client.get_account()['balances'])
    with engine.begin() as connection:
        pd.read_json('transactions.json').transpose().to_sql('transactions', con=connection, if_exists='append')

    print('Zapis do bazy danych - start')
    session.commit()
    print('Zapis do bazy danych - koniec')
    print('Bot stopped working')