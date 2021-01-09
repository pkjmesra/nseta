import inspect
import numpy as np
import os.path
import pandas as pd
import talib as ta
import datetime
import sys

from time import time

from nseta.common.commons import *
from nseta.archives.archiver import *
from nseta.common.history import historicaldata
from nseta.common.log import tracelog, default_logger
from nseta.common.ti import ti
from nseta.live.live import get_live_quote

__all__ = ['KEY_MAPPING', 'scanner', 'TECH_INDICATOR_KEYS']

TYPE_LIVE = 'live'
TYPE_INTRADAY = 'intraday'
TYPE_SWING = 'swing'

KEY_MAPPING = {
	'dt': 'Date',
	'open': 'Open',
	'High': 'High',
	'Low': 'Low',
	'close': 'Close',
	# 'volume': 'Volume',
}

TECH_INDICATOR_KEYS = ['rsi', 'smac', 'emac', 'macd', 'bbands', 'all']

INTRADAY_KEYS_MAPPING = {
	'Symbol': 'Symbol',
	'Date': 'Date',
	'Close': 'LTP',
	# 'Low': 'Prev_Close',
	'RSI': 'RSI',
	'MOM': 'MOM',
	'BBands-U': 'BBands-U',
	'BBands-L' : 'BBands-L',
	# 'SMA(10)': 'SMA(10)',
	# 'SMA(50)': 'SMA(50)',
	'EMA(9)': 'EMA(9)',
	'macd(12)': 'macd(12)',
	'macdsignal(9)': 'macdsignal(9)',
	'macdhist(26)': 'macdhist(26)',
	# 'PP':'PP',
	# 'R1': 'R1',
	# 'S1': 'S1',
	# 'R2': 'R2',
	# 'S2': 'S2',
	# 'R3': 'R3',
	# 'S3': 'S3',
}

# PIVOT_KEYS =['PP', 'R1','S1','R2','S2','R3','S3']

class scanner:
	def __init__(self, indicator='all'):
		if indicator not in TECH_INDICATOR_KEYS:
			indicator = 'all'
		self._indicator = indicator
		self._stocksdict = {}
		self._keys = ['symbol','previousClose', 'lastPrice']
		self._scanner_dir = os.path.dirname(os.path.realpath(__file__))

	@property
	def keys(self):
		return self._keys

	@property
	def scanner_directory(self):
		return self._scanner_dir

	@property
	def indicator(self):
		return self._indicator

	@property
	def stocksdict(self):
		return self._stocksdict

	def get_func_name(self, kind):
		if kind==TYPE_LIVE:
			return self.scan_live_quanta
		elif kind==TYPE_INTRADAY:
			return self.scan_intraday_quanta
		elif kind==TYPE_SWING:
			return self.scan_swing_quanta

	@tracelog
	def scan_live(self, stocks=[]):
		start_time = time()
		file_path = "stocks.py"
		if not os.path.exists(file_path):
			file_path = os.path.join(self.scanner_directory, file_path)
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(file_path, "r")]
		list_returned = self.scan_internal(stocks, TYPE_LIVE)
		end_time = time()
		time_spent = end_time-start_time
		print("\nThis run of live scan took {:.1f} sec".format(time_spent))
		return list_returned.pop(0), list_returned.pop(0)

	@tracelog
	def scan_intraday(self, stocks=[]):
		start_time = time()
		file_path = "stocks.py"
		if not os.path.exists(file_path):
			file_path = os.path.join(self.scanner_directory, file_path)
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(file_path, "r")]
		list_returned = self.scan_internal(stocks, TYPE_INTRADAY)
		end_time = time()
		time_spent = end_time-start_time
		print("\nThis run of intraday scan took {:.1f} sec".format(time_spent))
		return list_returned.pop(0), list_returned.pop(0)

	@tracelog
	def scan_swing(self, stocks=[]):
		start_time = time()
		file_path = "stocks.py"
		if not os.path.exists(file_path):
			file_path = os.path.join(self.scanner_directory, file_path)
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(file_path, "r")]
		list_returned = self.scan_internal(stocks, TYPE_SWING)
		end_time = time()
		time_spent = end_time-start_time
		print("\nThis run of swing scan took {:.1f} sec".format(time_spent))
		return list_returned.pop(0), list_returned.pop(0)

	@tracelog
	def scan_internal(self, stocks, kind):
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
			df = concatenated_dataframe(df1, df2)
			signaldf = concatenated_dataframe(signaldf1, signaldf2)
			return [df, signaldf]
		else:
			del(kwargs['kind'])
			func_execute = self.get_func_name(kind)
			return func_execute(**kwargs)

	@tracelog
	def scan_live_quanta(self, stocks):
		frames = []
		signalframes = []
		df = None
		signaldf = None
		for stock in stocks:
			try:
				sys.stdout.write("\rFetching for {}".ljust(25).format(stock))
				sys.stdout.flush()
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
				sys.stdout.write("\rFetching for {}".ljust(25).format(symbol))
				sys.stdout.flush()
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
				sys.stdout.write("\rFetching for {}".ljust(25).format(symbol))
				sys.stdout.flush()
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df)
					df = df.sort_values(by='Date',ascending=True)
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
			arch = archiver()
			df = arch.restore(symbol, ResponseType.Intraday)
			if df is None or len(df) == 0:
				df = historyinstance.daily_ohlc_history(symbol, start=datetime.date.today(), end = datetime.date.today(), intraday=True)
			if df is not None and len(df) > 0:
				# default_logger().debug("Dataframe for " + symbol + "\n" + str(df))
				df = self.map_keys(df, symbol)
				arch.archive(df, symbol, ResponseType.Intraday)
			else:
				default_logger().debug("Empty dataframe for " + symbol)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return None
		except SystemExit:
			return None
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
				if key in df.keys():
					df.drop([key], axis = 1, inplace = True)
			df['Symbol'] = symbol
			df['datetime'] = df['Date']
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			default_logger().debug('Exception encountered for key: ' + searchkey + "\n")
		return df

	@tracelog
	def update_signals(self, signalframes, df):
		if (df is None) or (len(df) < 1) or (not 'RSI' in df.keys() and not 'EMA(9)' in df.keys()):
			return signalframes
		try:
			df['Signal'] = 'NA'
			decimals = 2
			ltp = df['LTP'].iloc[0]
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-L', 0.05, ltp, '<=', '(BUY)  [LTP < BBands-L]', '(BUY)  [LTP ~ BBands-L]')
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-U', 0.05, ltp, '<=', '(SELL) [LTP ~ BBands-U]', '(SELL) [LTP > BBands-U]')
			signalframes = self.update_signal_indicator(df, signalframes, 'rsi', 'RSI', 25, 75, '><', '(SELL) [RSI >= 75]', '(BUY)  [RSI <= 25]')
			signalframes = self.update_signal_indicator(df, signalframes, 'ema', 'EMA(9)', 0.1, ltp, '>=', '(BUY)  [LTP > EMA(9)]', '(SELL) [LTP < EMA(9)]')
			macd12 = df['macd(12)'].iloc[0]
			signalframes = self.update_signal_indicator(df, signalframes, 'macd', 'macdsignal(9)', 0.05, macd12, '>=', '(BUY)  [MACD > EMA]', '(SELL) [MACD < EMA]')
			if self.indicator == 'macd' or self.indicator == 'all':
				df['macd(12)'] = df['macd(12)'].apply(lambda x: round(x, decimals))
				df['macdhist(26)'] = df['macdhist(26)'].apply(lambda x: round(x, decimals))
			else:
				df.drop(['macd(12)', 'macdhist(26)'], axis = 1, inplace = True)
			# Drop the Momentum indicator. We don't need it anymore
			df.drop(['MOM'], axis = 1, inplace = True)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return
		return signalframes

	def update_signal_indicator(self, df, signalframes, indicator, column, margin, comparator_value, ltp_label_comparator, true_remarks, false_remarks):
		if self.indicator == indicator or self.indicator == 'all':
			decimals = 2
			value = round(df[column].iloc[0],2)
			true_remarks = true_remarks.ljust(23)
			false_remarks = false_remarks.ljust(23)
			if ltp_label_comparator == '><':
				if (value is not None) and (value > comparator_value or value < margin):
					df['Signal'].iloc[0] = true_remarks if value > comparator_value else false_remarks
					default_logger().debug(df.to_string(index=False))
					signalframes.append(df)
			else:
				if (value is not None) and abs(value-comparator_value) <= margin:
					if ltp_label_comparator == '<=':
						df['Signal'].iloc[0] = true_remarks if comparator_value - value <=0 else false_remarks
					elif ltp_label_comparator == '>=':
						df['Signal'].iloc[0] = true_remarks if comparator_value - value >=0 else false_remarks
					default_logger().debug(df.to_string(index=False))
					signalframes.append(df)
			df[column] = df[column].apply(lambda x: round(x, decimals))
		else:
			df.drop([column], axis = 1, inplace = True)
		return signalframes

	# def buy_solid():
		# OBV trending upwards
		# RSI trending upwards. If not, then if it's closer to lower limit, strong buy
		# MACD trending upwards and +ve. MACD > MACD 12
		# LTP line > EMA9 and LTP > MA50
		# MOM +ve and trending upwards
