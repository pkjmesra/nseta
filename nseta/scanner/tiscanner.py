import os
import os.path
import numpy as np
from os import path
from datetime import datetime, date
from time import time

import pandas as pd

from nseta.live.live import get_live_quote
from nseta.common.history import historicaldata
from nseta.common.log import logdebug, default_logger
from nseta.common.ti import *
import talib as ta

__all__ = ['KEY_MAPPING', 'scanner']

KEY_MAPPING = {
	'dt': 'Date',
	'open': 'Open',
	'high': 'High',
	'low': 'Low',
	'close': 'Close',
	'volume': 'Volume',
}

INTRADAY_KEYS_MAPPING = {
	'Symbol': 'Symbol',
	'Date': 'Date',
	'Close': 'LTP',
	'Low': 'Prev_Close',
	'RSI': 'RSI',
	# 'MOM': 'MOM',
	# 'SMA(10)': 'SMA(10)',
	# 'SMA(50)': 'SMA(50)',
	'EMA(9)': 'EMA(9)',
	# 'macd(12)': 'macd(12)',
	# 'macdsignal(9)': 'macdsignal(9)',
	# 'macdhist(26)': 'macdhist(26)',
}

class scanner:
	def __init__(self, scan_intraday=False):
		self._intraday = scan_intraday
		self._stocksdict = {}
		self._keys = ['symbol','previousClose', 'lastPrice']

	@property
	def keys(self):
		return self._keys

	@property
	def intraday(self):
		return self._intraday

	@intraday.setter
	def intraday(self, value):
		self._intraday = value

	@property
	def stocksdict(self):
		return self._stocksdict

	@logdebug
	def scan(self, stocks=[], start_date=None, end_date=None):
		dir_path = ""
		start_time = time()
		if not path.exists("stocks.py"):
			dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(dir_path + "stocks.py", "r")]
		# Time frame you want to pull data from
		# start_date = datetime.datetime.now()-datetime.timedelta(days=365)
		# end_date = datetime.datetime.now()
		frames = []
		signalframes = []
		for stock in stocks:
			try:
				result, primary = get_live_quote(stock, keys = self.keys)
				row = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP'], index = [''])
				value = (row['LTP'][0]).replace(' ','').replace(',','')
				if stock in self.stocksdict:
					(self.stocksdict[stock]).append(float(value))
				else:
					self.stocksdict[stock] = [float(value)]
				index = len(self.stocksdict[stock])
				if index >= 15:
					dfclose = pd.DataFrame(self.stocksdict[stock], columns = ['Close'])
					rsi = ta.RSI(dfclose['Close'],14)
					rsivalue = rsi[index -1]
					row['RSI'] = rsivalue
					print(stock + " RSI:" + str(rsi))
					if rsivalue > 70 or rsivalue < 30:
						signalframes.append(row)
				frames.append(row)
			except Exception as e:
				default_logger().error("Exception encountered for " + stock)
				default_logger().error(e, exc_info=True)
				pass
		if len(frames) > 0:
			df = pd.concat(frames)
			default_logger().debug(df.to_string(index=False))
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
			default_logger().info(signaldf.to_string(index=False))
		end_time = time()
		time_spent = end_time-start_time
		default_logger().info("This run of scan took {:.1f} sec".format(time_spent))

	@logdebug
	def scan_intraday(self, stocks=[]):
		start_time = time()
		dir_path = ""
		if not path.exists("stocks.py"):
			dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(dir_path + "stocks.py", "r")]
		# Time frame you want to pull data from
		# start_date = datetime.datetime.now()-datetime.timedelta(days=365)
		# end_date = datetime.datetime.now()
		frames = []
		signalframes = []
		df = None
		signaldf = None

		for symbol in stocks:
			try:
				df = self.live_intraday(symbol)
				if df is not None and len(df) > 0:
					df = update_ti(df)
					df.drop(df.head(len(df) - 1).index, inplace = True)
					for key in df.keys():
						if not key in INTRADAY_KEYS_MAPPING.keys():
							df.drop([key], axis = 1, inplace = True)
						else:
							searchkey = INTRADAY_KEYS_MAPPING[key]
							df[searchkey] = df[key]
							if key != searchkey:
								df.drop([key], axis = 1, inplace = True)
					frames.append(df)
					signalframes = self.update_signals(signalframes, df)
			except KeyboardInterrupt as e:
				default_logger().debug(e, exc_info=True)
				default_logger().debug('[scan_intraday] Keyboard Interrupt received. Exiting.')
				try:
					stocks = []
					sys.exit(1)
					break
				except SystemExit as se:
					os._exit(1) # se.args[0][0]["code"]
					break
			except Exception as e:
				default_logger().error("Exception encountered for " + symbol)
				default_logger().error(e, exc_info=True)
				pass
			except SystemExit:
				stocks = []
				df = None
				sys.exit(1)
				break
				return
		if len(frames) > 0:
			df = pd.concat(frames)
			# default_logger().debug(df.to_string(index=False))
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
			default_logger().info(signaldf.to_string(index=False))
		end_time = time()
		time_spent = end_time-start_time
		default_logger().info("This run of scan took {:.1f} sec".format(time_spent))
		return df, signaldf

	@logdebug
	def live_intraday(self, symbol):
		df = None
		try:
			historyinstance = historicaldata()
			df = historyinstance.daily_ohlc_history(symbol, start=date.today(), end = date.today(), intraday=True)
			if df is not None and len(df) > 0:
				default_logger().debug("Dataframe for " + symbol + "\n" + str(df))
				df = self.map_keys(df, symbol)
			else:
				default_logger().info("Empty dataframe for " + symbol)
		except KeyboardInterrupt as e:
				default_logger().debug(e, exc_info=True)
				default_logger().debug('Keyboard Interrupt received. Exiting.')
				try:
					sys.exit(e.args[0][0]["code"])
				except SystemExit as se:
					os._exit(se.args[0][0]["code"])
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return
		except SystemExit:
			df = None
			return
		return df

	def map_keys(self, df, symbol):
		try:
			for key in KEY_MAPPING.keys():
				searchkey = KEY_MAPPING[key]
				if searchkey in df:
					df[key] = df[searchkey]
				else:
					df[key] = np.nan
					df[searchkey] = np.nan
			df['Symbol'] = symbol
			df['Volume'] = np.nan
			# df.drop(list(KEY_MAPPING.keys()), axis = 1, inplace = True)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			default_logger().debug('Exception encountered for key: ' + searchkey + "\n")
			pass
		return df

	@logdebug
	def update_signals(self, signalframes, df):
		if not 'RSI' in df.keys() and not 'EMA(9)' in df.keys():
			return signalframes
		try:
			rsivalue = df['RSI'].iloc[0]
			ema9 = df['EMA(9)'].iloc[0]
			# macd12 = df['macd(12)'].iloc[0]
			# macd9 = df['macdsignal(9)'].iloc[0]
			df['Signal'] = 'NA'
			ltp = df['LTP'].iloc[0]
			if (rsivalue is not None) and (rsivalue > 75 or rsivalue < 25):
				df['Signal'].iloc[0] = '(SELL)[RSI >= 75]' if rsivalue > 75 else '(BUY)[RSI <= 25]'
				signalframes.append(df)
			if (ema9 is not None) and abs(ltp-ema9) <= 0.1:
				df['Signal'].iloc[0] = '(BUY)[LTP > EMA(9)]' if ltp - ema9 >=0 else '(SELL)[LTP < EMA(9)]'
				signalframes.append(df)
			# if (macd12 is not None) and (macd9 is not None) and abs(macd12-macd9) <= 0.05:
			# 	df['Signal'].iloc[0] = 'MACD(12) > MACD(9)' if macd12 - macd9 >=0 else 'MACD(12) < MACD(9)'
			# 	signalframes.append(df)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return
		return signalframes						
