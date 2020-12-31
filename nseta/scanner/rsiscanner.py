import os
import os.path
import numpy as np
from os import path
from datetime import datetime, date

import pandas as pd

from nseta.live.live import get_live_quote
from nseta.common.history import get_history
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
	'MOM': 'MOM',
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

	@logdebug
	def scan_intraday(self, stocks=[]):
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
					rsivalue = df['RSI'].iloc[0]
					if (rsivalue is not None) and (rsivalue > 70 or rsivalue < 30):
						signalframes.append(df)
			except Exception as e:
				default_logger().error("Exception encountered for " + symbol)
				default_logger().error(e, exc_info=True)
				pass
		if len(frames) > 0:
			df = pd.concat(frames)
			# default_logger().debug(df.to_string(index=False))
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
			default_logger().info(signaldf.to_string(index=False))
		return df, signaldf

	@logdebug
	def live_intraday(self, symbol):
		try:
			df = get_history(symbol, start=date.today(), end = date.today(), intraday=True)
			if df is not None and len(df) > 0:
				default_logger().info("Dataframe for " + symbol + "\n" + str(df))
				df = self.map_keys(df, symbol)
			else:
				default_logger().info("Empty dataframe for " + symbol)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return
		except SystemExit:
			pass
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
