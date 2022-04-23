# SMA Crossover Strategy

# BUY
# SMA(10) or SMA(20) calculated with a shorter period crosses 
# above the SMA calculated with a longer period :SMA(50).
# IF SMA(10) > SMA(50) => BUY

# SELL
# SMA(50) calculated with a longer period crosses 
# above the SMA calculates with a shorter period: SMA(10) or SMA(20).
# IF SMA(50) > SMA(10) => SELL

import pandas as pd 
import datetime
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import math
# from tenacity import retry
from termcolor import colored as cl 
import numpy as np

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (15, 8)

from nseta.resources.resources import *

__all__ = ['sma_crossover_strategy']

def sma_crossover_strategy(df):
    df.set_index('Date')
    df.index = pd.to_datetime(df.index)
    df = update_sma_indicator_values(df)
    strategy = update_strategy_position(df)
    symbol = df.loc[:,'Symbol'].iloc[0]
    if calculate_roi(strategy, symbol):
        plot_strategy(strategy, symbol)

def sma(data, n):
    sma = data.rolling(window = n).mean()
    return pd.DataFrame(sma)

def update_sma_indicator_values(df):
    n = [20, 50]
    for i in n:
        df[f'sma_{i}'] = sma(df['Close'], i)
    return df

def run_sma_crossover_strategy(data, short_window, long_window):
    sma1 = short_window
    sma2 = long_window
    buy_price = []
    sell_price = []
    sma_signal = []
    signal = 0
    
    for i in range(len(data)):
        if sma1[i] > sma2[i]:
            if signal != 1:
                buy_price.append(data[i])
                sell_price.append(np.nan)
                signal = 1
                sma_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                sma_signal.append(0)
        elif sma2[i] > sma1[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(data[i])
                signal = -1
                sma_signal.append(-1)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                sma_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            sma_signal.append(0)
            
    return buy_price, sell_price, sma_signal


def update_strategy_position(df):
    buy_price, sell_price, signal = run_sma_crossover_strategy(df['Close'], df['sma_20'], df['sma_50'])
    position = []
    for i in range(len(signal)):
        if signal[i] > 1:
            position.append(0)
        else:
            position.append(1)
            
    for i in range(len(df['Close'])):
        if signal[i] == 1:
            position[i] = 1
        elif signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]
            
    # CONSOLIDATING LISTS TO DATAFRAME
    sma_20 = pd.DataFrame(df['sma_20']).rename(columns = {0:'sma_20'})
    sma_50 = pd.DataFrame(df['sma_50']).rename(columns = {0:'sma_50'})
    close_price = df['Close']
    date = df['Date']
    buy_price = pd.DataFrame(buy_price).rename(columns = {0:'buy_price'}).set_index(df.index)
    sell_price = pd.DataFrame(sell_price).rename(columns = {0:'sell_price'}).set_index(df.index)
    signal = pd.DataFrame(signal).rename(columns = {0:'sma_signal'}).set_index(df.index)
    position = pd.DataFrame(position).rename(columns = {0:'sma_position'}).set_index(df.index)
    
    signal = signal.loc[~signal.index.duplicated(keep='first')]
    position = position.loc[~position.index.duplicated(keep='first')]
    date = date.loc[~date.index.duplicated(keep='first')]
    buy_price = buy_price.loc[~buy_price.index.duplicated(keep='first')]
    sell_price = sell_price.loc[~sell_price.index.duplicated(keep='first')]
    close_price = close_price.loc[~close_price.index.duplicated(keep='first')]
    sma_20 = sma_20.loc[~sma_20.index.duplicated(keep='first')]
    sma_50 = sma_50.loc[~sma_50.index.duplicated(keep='first')]

    frames = [date, close_price, sma_20, sma_50, buy_price, sell_price, signal, position]
    strategy = pd.concat(frames, join = 'inner', axis = 1)
    strategy.reset_index(drop=True, inplace=True)
    return strategy

def calculate_roi(strategy, symbol):
    strategy_copy = strategy.copy(deep=True)
    strategy_copy = strategy_copy.dropna(subset=['buy_price', 'sell_price'], how='all')
    if len(strategy_copy) <= 0:
        print('Not enough data yet')
        return False
    strategy_copy = strategy_copy.loc[:,['Date', 'Close', 'sma_signal', 'sma_position']]
    strategy_copy['Symbol'] = symbol
    df_ret = pd.DataFrame(np.diff(strategy_copy['Close'])).rename(columns = {0:'returns'})

    strategy_copy.loc[:,'sma_margin'] = 0
    strategy_copy.loc[:,'sma_returns'] = 0
    investment_value_initial = resources.backtest().init_cash
    investment_value = investment_value_initial

    for i in range(len(df_ret)):
        returns = df_ret.loc[:,'returns'].iloc[i]*strategy_copy.loc[:,'sma_position'].iloc[i]
        strategy_copy.loc[:,'sma_margin'].iloc[i+1] = returns
        number_of_stocks = math.floor(investment_value/strategy_copy.loc[:,'Close'].iloc[i])
        returns = number_of_stocks*strategy_copy.loc[:,'sma_margin'].iloc[i+1]
        strategy_copy.loc[:,'sma_returns'].iloc[i+1] = returns
        investment_value = investment_value + returns

    print('\n{}\n'.format(strategy_copy.to_string(index=False)))
    total_investment_ret = round(sum(strategy_copy['sma_returns']), 2)
    profit_percentage = round((total_investment_ret/investment_value_initial)*100,3)
    print(cl('\nProfit gained from the SMA strategy by investing INR 100k in {} : {}\n'.format(symbol, total_investment_ret), attrs = ['bold']))
    print(cl('\nProfit percentage of the SMA strategy : {} %\n'.format(profit_percentage), attrs = ['bold']))
    return True

def plot_strategy(df, symbol):
    # PLOTTING SMA TRADE SIGNALS
    xAxisFmt = mdates.DateFormatter('%Y-%m-%d')
    df.set_index('Date', inplace=True)
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    intraday_df = df[df.index >= today]
    if len(intraday_df) > 1:
        xAxisFmt = mdates.DateFormatter('%H:%M')
    else:
        df.index = pd.to_datetime(df.index)
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
    plt.gca().xaxis.set_major_formatter(xAxisFmt)
    
    plt.plot(df['Close'], label = '{} Close Prices'.format(symbol), linewidth = 5, alpha = 0.3)
    plt.plot(df['sma_20'], alpha = 0.6, label = 'SMA 20')
    plt.plot(df['sma_50'], alpha = 0.6, label = 'SMA 50')
    plt.scatter(df.index, df['buy_price'], marker = '^', s = 200, color = 'darkblue', label = 'BUY SIGNAL')
    plt.scatter(df.index, df['sell_price'], marker = 'v', s = 200, color = 'crimson', label = 'SELL SIGNAL')
    plt.legend(loc = 'lower right')
    plt.title('{} SMA CROSSOVER TRADING SIGNALS'.format(symbol))
    plt.ylabel('{} Stock Closing Prices'.format(symbol))
    plt.xlabel('Date/Time')
    plt.grid(True)
    plt.gcf().autofmt_xdate()
    plt.show()
