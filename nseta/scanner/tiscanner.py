import inspect
import numpy as np
import os.path
import pandas as pd
import talib as ta
import datetime

from datetime import date
from time import time

from nseta.common.commons import *
from nseta.common.history import historicaldata
from nseta.common.log import tracelog, default_logger
from nseta.common.ti import ti
from nseta.live.live import get_live_quote

__all__ = ['KEY_MAPPING', 'scanner']

TOKEN_LIVE = 'live'
TOKEN_INTRADAY = 'intraday'
TOKEN_SWING = 'swing'

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
	# 'Low': 'Prev_Close',
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

	def get_func_name(self, token):
		if token==TOKEN_LIVE:
			return self.scan_live_quanta
		elif token==TOKEN_INTRADAY:
			return self.scan_intraday_quanta
		elif token==TOKEN_SWING:
			return self.scan_swing_quanta

	@tracelog
	def scan_live(self, stocks=[], indicator='all'):
		dir_path = ""
		start_time = time()
		if not os.path.exists("stocks.py"):
			dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(dir_path + "stocks.py", "r")]
		list_returned = self.scan_internal(stocks, TOKEN_LIVE)
		end_time = time()
		time_spent = end_time-start_time
		default_logger().info("This run of live scan took {:.1f} sec".format(time_spent))
		return list_returned.pop(0), list_returned.pop(0)

	@tracelog
	def scan_intraday(self, stocks=[], indicator='all'):
		start_time = time()
		dir_path = ""
		if not os.path.exists("stocks.py"):
			dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(dir_path + "stocks.py", "r")]
		list_returned = self.scan_internal(stocks, TOKEN_INTRADAY)
		end_time = time()
		time_spent = end_time-start_time
		default_logger().info("This run of intraday scan took {:.1f} sec".format(time_spent))
		return list_returned.pop(0), list_returned.pop(0)

	@tracelog
	def scan_swing(self, stocks=[], indicator='all'):
		dir_path = ""
		start_time = time()
		if not os.path.exists("stocks.py"):
			dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(dir_path + "stocks.py", "r")]
		list_returned = self.scan_internal(stocks, TOKEN_SWING)
		end_time = time()
		time_spent = end_time-start_time
		default_logger().info("This run of swing scan took {:.1f} sec".format(time_spent))
		return list_returned.pop(0), list_returned.pop(0)

	@tracelog
	def scan_internal(self, stocks, token):
		frame = inspect.currentframe()
		args, _, _, kwargs = inspect.getargvalues(frame)
		del(kwargs['frame'])
		del(kwargs['self'])
		stocks_segment = kwargs['stocks']
		n = 3 # Max number of stocks to be processed at a time by a thread
		if len(stocks_segment) > n:
			kwargs1 = dict(kwargs)
			kwargs2 = dict(kwargs)
			first_n = stocks[:n]
			remaining_stocks = stocks[n:]
			# n_segmented_stocks = [stocks_segment[i * n:(i + 1) * n] for i in range((len(stocks_segment) + n - 1) // n )]
			kwargs1['stocks'] = first_n
			kwargs2['stocks'] = remaining_stocks
			t1 = ThreadReturns(target=self.scan_internal, kwargs=kwargs1)
			t2 = ThreadReturns(target=self.scan_internal, kwargs=kwargs2)
			t1.start()
			t2.start()
			t1.join()
			t2.join()
			list1 = t1.result
			list2 = t2.result
			df1 = list1.pop(0)
			df2 = list2.pop(0)
			signaldf1 = list1.pop(0)
			signaldf2 = list2.pop(0)
			df = self.concatenated_dataframe(df1, df2)
			signaldf = self.concatenated_dataframe(signaldf1, signaldf2)
			return [df, signaldf]
		else:
			del(kwargs['token'])
			func_execute = self.get_func_name(token)
			return func_execute(**kwargs)

	@tracelog
	def scan_live_quanta(self, stocks):
		frames = []
		signalframes = []
		df = None
		signaldf = None
		for stock in stocks:
			try:
				result, primary = get_live_quote(stock, keys = self.keys)
				if primary is not None and len(primary) > 0:
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
						default_logger().debug(stock + " RSI:" + str(rsi))
						if rsivalue > 70 or rsivalue < 30:
							signalframes.append(row)
					frames.append(row)
			except Exception as e:
				default_logger().debug("Exception encountered for " + stock)
				default_logger().debug(e, exc_info=True)
		if len(frames) > 0:
			df = pd.concat(frames)
			# default_logger().debug(df.to_string(index=False))
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
			# default_logger().debug(signaldf.to_string(index=False))
		return [df, signaldf]

	@tracelog
	def scan_intraday_quanta(self, stocks):
		frames = []
		signalframes = []
		df = None
		signaldf = None
		tiinstance = ti()
		for symbol in stocks:
			try:
				df = self.ohlc_intraday_history(symbol)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df)
					df = df.tail(1)
					for key in df.keys():
						if not key in INTRADAY_KEYS_MAPPING.keys():
							df.drop([key], axis = 1, inplace = True)
						else:
							searchkey = INTRADAY_KEYS_MAPPING[key]
							if key != searchkey:
								if searchkey not in df.keys():
									df[searchkey] = df[key]
								df.drop([key], axis = 1, inplace = True)
					frames.append(df)
					signalframes = self.update_signals(signalframes, df)
			except KeyboardInterrupt as e:
				default_logger().debug(e, exc_info=True)
				default_logger().debug('[scan_intraday] Keyboard Interrupt received. Exiting.')
				try:
					sys.exit(1)
					break
				except SystemExit as se:
					os._exit(1) # se.args[0][0]["code"]
					break
			except Exception as e:
				default_logger().debug("Exception encountered for " + symbol)
				default_logger().debug(e, exc_info=True)
			except SystemExit:
				sys.exit(1)
		if len(frames) > 0:
			df = pd.concat(frames)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [df, signaldf]

	@tracelog
	def scan_swing_quanta(self, stocks):
		frames = []
		signalframes = []
		df = None
		signaldf = None
		tiinstance = ti()
		historyinstance = historicaldata()
		# Time frame you want to pull data from
		start_date = datetime.datetime.now()-datetime.timedelta(days=365)
		end_date = datetime.datetime.now()
		for symbol in stocks:
			try:
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df)
					df = df.tail(1)
					default_logger().debug(df.to_string(index=False))
					for key in df.keys():
						# Symbol Series       Date  Prev Close     Open     High      Low     Last    Close     VWAP    Volume      Turnover  Trades  Deliverable Volume  %Deliverable
						if not key in INTRADAY_KEYS_MAPPING.keys():
							df.drop([key], axis = 1, inplace = True)
						elif (key in INTRADAY_KEYS_MAPPING.keys()):
							searchkey = INTRADAY_KEYS_MAPPING[key]
							if key != searchkey:
								df[searchkey] = df[key]
								df.drop([key], axis = 1, inplace = True)
					default_logger().debug(df.to_string(index=False))
					frames.append(df)
					signalframes = self.update_signals(signalframes, df)
			except KeyboardInterrupt as e:
				default_logger().debug(e, exc_info=True)
				default_logger().debug('[scan_intraday] Keyboard Interrupt received. Exiting.')
				try:
					sys.exit(1)
					break
				except SystemExit as se:
					os._exit(1) # se.args[0][0]["code"]
					break
			except Exception as e:
				default_logger().debug("Exception encountered for " + symbol)
				default_logger().debug(e, exc_info=True)
			except SystemExit:
				sys.exit(1)
		if len(frames) > 0:
			df = pd.concat(frames)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [df, signaldf]

	@tracelog
	def ohlc_intraday_history(self, symbol):
		df = None
		try:
			historyinstance = historicaldata()
			df = historyinstance.daily_ohlc_history(symbol, start=date.today(), end = date.today(), intraday=True)
			if df is not None and len(df) > 0:
				# default_logger().debug("Dataframe for " + symbol + "\n" + str(df))
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
			return None
		except SystemExit:
			return None
		return df

	def concatenated_dataframe(self, df1, df2):
		if df1 is not None and len(df1) > 0:
			if df2 is not None and len(df2) > 0:
				df = pd.concat((df1, df2))
			else:
				df = df1
		elif df2 is not None and len(df2) > 0:
			df = df2
		else:
			df = None
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
		return df

	@tracelog
	def update_signals(self, signalframes, df):
		if (df is None) or (len(df) < 1) or (not 'RSI' in df.keys() and not 'EMA(9)' in df.keys()):
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
