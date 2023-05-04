# coding: utf-8

# There are many patterns for recognition
# top m, bottom w, head-shoulder top, head-shoulder bottom, elliott waves
# This is the Bottom W strategy implementation.
# top m is just the reverse of bottom w
# rules of bollinger bands and bottom w can be found in the following link:
# https://www.tradingview.com/wiki/Bollinger_Bands_(BB)

import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import math
from termcolor import colored as cl 

import copy
import numpy as np

from nseta.common.log import tracelog, default_logger
from nseta.resources.resources import *

__all__ = ['bollingerbandsBottomWStrategy']

class bollingerbandsBottomWStrategy:

    @tracelog
    def bbands_bottom_w_strategy(self, df, shouldplot=False):
        # df.set_index('Date')
        # df.index = pd.to_datetime(df.index)   
        signals=self.signal_generation(df)
        signals = signals.loc[:,['Date', 'std', 'close','mid_band', 'upper_band', 'lower_band', 'bb_signal', 'bb_position', 'coordinates']]
        signals = signals.reset_index(drop=True)
        # signals.set_index('Date')
        # signals.index = pd.to_datetime(signals.index) 
        default_logger().debug('\nSignal generated:\n{}'.format(signals[signals['bb_signal']!=0]))
        symbol = df.loc[:,'Symbol'].iloc[0]
        if self.calculate_roi(signals, symbol):
            if shouldplot:
                self.plot_strategy(signals, symbol)
        else:
            print('Sufficient signals for bottom W strategy could not be found for the given duration')
    #first step is to calculate moving average and moving standard deviation
    #we plus/minus two standard deviations on moving average
    #we get our upper, mid, lower_bands
    def bollinger_bands(self, df):
        data=copy.deepcopy(df)
        data['std']=data['close'].rolling(window=20,min_periods=20).std()
        data['mid_band']=data['close'].rolling(window=20,min_periods=20).mean()
        data['upper_band']=data['mid_band']+2*data['std']
        data['lower_band']=data['mid_band']-2*data['std']
        data = data.dropna(subset=['mid_band', 'upper_band', 'lower_band'], how='all')
        return data


    #the signal generation is a bit tricky
    #there are four conditions to satisfy
    #for the shape of w, there are five nodes
    #from left to right, top to bottom, l,k,j,m,i
    #when we generate signals
    #the iteration node is the top right node i, condition 4
    #first, we find the middle node j, condition 2
    #next, we identify the first bottom node k, condition 1
    #after that, we point out the first top node l
    #l is not any of those four conditions
    #we just use it for pattern visualization
    #finally, we locate the second bottom node m, condition 3
    #plz refer to the following link for my poor visualization
    # https://github.com/je-suis-tm/quant-trading/blob/master/preview/bollinger%20bands%20bottom%20w%20pattern.png
    @tracelog
    def signal_generation(self, data):
        
        #according to investopedia
        #for a double bottom pattern
        #we should use 3-month horizon which is 75
        period=75
        
        #alpha denotes the difference between price and bollinger bands
        #if alpha is too small, its unlikely to trigger a signal
        #if alpha is too large, its too easy to trigger a signal
        #which gives us a higher probability to lose money
        #beta denotes the scale of bandwidth
        #when bandwidth is larger than beta, it is expansion period
        #when bandwidth is smaller than beta, it is contraction period
        alpha = data.loc[:,'close'].iloc[0] * 0.01 # 0.0001 # TODO: Should be a much lower value for alpha?
        beta = alpha # 0.0001
        default_logger().debug('\nAlpha set to: {}'.format(alpha))
        df=self.bollinger_bands(data)
        df['bb_signal']=0
        
        #as usual, bb_position denotes the holding position
        #coordinates store five nodes of w shape
        #later we would use these coordinates to draw a w shape
        df['bb_position']=0
        df['coordinates']=''
        
        for i in range(period,len(df)):
            
            #moveon is a process control
            #if moveon==true, we move on to verify the next condition
            #if false, we move on to the next iteration
            #threshold denotes the value of node k
            #we would use it for the comparison with node m
            #plz refer to condition 3
            moveon=False
            threshold=0.0
            
            #bottom w pattern recognition
            #there is another signal generation method called walking the bands
            #i personally think its too late for following the trend
            #after confirmation of several breakthroughs
            #maybe its good for stop and reverse
            #condition 4
            if (df['close'][i]>df['upper_band'][i]) and \
            (df['bb_position'][i]==0):
                default_logger().debug('\nCondition 4 satisfied for BB Bottom W pattern')
                for j in range(i,i-period,-1):
                    #condition 2
                    if (np.abs(df['mid_band'][j]-df['close'][j])<alpha) and \
                    (np.abs(df['mid_band'][j]-df['upper_band'][i])<alpha):
                        moveon=True
                        default_logger().debug('\nCondition 2 satisfied for BB Bottom W pattern')
                        break
                
                if moveon==True:
                    moveon=False
                    for k in range(j,i-period,-1):
                        #condition 1
                        if (np.abs(df['lower_band'][k]-df['close'][k])<alpha):
                            threshold=df['close'][k]
                            moveon=True
                            default_logger().debug('\nCondition 1 satisfied with threshold: {}'.format(threshold))
                            break
                            
                if moveon==True:
                    moveon=False
                    for l in range(k,i-period,-1):
                        #this one is for plotting w shape
                        if (df['mid_band'][l]<df['close'][l]):
                            moveon=True
                            default_logger().debug('\nPlot Condition satisfied for BB Bottom W pattern')
                            break
                        
                if moveon==True:
                    moveon=False
                    default_logger().debug('\nRange from {} - {}'.format(i,j))
                    for m in range(i,j-1,-1): # TODO: Should be (i, j, -1) ?
                        default_logger().debug('\nClose: {}, lower_band: {}, alpha: {}, threshold: {}'.format(df['close'][m], df['lower_band'][m], alpha, threshold))
                        #condition 3
                        if (df['close'][m]-df['lower_band'][m]<alpha) and \
                        (df['close'][m]>df['lower_band'][m]) and \
                        (df['close'][m]<=threshold): # TODO: Should be (df['close'][m]<=threshold) ?
                            df.loc[:,'bb_signal'].iloc[i]=1
                            df.loc[:,'coordinates'].iloc[i]='%s,%s,%s,%s,%s'%(l,k,j,m,i)
                            df['bb_position']=df['bb_signal'].cumsum()
                            moveon=True
                            default_logger().debug('\nCondition 3 satisfied for BB Bottom W pattern')
                            break
            
            #clear our positions when there is contraction on bollinger bands
            #contraction on the bandwidth is easy to understand
            #when price momentum exists, the price would move dramatically for either direction
            #which greatly increases the standard deviation
            #when the momentum vanishes, we clear our positions
            
            #note that we put moveon in the condition
            #just in case our signal generation time is contraction period
            #but we dont wanna clear positions right now
            if (df['bb_position'][i]!=0) and \
            (df['std'][i]<beta) and \
            (moveon==False):
                df.loc[:,'bb_signal'].iloc[i]=-1
                df['bb_position']=df['bb_signal'].cumsum()
                default_logger().debug('\nPosition Condition satisfied for BB Bottom W pattern')
        return df

    @tracelog
    def calculate_roi(self, strategy, symbol):
        strategy_copy = strategy.copy(deep=True)
        if len(strategy_copy[strategy_copy['bb_signal']!=0]) < 2:
            print('Not enough data yet')
            return False
        strategy_copy = strategy_copy[strategy_copy['bb_signal']!=0]
        strategy_copy = strategy_copy.loc[:,['Date', 'close', 'bb_signal', 'bb_position']]
        strategy_copy.loc[:,'Symbol'] = symbol
        df_ret = pd.DataFrame(np.diff(strategy_copy['close'])).rename(columns = {0:'returns'})

        strategy_copy.loc[:,'bb_margin'] = 0
        strategy_copy.loc[:,'bb_returns'] = 0
        strategy_copy.loc[:,'bb_rolling_returns'] = 0
        investment_value_initial = resources.backtest().init_cash
        investment_value = investment_value_initial

        for i in range(len(df_ret)):
            returns = df_ret.loc[:,'returns'].iloc[i]*strategy_copy.loc[:,'bb_position'].iloc[i]
            strategy_copy.loc[:,'bb_margin'].iloc[i+1] = returns
            number_of_stocks = math.floor(investment_value/strategy_copy.loc[:,'close'].iloc[i])
            returns = number_of_stocks*strategy_copy.loc[:,'bb_margin'].iloc[i+1]
            strategy_copy.loc[:,'bb_returns'].iloc[i+1] = returns
            strategy_copy.loc[:,'bb_rolling_returns'].iloc[i+1] = round(sum(strategy_copy['bb_returns']), 2)
            investment_value = investment_value + returns

        print('\n{}\n'.format(strategy_copy.to_string(index=False)))
        total_investment_ret = round(sum(strategy_copy['bb_returns']), 2)
        profit_percentage = round((total_investment_ret/investment_value_initial)*100,3)
        print(cl('\nProfit gained from the BB strategy by investing INR 100k in {} : {}\n'.format(symbol, total_investment_ret), attrs = ['bold']))
        print(cl('\nProfit percentage of the BB strategy : {} %\n'.format(profit_percentage), attrs = ['bold']))
        return True

    #visualization
    def plot_strategy(self, new, symbol):
        #as usual we could cut the dataframe into a small slice
        #for a tight and neat figure
        #a and b denotes entry and exit of a trade
        a,b=list(new[new['bb_signal']!=0].iloc[:2].index)
        default_logger().debug('\na: {} and b: {}'.format(a,b))
        newbie=new[a-85:b+30]
        newbie.set_index(pd.to_datetime(newbie['Date'],format='%Y-%m-%d %H:%M:%S'),inplace=True)

        fig=plt.figure(figsize=(10,5))
        ax=fig.add_subplot(111)
        
        #plotting positions on price series and bollinger bands
        ax.plot(newbie['close'],label='close')
        ax.fill_between(newbie.index,newbie['lower_band'],newbie['upper_band'],alpha=0.2,color='#45ADA8')
        ax.plot(newbie['mid_band'],linestyle='--',label='moving average',c='#132226')
        ax.plot(newbie['close'][newbie['bb_signal']==1],marker='^',markersize=12, \
                lw=0,c='g',label='LONG')
        ax.plot(newbie['close'][newbie['bb_signal']==-1],marker='v',markersize=12, \
                lw=0,c='r',label='SHORT')
        
        #plotting w shape
        #we locate the coordinates then find the exact date as index
        temp=newbie['coordinates'][newbie['bb_signal']==1]
        indexlist=list(map(int,temp[temp.index[0]].split(',')))
        ax.plot(newbie['close'][pd.to_datetime(new['Date'].iloc[indexlist])], \
                lw=5,alpha=0.7,c='#FE4365',label='double bottom pattern')
        
        #add some captions
        plt.style.use('fivethirtyeight')
        plt.rcParams['figure.figsize'] = (20, 10)
        xAxisFmt = mdates.DateFormatter('%Y-%m-%d')
        newbie.set_index('Date', inplace=True)
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        intraday_df = newbie[newbie.index >= today]
        if len(intraday_df) > 1:
            xAxisFmt = mdates.DateFormatter('%H:%M')
        else:
            newbie.index = pd.to_datetime(newbie.index)
            plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=5))
        plt.gca().xaxis.set_major_formatter(xAxisFmt)
        plt.text((newbie.loc[newbie['bb_signal']==1].index[0]), \
                newbie['lower_band'][newbie['bb_signal']==1],'Expansion',fontsize=15,color='#563838')
        plt.text((newbie.loc[newbie['bb_signal']==-1].index[0]), \
                newbie['lower_band'][newbie['bb_signal']==-1],'Contraction',fontsize=15,color='#563838')
        
        plt.legend(loc='best')
        plt.title('BB Bottom W Pattern Recognition for {}'.format(symbol))
        plt.ylabel('close')
        plt.grid(True)
        plt.show()

