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
from nseta.common.tradingtime import *

__all__ = ['KEY_MAPPING', 'scanner', 'TECH_INDICATOR_KEYS']

TYPE_LIVE = 'live'
TYPE_INTRADAY = 'intraday'
TYPE_SWING = 'swing'
TYPE_VOLUME = 'volume'
VOLUME_PERIOD = 7
SWING_PERIOD = 90

KEY_MAPPING = {
	'dt': 'Date',
	'open': 'Open',
	'High': 'High',
	'Low': 'Low',
	'close': 'Close',
	# 'volume': 'Volume',
}

TECH_INDICATOR_KEYS = ['rsi', 'smac', 'emac', 'macd', 'bbands', 'all']
VOLUME_KEYS = ['Remarks','PPoint', 'S1/S2/S3/R1/R2/R3','Symbol', 'Date', 'LTP', 'VWAP', 'T-1%Del', '7DayAvgVolume', 'T-1-7(%)', 'TodaysVolume','T0(%)', 'T0-7(%)', 'T0%Del', 'T0BuySellDiff', '%Change']

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
		self._keys = ['symbol','previousClose', 'lastPrice', 'deliveryToTradedQuantity', 'BuySellDiffQty', 'totalTradedVolume', 'pChange']
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
		elif kind==TYPE_VOLUME:
			return self.scan_volume_quanta
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
	def scan_volume(self, stocks=[]):
		start_time = time()
		file_path = "stocks.py"
		if not os.path.exists(file_path):
			file_path = os.path.join(self.scanner_directory, file_path)
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(file_path, "r")]
		list_returned = self.scan_internal(stocks, TYPE_VOLUME)
		end_time = time()
		time_spent = end_time-start_time
		print("\nThis run of volume scan took {:.1f} sec".format(time_spent))
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
					row = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP', '% Delivery', 'Buy - Sell', 'TotalTradedVolume', 'pChange'], index = [''])
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
		start_date = datetime.datetime.now()-datetime.timedelta(days=SWING_PERIOD)
		end_date = datetime.datetime.now()
		for symbol in stocks:
			try:
				sys.stdout.write("\rFetching for {}".ljust(25).format(symbol))
				sys.stdout.flush()
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date, type=ResponseType.History)
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
	def scan_volume_quanta(self, stocks):
		frames = []
		signalframes = []
		df = None
		signaldf = None
		tiinstance = ti()
		historyinstance = historicaldata()
		# Time frame you want to pull data from
		start_date = datetime.datetime.now()-datetime.timedelta(days=VOLUME_PERIOD)
		end_date = datetime.datetime.now()
		for symbol in stocks:
			try:
				sys.stdout.write("\rFetching for {}".ljust(25).format(symbol))
				sys.stdout.flush()
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date, type=ResponseType.Volume)
				df = tiinstance.update_ti(df)
				default_logger().debug(df.to_string(index=False))
				result, primary = get_live_quote(symbol, keys = self.keys)
				if (primary is not None and len(primary) > 0) and (df is not None and len(df) > 0):
					df_today = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP', 'T0%Del', 'T0BuySellDiff', 'TotalTradedVolume','pChange'], index = [''])
					df, df_today, signalframes = self.format_scan_volume_df(df, df_today, signalframes)
					frames.append(df)
			except Exception as e:
				default_logger().debug("Exception encountered for " + symbol)
				default_logger().debug(e, exc_info=True)
				continue
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
				df = historyinstance.daily_ohlc_history(symbol, start=datetime.date.today(), end = datetime.date.today(), intraday=True, type=ResponseType.Intraday)
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
			df['Remarks'] = 'NA'
			df['Confidence'] = 'NA'
			decimals = 2
			ltp = df['LTP'].iloc[0]
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-L', 0.05, ltp, '<=', 'BUY', '[LTP < BBands-L]', 'BUY', '[LTP ~ BBands-L]')
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-U', 0.05, ltp, '<=', 'SELL', '[LTP ~ BBands-U]', 'SELL', '[LTP > BBands-U]')
			signalframes = self.update_signal_indicator(df, signalframes, 'rsi', 'RSI', 25, 75, '><', 'SELL', '[RSI >= 75]', 'BUY', '[RSI <= 25]')
			signalframes = self.update_signal_indicator(df, signalframes, 'emac', 'EMA(9)', 0.1, ltp, '>=', 'BUY', '[LTP > EMA(9)]', 'SELL', '[LTP < EMA(9)]')
			macd12 = df['macd(12)'].iloc[0]
			signalframes = self.update_signal_indicator(df, signalframes, 'macd', 'macdsignal(9)', 0.05, macd12, '>=', 'BUY', '[MACD > EMA]', 'SELL', '[MACD < EMA]')
			if self.indicator == 'macd' or self.indicator == 'all':
				df['macd(12)'] = df['macd(12)'].apply(lambda x: round(x, decimals))
				df['macdhist(26)'] = df['macdhist(26)'].apply(lambda x: round(x, decimals))
			self.trim_columns(df)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return
		return signalframes

	def update_signal_indicator(self, df, signalframes, indicator, column, margin, comparator_value, ltp_label_comparator, true_type, true_remarks, false_type, false_remarks):
		if self.indicator == indicator or self.indicator == 'all':
			decimals = 2
			value = round(df[column].iloc[0],2)
			if ltp_label_comparator == '><':
				if (value is not None) and (value > comparator_value or value < margin):
					df['Remarks'].iloc[0] = true_remarks if value > comparator_value else false_remarks
					df['Signal'].iloc[0] = true_type if value > comparator_value else false_type
					self.update_confidence_level(df)
					default_logger().debug(df.to_string(index=False))
					signalframes.append(df)
			else:
				if (value is not None) and abs(value-comparator_value) <= margin:
					if ltp_label_comparator == '<=':
						df['Remarks'].iloc[0] = true_remarks if comparator_value - value <=0 else false_remarks
						df['Signal'].iloc[0] = true_type if comparator_value - value <=0 else false_type
					elif ltp_label_comparator == '>=':
						df['Remarks'].iloc[0] = true_remarks if comparator_value - value >=0 else false_remarks
						df['Signal'].iloc[0] = true_type if comparator_value - value >=0 else false_type
					self.update_confidence_level(df)
					default_logger().debug(df.to_string(index=False))
					signalframes.append(df)
			df[column] = df[column].apply(lambda x: round(x, decimals))
		return signalframes

	def update_confidence_level(self, df):
		rsi = round(df['RSI'].iloc[0],2)
		bbandsl = round(df['BBands-L'].iloc[0],2)
		bbandsu = round(df['BBands-U'].iloc[0],2)
		ema = round(df['EMA(9)'].iloc[0],2)
		macdsignal = round(df['macdsignal(9)'].iloc[0],2)
		macd12 = round(df['macd(12)'].iloc[0],2)
		mom = round(df['MOM'].iloc[0],2)
		signal = df['Signal'].iloc[0]
		ltp = df['LTP'].iloc[0]
		confidence = 0
		if signal == 'BUY':
			if rsi >=60:
				confidence = confidence + 20
			elif self.indicator == 'rsi':
				confidence = confidence + 10
			if mom > 0:
				confidence = confidence + 20
			if macd12 > macdsignal and macd12 > 0:
				confidence = confidence + 20
			elif macd12 > macdsignal and macd12 <= 0 or self.indicator == 'macd' or self.indicator == 'all':
				confidence = confidence + 10
			if ltp <= bbandsl:
				confidence = confidence + 20
			elif ltp - bbandsl <= .1 or self.indicator == 'bbands' or self.indicator == 'all':
				confidence = confidence + 10
			if ltp >= ema:
				confidence = confidence + 10
			elif self.indicator == 'emac':
				confidence = confidence + 10
		elif signal == 'SELL':
			if rsi <=40:
				confidence = confidence + 20
			elif self.indicator == 'rsi':
				confidence = confidence + 10
			if mom < 0:
				confidence = confidence + 20
			if macd12 < macdsignal and macd12 < 0:
				confidence = confidence + 20
			elif macd12 < macdsignal and macd12 >= 0 or self.indicator == 'macd' or self.indicator == 'all':
				confidence = confidence + 10
			if ltp >= bbandsu:
				confidence = confidence + 20
			elif bbandsu - ltp >= .1 or self.indicator == 'bbands' or self.indicator == 'all':
				confidence = confidence + 10
			if ltp <= ema:
				confidence = confidence + 10
			elif self.indicator == 'emac':
				confidence = confidence + 10
		df['Confidence'].iloc[0] = ' >> {} %  <<'.format(confidence) if confidence >=80 else '{} %'.format(confidence)
		return df

	def trim_columns(self, df):
		columns = {'bbands':['BBands-L', 'BBands-U'], 
			'rsi': ['RSI'], 
			'emac': ['EMA(9)'], 
			'macd': ['macdsignal(9)', 'macd(12)', 'macdhist(26)']}
		for indicator in columns.keys():
			if self.indicator != indicator and self.indicator != 'all':
				for key in columns[indicator]:
					if key in df.keys():
						df.drop([key], axis = 1, inplace = True)
		df.drop(['MOM'], axis = 1, inplace = True)

	def format_scan_volume_df(self, df, df_today, signalframes=[]):
		default_logger().debug(df_today.to_string(index=False))
		signalframescopy = signalframes
		df_today = df_today.tail(1)
		df = df.sort_values(by='Date',ascending=True)
		# Get the 7 day average volume
		total_7day_volume = df['Volume'].sum()
		avg_volume = round(total_7day_volume/7,2)
		df = df.tail(1)
		df['LTP']=np.nan
		df['%Change'] = np.nan
		df['T0(%)']= np.nan
		df['T0-7(%)'] = np.nan
		df['Remarks']='NA'
		df['T-1-7(%)']= np.nan
		df['T-1%Del'] = df['%Deliverable'].apply(lambda x: round(x*100, 2))
		df['T0%Del']= np.nan
		df['PPoint']= df['PP']
		df['S1/S2/S3/R1/R2/R3']= np.nan
		if current_datetime_in_ist_trading_time_range():
			df['T0BuySellDiff']= np.nan
			df['T0BuySellDiff'].iloc[0] = df_today['T0BuySellDiff'].iloc[0]

		volume_yest = df['Volume'].iloc[0]
		vwap = df['VWAP'].iloc[0]
		ltp = (df_today['LTP'].iloc[0]).replace(',','')
		ltp = float(ltp)
		today_volume = df_today['TotalTradedVolume'].iloc[0]
		today_vs_yest = round((100* (float(today_volume.replace(',','')) - volume_yest)/volume_yest))
		df['Date'].iloc[0] = df_today['Updated'].iloc[0]
		df['%Change'].iloc[0] = df_today['pChange'].iloc[0]
		df['LTP'].iloc[0] = ltp
		df['T0(%)'].iloc[0] = today_vs_yest
		df['T0-7(%)'].iloc[0] = round((100* (float(today_volume.replace(',','')) - avg_volume)/avg_volume))
		df['T-1-7(%)'].iloc[0] = round((100 * (volume_yest - avg_volume)/avg_volume))
		df['T0%Del'].iloc[0] = df_today['T0%Del'].iloc[0]
		if ltp >= df['PP'].iloc[0]:
			df['Remarks'].iloc[0]='LTP >= PP'
			df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['PP'].iloc[0]
			if ltp >= df['R3'].iloc[0]:
				df['Remarks'].iloc[0]='LTP >= R3'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['R3'].iloc[0]
			elif ltp >= df['R2'].iloc[0]:
				df['Remarks'].iloc[0]='LTP >= R2'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['R2'].iloc[0]
			elif ltp >= df['R1'].iloc[0]:
				df['Remarks'].iloc[0]='LTP >= R1'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['R1'].iloc[0]
			elif ltp < df['R1'].iloc[0]:
				df['Remarks'].iloc[0]='LTP < R1'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['R1'].iloc[0]
		else:
			df['Remarks'].iloc[0]='LTP < PP'
			df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['PP'].iloc[0]
			if ltp >= df['S1'].iloc[0]:
				df['Remarks'].iloc[0]='LTP >= S1'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['S1'].iloc[0]
			elif ltp >= df['S2'].iloc[0]:
				df['Remarks'].iloc[0]='LTP >= S2'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['S2'].iloc[0]
			elif ltp >= df['S3'].iloc[0]:
				df['Remarks'].iloc[0]='LTP >= S3'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['S3'].iloc[0]
			elif ltp < df['S3'].iloc[0]:
				df['Remarks'].iloc[0]='LTP < S3'
				df['S1/S2/S3/R1/R2/R3'].iloc[0] = df['S3'].iloc[0]

		default_logger().debug(df.to_string(index=False))
		for key in df.keys():
			# Symbol Series       Date  Prev Close     Open     High      Low     Last    Close     VWAP    Volume      Turnover  Trades  Deliverable Volume  %Deliverable
			if not key in VOLUME_KEYS:
				df.drop([key], axis = 1, inplace = True)
		default_logger().debug(df.to_string(index=False))
		if today_vs_yest > 0 or ltp >= vwap:
			signalframescopy.append(df)
		return df, df_today, signalframescopy

	# def buy_solid():
		# OBV trending upwards
		# RSI trending upwards. If not, then if it's closer to lower limit, strong buy
		# MACD trending upwards and +ve. MACD > MACD 12
		# LTP line > EMA9 and LTP > MA50
		# MOM +ve and trending upwards
