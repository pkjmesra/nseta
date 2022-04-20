# Bollinger Bands Range Crossover Strategy

# BUY
# If the stock price of the previous day is greater than the previous day's lower band 
# and the current stock price is lesser than the current day’s lower band. 
# IF PREV_STOCK > PREV_LOWERBB & CUR_STOCK < CUR_LOWER_BB => BUY

# SELL
# If the stock price of the previous day is lesser than the previous day’s upper band 
# and the current stock price is greater than the current day’s upper band, 
# IF PREV_STOCK < PREV_UPPERBB & CUR_STOCK > CUR_UPPER_BB => SELL

from os import symlink
import pandas as pd 
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
from termcolor import colored as cl 
import numpy as np

from nseta.resources.resources import *

__all__ = ['bbands_range_crossover_strategy']

def bbands_range_crossover_strategy(df):
    df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df = update_bbands_indicator_values(df)
    strategy = update_strategy_position(df)
    symbol = df.loc[:,'Symbol'].iloc[0]
    if calculate_roi(strategy, symbol):
        plot_strategy(strategy, symbol)

def sma(data, window):
    sma = data.rolling(window = window).mean()
    return sma

def bb(data, sma, window):
    std = data.rolling(window = window).std()
    upper_bb = sma + std * 2
    lower_bb = sma - std * 2
    return upper_bb, lower_bb

def update_bbands_indicator_values(df):
    df['sma_20'] = sma(df['Close'], 20)
    df['upper_bb'], df['lower_bb'] = bb(df['Close'], df['sma_20'], 20)
    return df

def run_bbands_range_crossover_strategy(data, lower_bb, upper_bb):
    buy_price = []
    sell_price = []
    bb_signal = []
    signal = 0
    
    for i in range(len(data)):
        if data[i-1] > lower_bb[i-1] and data[i] < lower_bb[i]:
            if signal != 1:
                buy_price.append(data[i])
                sell_price.append(np.nan)
                signal = 1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        elif data[i-1] < upper_bb[i-1] and data[i] > upper_bb[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(data[i])
                signal = -1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            bb_signal.append(0)
            
    return buy_price, sell_price, bb_signal

def update_strategy_position(df):
    buy_price, sell_price, bb_signal = run_bbands_range_crossover_strategy(df['Close'], df['lower_bb'], df['upper_bb'])
    position = []
    for i in range(len(bb_signal)):
        if bb_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)
            
    for i in range(len(df['Close'])):
        if bb_signal[i] == 1:
            position[i] = 1
        elif bb_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]
            
    upper_bb = df['upper_bb']
    lower_bb = df['lower_bb']
    close_price = df['Close']
    date = df['Date']
    sma = df['sma_20']
    bb_buy = pd.DataFrame(buy_price).rename(columns = {0:'buy_price'}).set_index(df.index)
    bb_sell = pd.DataFrame(sell_price).rename(columns = {0:'sell_price'}).set_index(df.index)
    bb_signal = pd.DataFrame(bb_signal).rename(columns = {0:'bb_signal'}).set_index(df.index)
    position = pd.DataFrame(position).rename(columns = {0:'bb_position'}).set_index(df.index)
    bb_signal = bb_signal.loc[~bb_signal.index.duplicated(keep='first')]
    position = position.loc[~position.index.duplicated(keep='first')]
    upper_bb = upper_bb.loc[~upper_bb.index.duplicated(keep='first')]
    lower_bb = lower_bb.loc[~lower_bb.index.duplicated(keep='first')]
    date = date.loc[~date.index.duplicated(keep='first')]
    bb_buy = bb_buy.loc[~bb_buy.index.duplicated(keep='first')]
    bb_sell = bb_sell.loc[~bb_sell.index.duplicated(keep='first')]
    close_price = close_price.loc[~close_price.index.duplicated(keep='first')]
    sma = sma.loc[~sma.index.duplicated(keep='first')]

    frames = [date, close_price, upper_bb, sma, lower_bb, bb_buy, bb_sell, bb_signal, position]
    strategy = pd.concat(frames, join = 'inner', axis = 1)
    strategy = strategy.loc[:,['Date', 'Close', 'upper_bb', 'sma_20', 'lower_bb', 'buy_price', 'sell_price', 'bb_signal', 'bb_position']]
    strategy.reset_index(drop=True, inplace=True)
    return strategy

def calculate_roi(strategy, symbol):
    strategy_copy = strategy.copy(deep=True)
    strategy_copy = strategy_copy.dropna(subset=['buy_price', 'sell_price'], how='all')
    if len(strategy_copy) <= 0:
        print('Not enough data yet')
        return False
    strategy_copy = strategy_copy.loc[:,['Date', 'Close', 'bb_signal', 'bb_position']]
    strategy_copy.loc[:,'Symbol'] = symbol
    df_ret = pd.DataFrame(np.diff(strategy_copy['Close'])).rename(columns = {0:'returns'})

    strategy_copy.loc[:,'bb_margin'] = 0
    strategy_copy.loc[:,'bb_returns'] = 0
    investment_value_initial = resources.backtest().init_cash
    investment_value = investment_value_initial

    for i in range(len(df_ret)):
        try:
            returns = df_ret.loc[:,'returns'].iloc[i]*strategy_copy.loc[:,'bb_position'].iloc[i]
            strategy_copy.loc[:,'bb_margin'].iloc[i+1] = returns
        except:
            pass
        number_of_stocks = math.floor(investment_value/strategy_copy.loc[:,'Close'].iloc[i])
        returns = number_of_stocks*strategy_copy.loc[:,'bb_margin'].iloc[i+1]
        strategy_copy.loc[:,'bb_returns'].iloc[i+1] = returns
        investment_value = investment_value + returns

    print('\n{}\n'.format(strategy_copy.to_string(index=False)))
    total_investment_ret = round(sum(strategy_copy['bb_returns']), 2)
    profit_percentage = round((total_investment_ret/investment_value_initial)*100,3)
    print(cl('\nProfit gained from the BB strategy by investing INR 100k in {} : {}\n'.format(symbol, total_investment_ret), attrs = ['bold']))
    print(cl('\nProfit percentage of the BB strategy : {} %\n'.format(profit_percentage), attrs = ['bold']))
    return True

def plot_strategy(df, symbol):
    plt.style.use('fivethirtyeight')
    plt.rcParams['figure.figsize'] = (20, 10)
    df.set_index('Date', inplace=True)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.plot(df.index, df['Close'])
    df['Close'].plot(label = '{} CLOSE Prices'.format(symbol), alpha = 0.6, linewidth = 1, color = 'skyblue')
    df['upper_bb'].plot(label = 'UPPER BB 20', linestyle = '--', linewidth = 1, color = 'black')
    df['sma_20'].plot(label = 'MIDDLE BB 20', linestyle = '--', linewidth = 1, color = 'red')
    df['lower_bb'].plot(label = 'LOWER BB 20', linestyle = '--', linewidth = 1, color = 'black')
    plt.scatter(df.index, df['buy_price'], marker = '^', color = 'green', label = 'BUY', s = 200)
    plt.scatter(df.index, df['sell_price'], marker = 'v', color = 'red', label = 'SELL', s = 200)
    plt.gcf().autofmt_xdate()
    plt.xlabel('Date')
    plt.ylabel('{} Stock Closing Prices'.format(symbol))
    plt.title('{} BB STRATEGY TRADING SIGNALS'.format(symbol))
    plt.legend(loc = 'upper right')
    plt.show()
