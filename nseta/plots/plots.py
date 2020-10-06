from plotly.offline import plot
import plotly.graph_objs as go
import pandas as pd
import talib as ta
from matplotlib.widgets import Cursor
import matplotlib.pyplot as plt

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

def plot_technical_indicators(df):
	# plot with various axes scales
	plt.figure(1)
	# plt.subplot(221)
	plot_history(df,'Close', 'Turnover')

	plt.figure(2)	
	# plt.subplot(222)
	plot_rsi(df)

	plt.figure(3)
	# plt.subplot(223)
	plot_sma(df)
	
	plt.figure(4)
	# plt.subplot(224)
	plot_ema(df)

	# plt.figure()
	# plt.subplot(225)
	# plot_adx(df)

	# plt.figure()
	# plt.subplot(226)
	# plot_bbands(df)

	# plt.figure()
	# plt.subplot(227)
	# plot_sstochastic(df)

	# plt.figure()
	# plt.subplot(228)
	# plot_fstochastic(df)

	# Adjust the subplot layout
	# plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
	#                     wspace=0.5)
	return plt

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
def plot_rsi(df):
	df['RSI'] = ta.RSI(df['Close'],14)
	df['RSI'].plot()
	plt.title('RSI(14)')
	plt.grid(True)
	return plt

def plot_mom(df):
	df['MOM'] = ta.MOM(df['Close'],10)
	df['MOM'].plot()
	plt.title('Momentum - MOM(10)')
	plt.grid(True)
	return plt

def plot_dmi(df):
	df['DMI'] = ta.DX(df['High'],df['Low'],df['Close'],timeperiod=14)
	df['DMI'].plot()
	plt.title('Directional Movement Index - DMI(14)')
	plt.grid(True)
	return plt

def plot_macd(df):
	df['macd'], df['macdsignal'], df['macdhist'] = ta.MACDEXT(df['Close'], fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0)
	df[['macd','macdsignal', 'macdhist']].plot()
	plt.title('MACD(12, 26)')
	plt.grid(True)
	return plt

'''
Simple moving average (SMA) calculates the average of a selected 
range of closing prices, by the number of periods in that range.
'''
def plot_sma(df):
	df['SMA(10)'] = ta.SMA(df['Close'],10)
	df['SMA(50)'] = ta.SMA(df['Close'],50)
	df[['Close','SMA(10)', 'SMA(50)']].plot()
	plt.title('SMA(10) & SMA(50)')
	plt.grid(True)
	return plt

'''
(EMA) is a type of moving average (MA) that places a greater weight 
and significance on the most recent data points. That is it is 
generally known as Exponentially Weighted Moving Average.
'''
def plot_ema(df):
	df['EMA(10)'] = ta.EMA(df['Close'], timeperiod = 10)
	df[['Close','EMA(10)']].plot()
	plt.title('EMA(10)')
	plt.grid(True)
	return plt

'''
Average Directional Movement Index(Momentum Indicator) - ADX can be 
used to help measure the overall strength of a trend. The ADX 
indicator is an average of expanding price range values.
'''
def plot_adx(df):
	df['ADX'] = ta.ADX(df['High'],df['Low'], df['Close'], timeperiod=20)
	df[['ADX']].plot()
	plt.title('ADX(20)')
	plt.grid(True)
	return plt

'''
Bollinger Bands are a type of statistical chart characterizing the 
prices and volatility over time of a financial instrument or commodity, 
using a formulaic method propounded by John Bollinger.
'''
def plot_bbands(df):
	df['BBands-U'], df['BBands-M'], df['BBands-L'] = ta.BBANDS(df['Close'], timeperiod =20)
	df[['Close','BBands-U','BBands-M','BBands-L']].plot()
	plt.title('Bollinger Bands(20)')
	plt.grid(True)
	return plt

def plot_sstochastic(df):
	df['SStochastic(14)'], df['SStochastic(3)'] = ta.STOCH(df['High'], df['Low'], df['Close'], fastk_period=14, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
	df[['SStochastic(14)','SStochastic(3)']].plot()
	plt.title('Slow Stochastic(k=14, d=3)')
	plt.grid(True)
	return plt

def plot_fstochastic(df):
	df['FStochastic(14)'], df['FStochastic(3)'] = ta.STOCHF(df['High'], df['Low'], df['Close'], fastk_period=14, fastd_period=3, fastd_matype=0)
	df[['FStochastic(14)','FStochastic(3)']].plot()
	plt.title('Fast Stochastic(k=14, d=3)')
	plt.grid(True)
	return plt

