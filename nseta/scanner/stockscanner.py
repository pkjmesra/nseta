import enum
import inspect
import numpy as np
import pandas as pd
import talib as ta
import datetime
import sys
import threading
from time import time

from nseta.common.commons import *
from nseta.common.multithreadedScanner import multithreaded_scan
from nseta.archives.archiver import *
from nseta.common.history import historicaldata
from nseta.resources.resources import *
from nseta.strategy.rsiSignalStrategy import rsiSignalStrategy
from nseta.strategy.bbandsSignalStrategy import bbandsSignalStrategy
from nseta.strategy.macdSignalStrategy import macdSignalStrategy
from nseta.common.commons import Recommendation
from nseta.common.log import tracelog, default_logger
from nseta.common.ti import ti
from nseta.live.live import get_live_quote
from nseta.common.tradingtime import *

__all__ = ['KEY_MAPPING', 'scanner', 'TECH_INDICATOR_KEYS', 'ScannerType']

class ScannerType(enum.Enum):
	Intraday = 1
	Live = 2
	Quote = 3
	Swing = 4
	Volume = 5
	Unknown = 6

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
VOLUME_KEYS = ['Remarks','PPoint', 'S1-R3','Symbol', 'Date', 'LTP', 'VWAP', 'Yst%Del', '7DayAvgVolume', 'Yst7DVol(%)', 'TodaysVolume','TDYVol(%)', '7DVol(%)', 'Tdy%Del', 'T0BuySellDiff', '%Change']

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

	@property
	def keys(self):
		return self._keys

	@property
	def total_counter(self):
		return self._total_counter

	@property
	def indicator(self):
		return self._indicator

	@property
	def stocksdict(self):
		return self._stocksdict

	def multithreadedScanner_callback(self, **kwargs):
		scanner_type = kwargs['scanner_type']
		del(kwargs['scanner_type'])
		callback_func = self.get_func_name(scanner_type)
		return callback_func(**kwargs)

	def get_func_name(self, scanner_type=ScannerType.Unknown):
		scanner_dict = {(ScannerType.Intraday).name:self.scan_intraday_quanta,
			(ScannerType.Live).name:self.scan_live_quanta,
			(ScannerType.Swing).name:self.scan_swing_quanta,
			(ScannerType.Volume).name:self.scan_volume_quanta}
		return scanner_dict[scanner_type.name]
	
	@tracelog
	def stocks_list(self, stocks=[]):
		global __scan_counter__
		__scan_counter__ = 0
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if stocks is not None and len(stocks) > 0 else resources.default().stocks
		self._total_counter = len(stocks)
		return stocks

	@tracelog
	def scan(self, stocks=[], scanner_type=ScannerType.Unknown):
		start_time = time()
		stocks = self.stocks_list(stocks)
		frame = inspect.currentframe()
		args, _, _, kwargs = inspect.getargvalues(frame)
		del(kwargs['frame'])
		del(kwargs['self'])
		kwargs['scanner_type'] = scanner_type
		kwargs['callbackMethod'] = self.multithreadedScanner_callback
		kwargs['items'] = stocks
		kwargs['max_per_thread'] = 3
		list_returned = multithreaded_scan(**kwargs)
		end_time = time()
		time_spent = end_time-start_time
		sys.stdout.write("\rDone.".ljust(120))
		sys.stdout.flush()
		print("\nThis run of {} scan took {:.1f} sec".format(scanner_type.name, time_spent))
		return list_returned.pop(0), list_returned.pop(0)

	@tracelog
	def scan_live_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		df = None
		signaldf = None
		for stock in stocks:
			try:
				self.update_progress(stock)
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
						rsi = ta.RSI(dfclose['Close'],resources.rsi().period)
						rsivalue = rsi[index -1]
						row['RSI'] = rsivalue
						default_logger().debug(stock + " RSI:" + str(rsi))
						if rsivalue > resources.rsi().upper or rsivalue < resources.rsi().lower:
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
	def scan_intraday_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		df = None
		signaldf = None
		tiinstance = ti()
		tailed_df = None
		for symbol in stocks:
			try:
				self.update_progress(symbol)
				df = self.ohlc_intraday_history(symbol)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df)
					for key in df.keys():
						if not key in INTRADAY_KEYS_MAPPING.keys():
							df.drop([key], axis = 1, inplace = True)
						else:
							searchkey = INTRADAY_KEYS_MAPPING[key]
							if key != searchkey:
								if searchkey not in df.keys():
									df[searchkey] = df[key]
								df.drop([key], axis = 1, inplace = True)
					tailed_df = df.tail(1)
					frames.append(tailed_df)
					signalframes, df = self.update_signals(signalframes, tailed_df, df)
			except Exception as e:
				default_logger().debug("Exception encountered for " + symbol)
				default_logger().debug(e, exc_info=True)
			except SystemExit:
				sys.exit(1)
		if len(frames) > 0:
			tailed_df = pd.concat(frames)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [tailed_df, signaldf]

	@tracelog
	def scan_swing_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		df = None
		signaldf = None
		tiinstance = ti()
		historyinstance = historicaldata()
		tailed_df = None
		# Time frame you want to pull data from
		start_date = datetime.datetime.now()-datetime.timedelta(days=SWING_PERIOD)
		end_date = datetime.datetime.now()
		for symbol in stocks:
			try:
				self.update_progress(symbol)
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date, type=ResponseType.History)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df)
					df = df.sort_values(by='Date',ascending=True)
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
					tailed_df = df.tail(1)
					default_logger().debug(tailed_df.to_string(index=False))
					frames.append(tailed_df)
					signalframes, df = self.update_signals(signalframes, tailed_df, df)
			except Exception as e:
				default_logger().debug("Exception encountered for " + symbol)
				default_logger().debug(e, exc_info=True)
			except SystemExit:
				sys.exit(1)
		if len(frames) > 0:
			tailed_df = pd.concat(frames)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [tailed_df, signaldf]

	@tracelog
	def scan_volume_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		signaldf = None
		tiinstance = ti()
		historyinstance = historicaldata()
		# Time frame you want to pull data from
		start_date = datetime.datetime.now()-datetime.timedelta(days=self.last_7_days_timedelta())
		arch = archiver()
		end_date = datetime.datetime.now()
		for symbol in stocks:
			df_today = None
			primary = None
			df = None
			try:
				self.update_progress(symbol)
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date, type=ResponseType.Volume)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df)
					default_logger().debug(df.to_string(index=False))
					primary = arch.restore('{}_live_quote'.format(symbol), ResponseType.Volume)
					if primary is None or len(primary) == 0:
						result, primary = get_live_quote(symbol, keys = self.keys)
					else:
						df_today = primary
					if (primary is not None and len(primary) > 0):
						if df_today is None:
							df_today = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP', 'Tdy%Del', 'T0BuySellDiff', 'TotalTradedVolume','pChange'], index = [''])
							arch.archive(df_today, '{}_live_quote'.format(symbol), ResponseType.Volume)
						df, df_today, signalframes = self.format_scan_volume_df(df, df_today, signalframes)
						frames.append(df)
				else:
					default_logger().debug("Could not fetch daily_ohlc_history for {}".format(symbol))
			except Exception as e:
				default_logger().debug("Exception encountered for {}".format(symbol))
				default_logger().debug(e, exc_info=True)
				continue
			except SystemExit:
				sys.exit(1)
		if len(frames) > 0:
			df = pd.concat(frames)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [df, signaldf]

	def update_progress(self, symbol):
		global __scan_counter__
		with threading.Lock():
			__scan_counter__ += 1
		sys.stdout.write("\r{}/{}. Fetching for {}".ljust(120).format(__scan_counter__, self.total_counter, symbol))
		sys.stdout.flush()

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
	def update_signals(self, signalframes, df_main, full_df=None):
		if (df_main is None) or (len(df_main) < 1) or (not 'RSI' in df_main.keys() and not 'EMA(9)' in df_main.keys()):
			return signalframes, df_main
		try:
			df = df_main.copy(deep=True)
			df['Signal'] = 'NA'
			df['Remarks'] = 'NA'
			df['Confidence'] = np.nan
			decimals = 2
			ltp = df['LTP'].iloc[0]
			length_old = len(signalframes)
			bbands_reco = self.get_quick_recommendation(full_df, 'bbands')
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-L', 0.05, ltp, '<=', 'BUY', '[LTP < BBands-L].{}'.format(bbands_reco), 'BUY', '[LTP ~ BBands-L].{}'.format(bbands_reco))
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-U', 0.05, ltp, '<=', 'SELL', '[LTP ~ BBands-U].{}'.format(bbands_reco), 'SELL', '[LTP > BBands-U].{}'.format(bbands_reco))
			rsi_reco = self.get_quick_recommendation(full_df, 'rsi')
			signalframes = self.update_signal_indicator(df, signalframes, 'rsi', 'RSI', resources.rsi().lower, resources.rsi().upper, '><', '* SELL' if rsi_reco.endswith('Buy') else 'SELL', '[RSI >= {}].{}'.format(resources.rsi().upper, rsi_reco), '* BUY' if rsi_reco.endswith('Buy') else 'BUY', '[RSI <= {}].{}'.format(resources.rsi().lower,rsi_reco))
			signalframes = self.update_signal_indicator(df, signalframes, 'emac', 'EMA(9)', 0.1, ltp, '>=', 'BUY', '[LTP > EMA(9)]', 'SELL', '[LTP < EMA(9)]')
			macd12 = df['macd(12)'].iloc[0]
			macd_reco = self.get_quick_recommendation(full_df, 'macd')
			signalframes = self.update_signal_indicator(df, signalframes, 'macd', 'macdsignal(9)', 0.05, macd12, '>=', '* BUY' if macd_reco.endswith('Buy') else 'BUY', '[MACD > EMA].{}'.format(macd_reco), '* SELL' if macd_reco.endswith('Buy') else 'SELL', '[MACD < EMA].{}'.format(macd_reco))
			length_new = len(signalframes)
			
			if length_new > length_old:
				saved_df = signalframes[len(signalframes) - 1]
				if saved_df.loc[:,'macd(12)'].iloc[0] > saved_df.loc[:,'macdsignal(9)'].iloc[0]:
					saved_df.loc[:,'Signal'].iloc[0] = '{}*'.format(saved_df.loc[:,'Signal'].iloc[0])
					signalframes[len(signalframes) - 1] = saved_df
			if self.indicator == 'macd' or self.indicator == 'all':
				df['macd(12)'] = df['macd(12)'].apply(lambda x: round(x, decimals))
				df['macdhist(26)'] = df['macdhist(26)'].apply(lambda x: round(x, decimals))
			self.trim_columns(df)
			df_main = df
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return signalframes, df_main
		return signalframes, df_main

	@tracelog
	def update_signal_indicator(self, df, signalframes, indicator, column, margin, comparator_value, ltp_label_comparator, true_type, true_remarks, false_type, false_remarks):
		deep_df = df.copy(deep=True)
		if self.indicator == indicator or self.indicator == 'all':
			value = round(deep_df[column].iloc[0],2)
			if ltp_label_comparator == '><':
				if (value is not None) and (value > comparator_value or value < margin):
					deep_df['Remarks'].iloc[0] = true_remarks if value > comparator_value else false_remarks
					deep_df['Signal'].iloc[0] = true_type if value > comparator_value else false_type
					deep_df = self.update_confidence_level(deep_df)
					default_logger().debug('To be added to update_signal_indicator.signalframes:\n{}\n'.format(deep_df.to_string(index=False)))
					default_logger().debug('update_signal_indicator.signalframes:\n{}\n'.format(signalframes))
					if len(signalframes) > 0:
						saved_df = signalframes[len(signalframes) - 1]
						if saved_df['Symbol'].iloc[0] == deep_df['Symbol'].iloc[0]:
							saved_df['Remarks'].iloc[0] = '{},{}'.format(saved_df['Remarks'].iloc[0],deep_df['Remarks'].iloc[0])
							saved_df['Signal'].iloc[0] = '{},{}'.format(saved_df['Signal'].iloc[0],deep_df['Signal'].iloc[0])
							saved_df['Confidence'].iloc[0] = max(saved_df['Confidence'].iloc[0],deep_df['Confidence'].iloc[0])
							signalframes[len(signalframes) - 1] = saved_df
						else:
							signalframes.append(deep_df)
					else:
						signalframes.append(deep_df)
			else:
				if (value is not None) and (abs(value-comparator_value) >= margin):
					if ltp_label_comparator == '<=':
						deep_df['Remarks'].iloc[0] = true_remarks if comparator_value - value <=0 else false_remarks
						deep_df['Signal'].iloc[0] = true_type if comparator_value - value <=0 else false_type
					elif ltp_label_comparator == '>=':
						deep_df['Remarks'].iloc[0] = true_remarks if comparator_value - value >=0 else false_remarks
						deep_df['Signal'].iloc[0] = true_type if comparator_value - value >=0 else false_type
					deep_df = self.update_confidence_level(deep_df)
					default_logger().debug('To be added to update_signal_indicator.signalframes:\n{}\n'.format(deep_df.to_string(index=False)))
					default_logger().debug('update_signal_indicator.signalframes:\n{}\n'.format(signalframes))
					if len(signalframes) > 0:
						saved_df = signalframes[len(signalframes) - 1]
						if saved_df['Symbol'].iloc[0] == deep_df['Symbol'].iloc[0]:
							saved_df['Remarks'].iloc[0] = '{},{}'.format(saved_df['Remarks'].iloc[0],deep_df['Remarks'].iloc[0])
							saved_df['Signal'].iloc[0] = '{},{}'.format(saved_df['Signal'].iloc[0],deep_df['Signal'].iloc[0])
							saved_df['Confidence'].iloc[0] = max(saved_df['Confidence'].iloc[0],deep_df['Confidence'].iloc[0])
							signalframes[len(signalframes) - 1] = saved_df
						else:
							signalframes.append(deep_df)
					else:
						signalframes.append(deep_df)
		return signalframes

	def get_quick_recommendation(self, df, indicator):
		if indicator not in ['rsi', 'bbands', 'macd', 'all']:
			return 'Unknown'
		sm = None
		tiny_df = None
		limited_df = df.tail(7)
		if indicator == 'macd' or indicator == 'all':
			tiny_df = pd.DataFrame({'Symbol':limited_df['Symbol'],'Date':limited_df['Date'],'macd(12)':limited_df['macd(12)'],'macdsignal(9)':limited_df['macdsignal(9)'], 'Close':limited_df['LTP']})
			sm = macdSignalStrategy(strict=True, intraday=False, requires_ledger=False)
		elif indicator == 'rsi' or indicator == 'all':
			tiny_df = pd.DataFrame({'Symbol':limited_df['Symbol'],'Date':limited_df['Date'],'RSI':limited_df['RSI'],'Close':limited_df['LTP']})
			sm = rsiSignalStrategy(strict=True, intraday=False, requires_ledger=False)
			sm.set_limits(resources.rsi().lower, resources.rsi().upper)
		elif indicator == 'bbands' or indicator == 'all':
			tiny_df = pd.DataFrame({'Symbol':limited_df['Symbol'],'Date':limited_df['Date'],'BBands-L':limited_df['BBands-L'], 'BBands-U':limited_df['BBands-U'], 'Close':limited_df['LTP']})
			sm = bbandsSignalStrategy(strict=True, intraday=False, requires_ledger=False)

		results, summary = sm.test_strategy(tiny_df)
		default_logger().debug(summary.to_string(index=False))
		if summary is not None and len(summary) > 0:
			last_row = summary.tail(1)
			return last_row['Recommendation'].iloc[0]
		else:
			return 'Unknown'

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
		df['Confidence'].iloc[0] = confidence
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

	def format_scan_volume_df(self, df, df_today, signalframes):
		default_logger().debug(df_today.to_string(index=False))
		signalframescopy = signalframes
		df_today = df_today.tail(1)
		df = df.sort_values(by='Date',ascending=True)
		# Get the 7 day average volume
		total_7day_volume = df['Volume'].sum()
		avg_volume = round(total_7day_volume/7,2)
		n = 1
		if current_datetime_in_ist_trading_time_range():
			# The last record will still be from yesterday
			df = df.tail(n)
		else:
			# When after today's trading session, we want to compare with yesterday's
			# The 2nd last record will be from yesterday
			n = 2
			df = df.tail(n)

		df['LTP']=np.nan
		df['%Change'] = np.nan
		df['TDYVol(%)']= np.nan
		df['7DVol(%)'] = np.nan
		df['Remarks']='NA'
		df['Yst7DVol(%)']= np.nan
		df['Yst%Del'] = df['%Deliverable'].apply(lambda x: round(x*100, 2))
		df['Tdy%Del']= np.nan
		df['PPoint']= df['PP']
		df['S1-R3']= np.nan
		

		volume_yest = df['Volume'].iloc[0]
		vwap = df['VWAP'].iloc[n-1]
		ltp = str(df_today['LTP'].iloc[0]).replace(',','')
		ltp = float(ltp)
		today_volume = float(str(df_today['TotalTradedVolume'].iloc[0]).replace(',',''))
		today_vs_yest = round(100* (today_volume - volume_yest)/volume_yest)
		df['Date'].iloc[n-1] = df_today['Updated'].iloc[0]
		df['%Change'].iloc[n-1] = df_today['pChange'].iloc[0]
		df['LTP'].iloc[n-1] = ltp
		df['TDYVol(%)'].iloc[n-1] = today_vs_yest
		df['7DVol(%)'].iloc[n-1] = round(100* (today_volume - avg_volume)/avg_volume)
		df['Yst7DVol(%)'].iloc[n-1] = round((100 * (volume_yest - avg_volume)/avg_volume))
		df['Tdy%Del'].iloc[n-1] = df_today['Tdy%Del'].iloc[0]
		df['Yst%Del'].iloc[n-1] = df['Yst%Del'].iloc[0]
		r3 = df['R3'].iloc[n-1]
		r2 = df['R2'].iloc[n-1]
		r1 = df['R1'].iloc[n-1]
		pp = df['PP'].iloc[n-1]
		s1 = df['S1'].iloc[n-1]
		s2 = df['S2'].iloc[n-1]
		s3 = df['S3'].iloc[n-1]
		crossover_point = False
		for pt, pt_name in zip([r3,r2,r1,pp,s1,s2,s3], ['R3', 'R2', 'R1', 'PP', 'S1', 'S2', 'S3']):
			# Stocks that are within 0.075% of crossover points
			if abs((ltp-pt)*100/ltp) - resources.scanner().crossover_reminder_percent <= 0:
				crossover_point = True
				df['Symbol'].iloc[n-1] = '** {}'.format(df['Symbol'].iloc[n-1])
				df['Remarks'].iloc[n-1]= pt_name
				df['S1-R3'].iloc[n-1] = pt
				break
		if not crossover_point:
			if ltp >= pp:
				df['Remarks'].iloc[n-1]='LTP >= PP'
				df['S1-R3'].iloc[n-1] = pp
				if ltp >= r3:
					df['Remarks'].iloc[n-1]='LTP >= R3'
					df['S1-R3'].iloc[n-1] = r3
				elif ltp >= r2:
					df['Remarks'].iloc[n-1]='LTP >= R2'
					df['S1-R3'].iloc[n-1] = r2
				elif ltp >= r1:
					df['Remarks'].iloc[n-1]='LTP >= R1'
					df['S1-R3'].iloc[n-1] = r1
				elif ltp < r1:
					df['Remarks'].iloc[n-1]='PP <= LTP < R1'
					df['S1-R3'].iloc[n-1] = r1
			else:
				df['Remarks'].iloc[n-1]='LTP < PP'
				df['S1-R3'].iloc[n-1] = pp
				if ltp >= s1:
					df['Remarks'].iloc[n-1]='PP > LTP >= S1'
					df['S1-R3'].iloc[n-1] = s1
				elif ltp >= s2:
					df['Remarks'].iloc[n-1]='LTP >= S2'
					df['S1-R3'].iloc[n-1] = s2
				elif ltp >= s3:
					df['Remarks'].iloc[n-1]='LTP >= S3'
					df['S1-R3'].iloc[n-1] = s3
				elif ltp < s3:
					df['Remarks'].iloc[n-1]='LTP < S3'
					df['S1-R3'].iloc[n-1] = s3
		if current_datetime_in_ist_trading_time_range():
			df['T0BuySellDiff']= np.nan
			df['T0BuySellDiff'].iloc[n-1] = df_today['T0BuySellDiff'].iloc[0]

		df = df.tail(1)
		default_logger().debug(df.to_string(index=False))
		for key in df.keys():
			# Symbol                  Date     VWAP     LTP %Change  TDYVol(%)  7DVol(%)    Remarks  Yst7DVol(%)  Yst%Del Tdy%Del   PPoint    S1-R3
			if not key in VOLUME_KEYS:
				df.drop([key], axis = 1, inplace = True)
		default_logger().debug(df.to_string(index=False))
		if today_vs_yest > 0 or ltp >= vwap or crossover_point:
			signalframescopy.append(df)
		return df, df_today, signalframescopy
	
	def last_7_days_timedelta(self):
		delhi_now = IST_datetime()
		if delhi_now.weekday() <= 1 or delhi_now.weekday() >= 6:
			return 11
		else:
			return 9

	# def buy_solid():
		# OBV trending upwards
		# RSI trending upwards. If not, then if it's closer to lower limit, strong buy
		# MACD trending upwards and +ve. MACD > MACD 12
		# LTP line > EMA9 and LTP > MA50
		# MOM +ve and trending upwards