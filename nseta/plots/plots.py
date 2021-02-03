from nseta.common.log import tracelog
from nseta.common.ti import ti

from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
import talib as ta
import matplotlib.pyplot as plt

__all__ = ['plot_candlestick', 'plot_technical_indicators', 'plot_history', 'plot_rsi', 'plot_mom', 'plot_dmi', 'plot_macd', 'plot_sma', 'plot_ema', 'plot_adx', 'plot_bbands', 'plot_obv', 'plot_sstochastic', 'plot_fstochastic']

@tracelog
def plot_candlestick_from_csv(csv_file_path):
	df = pd.read_csv(csv_file_path)
	plot_candlestick(df)

'''
We can validate our results by plotting the candles and visually check 
against the patterns found. This visualizes the data using Plotly. 
The dataset and the plot can be compared side by side and the patterns 
can be validated easily by matching the indexes.
Before calling this, we should have extracted all the candlestick patterns 
using TA-Lib. We should have ranked them based on the 
“Overall performance rank” and selected the best performance pattern 
for each candle.
'''
@tracelog
def plot_candlestick(df, symbol_name="", plot_title=""):
	o = df['Open'].astype(float)
	h = df['High'].astype(float)
	l = df['Low'].astype(float)
	c = df['Close'].astype(float)
	p = df['candlestick_pattern'].astype(str)

	trace = go.Candlestick(
				open=o,
				high=h,
				low=l,
				close=c,
				text=p)
	data = [trace]

	layout = {
		'title': plot_title,
		'yaxis': {'title': 'Price'},
		'xaxis': {'title': 'Index Number'},

	}
	fig = dict(data=data, layout=layout)
	plot(fig, filename= symbol_name +'_candles.html')

@tracelog
def plot_technical_indicators(df):
	# plot with various axes scales
	fig, axs = plt.subplots(5,2, sharex=True)
	tiinstance = ti()
	axs[0,0].plot(tiinstance.get_rsi_df(df))
	axs[0,0].set_ylabel('RSI')
	axs[0,0].axhline(y=30, linestyle='--', color='g', label='30')
	axs[0,0].axhline(y=70, linestyle='--', color='r', label='70')
	axs[0,0].legend(['RSI(14)'], loc='upper left', fontsize='x-small')

	axs[1,0].plot(tiinstance.get_macd_df(df))
	axs[1,0].bar(df['dt'], df['macdhist(26)'])
	axs[1,0].legend(['MACD(12,26)', 'EMA(9)', 'Divergence'], loc='upper left', fontsize='x-small')

	axs[2,0].plot(tiinstance.get_sma_df(df))
	axs[2,0].set_ylabel('Price')
	axs[2,0].legend(['Close','SMA(10)', 'SMA(50)'], loc='upper left', fontsize='x-small')

	axs[3,0].plot(tiinstance.get_ema_df(df))
	axs[3,0].set_ylabel('Price')
	axs[3,0].set_xlabel('Date')
	axs[3,0].legend(['Close','EMA(10)'], loc='upper left', fontsize='x-small')

	axs[4,0].bar(df['dt'],df['Volume'])
	axs[4,0].set_ylabel('Volume')

	axs[0,1].plot(tiinstance.get_mom_df(df))
	axs[0,1].legend(['Mom(2)'], loc='upper left', fontsize='x-small')

	axs[1,1].plot(tiinstance.get_dmi_df(df))
	axs[1,1].plot(tiinstance.get_adx_df(df))
	axs[1,1].legend(['DMI(14)', 'ADX(14)'], loc='upper left', fontsize='x-small')

	axs[2,1].plot(tiinstance.get_bbands_df(df))
	axs[2,1].legend(['Close','BBands-U(20,2)','BBands-M(20,2)','BBands-L(20,2)'], loc='upper left', fontsize='x-small')
	
	axs[3,1].plot(tiinstance.get_obv_df(df))
	axs[3,1].axhline(linestyle='--', color='r')
	axs[3,1].legend(['OBV'], loc='upper left', fontsize='x-small')

	axs[4,1].bar(df['dt'],df['Volume'])

	fig.suptitle('Technical indicators for ' + df['Symbol'][0])
	fig.align_labels()

	return plt

@tracelog
def plot_history(df, plot_points=['Close'], secondary_y="Turnover"):
	df[plot_points].plot(secondary_y=secondary_y)
	plt.title('Price History')
	plt.grid(True)
	return plt

'''
The relative strength index is a technical indicator used in the 
analysis of financial markets. It is intended to chart the current 
and historical strength or weakness of a stock or market based on 
the closing prices of a recent trading period.
'''
@tracelog
def plot_rsi(df):
	tiinstance = ti()
	tiinstance.get_rsi_df(df).plot()
	plt.title('RSI(14)')
	plt.grid(True)
	return plt

@tracelog
def plot_mom(df):
	tiinstance = ti()
	tiinstance.get_mom_df(df).plot()
	plt.title('Momentum - MOM(10)')
	plt.grid(True)
	return plt

@tracelog
def plot_dmi(df):
	tiinstance = ti()
	tiinstance.get_dmi_df(df).plot()
	plt.title('Directional Movement Index - DMI(14)')
	plt.grid(True)
	return plt

@tracelog
def plot_macd(df):
	fig, axs = plt.subplots(1,1, sharex=True)
	tiinstance = ti()
	axs.plot(tiinstance.get_macd_df(df))
	axs.bar(df['dt'], df['macdhist(26)'])
	axs.legend(['MACD(12,26)', 'EMA(9)', 'Divergence'], loc='upper left', fontsize='x-small')
	fig.suptitle('Moving Average Convergence Divergence for ' + df['Symbol'][0])
	fig.align_labels()
	return plt

'''
Simple moving average (SMA) calculates the average of a selected 
range of closing prices, by the number of periods in that range.
'''
@tracelog
def plot_sma(df):
	tiinstance = ti()
	tiinstance.get_sma_df(df).plot()
	plt.title('SMA(10) & SMA(50)')
	plt.grid(True)
	return plt

'''
(EMA) is a type of moving average (MA) that places a greater weight 
and significance on the most recent data points. That is it is 
generally known as Exponentially Weighted Moving Average.
'''
@tracelog
def plot_ema(df):
	tiinstance = ti()
	tiinstance.get_ema_df(df).plot()
	plt.title('EMA(10)')
	plt.grid(True)
	return plt

'''
Average Directional Movement Index(Momentum Indicator) - ADX can be 
used to help measure the overall strength of a trend. The ADX 
indicator is an average of expanding price range values.
'''
@tracelog
def plot_adx(df):
	tiinstance = ti()
	tiinstance.get_adx_df(df).plot()
	plt.title('ADX(14)')
	plt.grid(True)
	return plt

'''
Bollinger Bands are a type of statistical chart characterizing the 
prices and volatility over time of a financial instrument or commodity, 
using a formulaic method propounded by John Bollinger.
'''
@tracelog
def plot_bbands(df):
	tiinstance = ti()
	tiinstance.get_bbands_df(df).plot()
	plt.title('Bollinger Bands(20)')
	plt.grid(True)
	return plt

@tracelog
def plot_obv(df):
	tiinstance = ti()
	tiinstance.get_obv_df(df).plot()
	plt.title('OBV')
	plt.grid(True)
	return plt

@tracelog
def plot_sstochastic(df):
	df['SStochastic(14)'], df['SStochastic(3)'] = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
	df[['SStochastic(14)','SStochastic(3)']].plot()
	plt.title('Slow Stochastic(k=14, d=3)')
	plt.grid(True)
	return plt

@tracelog
def plot_fstochastic(df):
	df['FStochastic(14)'], df['FStochastic(3)'] = ta.STOCHF(df['High'], df['Low'], df['Close'], fastk_period=14, fastd_period=3, fastd_matype=0)
	df[['FStochastic(14)','FStochastic(3)']].plot()
	plt.title('Fast Stochastic(k=14, d=3)')
	plt.grid(True)
	return plt

