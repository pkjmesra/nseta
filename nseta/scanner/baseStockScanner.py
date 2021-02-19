import enum
import inspect
import sys
import numpy as np
import pandas as pd
import threading

from time import time

from nseta.common.commons import *
from nseta.common.multithreadedScanner import multithreaded_scan
from nseta.common.log import tracelog, default_logger
from nseta.resources.resources import *
from nseta.strategy.rsiSignalStrategy import rsiSignalStrategy
from nseta.strategy.bbandsSignalStrategy import bbandsSignalStrategy
from nseta.strategy.macdSignalStrategy import macdSignalStrategy
from nseta.common.tradingtime import *

__all__ = ['baseStockScanner', 'TECH_INDICATOR_KEYS', 'ScannerType']
__scan_counter__ = 0
TECH_INDICATOR_KEYS = ['rsi', 'smac', 'emac', 'macd', 'bbands', 'all']

class ScannerType(enum.Enum):
	Intraday = 1
	Live = 2
	Quote = 3
	Swing = 4
	Volume = 5
	TopReversal = 6
	BottomReversal = 7
	TopPick = 8
	News = 9
	Unknown = 10

class baseStockScanner:
	def __init__(self, indicator='all'):
		if indicator not in TECH_INDICATOR_KEYS:
			indicator = 'all'
		self._indicator = indicator
		self._stocksdict = {}
		self._instancedict = {}
		self._total_counter = 0
		self._periodicity = None
		self._time_spent = 0

	@property
	def time_spent(self):
		return self._time_spent

	@time_spent.setter
	def time_spent(self, value):
		self._time_spent = value

	@property
	def total_counter(self):
		return self._total_counter

	@total_counter.setter
	def total_counter(self, value):
		self._total_counter = value

	@property
	def indicator(self):
		return self._indicator

	# @indicator.setter
	# def indicator(self, value):
	# 	self._indicator = value

	@property
	def periodicity(self):
		return self._periodicity

	@periodicity.setter
	def periodicity(self, value):
		self._periodicity = value

	@property
	def instancedict(self):
		return self._instancedict

	@property
	def stocksdict(self):
		return self._stocksdict

	# @stocksdict.setter
	# def stocksdict(self, value):
	# 	self._stocksdict = value

	@tracelog
	def stocks_list(self, stocks=[]):
		global __scan_counter__
		__scan_counter__ = 0
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if stocks is not None and len(stocks) > 0 else resources.default().stocks
		self.total_counter = len(stocks)
		return stocks

	def multithreadedScanner_callback(self, **kwargs):
		scanner_type = kwargs['scanner_type']
		del(kwargs['scanner_type'])
		callback_instance = self.get_instance(scanner_type=scanner_type)
		callback_instance.total_counter = self.total_counter
		if self.periodicity is not None:
			callback_instance.periodicity = self.periodicity
		return callback_instance.scan_quanta(**kwargs)

	def get_instance(self, scanner_type=ScannerType.Unknown):
		return self

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
		self.time_spent += time_spent
		return list_returned.pop(0), list_returned.pop(0)

	def scan_finished(self, scanner_type):
		sys.stdout.write("\rDone.".ljust(120))
		sys.stdout.flush()
		print("\nThis run of {} scan took {:.1f} sec".format(scanner_type.name, self.time_spent))

	def update_progress(self, symbol):
		global __scan_counter__
		with threading.Lock():
			__scan_counter__ += 1
		sys.stdout.write("\r{}/{}. Fetching for {}".ljust(120).format(__scan_counter__, self.total_counter, symbol))
		sys.stdout.flush()

	def last_x_days_timedelta(self):
		delhi_now = IST_datetime()
		if delhi_now.weekday() <= 1 or delhi_now.weekday() >= 6:
			return 40
		else:
			return 36

	@tracelog
	def update_signals(self, signalframes, df_main, full_df=None):
		if (df_main is None) or (len(df_main) < 1) or (not 'RSI' in df_main.keys() and not 'EMA(9)' in df_main.keys()):
			return signalframes, df_main
		try:
			df = df_main.copy(deep=True)
			df['Signal'] = 'NA'
			df['Remarks'] = 'NA'
			df['Confidence'] = np.nan
			ltp = df['LTP'].iloc[0]
			length_old = len(signalframes)
			bbands_reco = self.get_quick_recommendation(full_df, 'bbands')
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-L', 0.05, ltp, '<=', 'BUY', '[LTP < BBands-L].{}'.format(bbands_reco), 'BUY', '[LTP ~ BBands-L].{}'.format(bbands_reco))
			signalframes = self.update_signal_indicator(df, signalframes, 'bbands', 'BBands-U', 0.05, ltp, '<=', 'SELL', '[LTP ~ BBands-U].{}'.format(bbands_reco), 'SELL', '[LTP > BBands-U].{}'.format(bbands_reco))
			rsi_reco = self.get_quick_recommendation(full_df, 'rsi')
			signalframes = self.update_signal_indicator(df, signalframes, 'rsi', 'RSI', resources.rsi().lower, resources.rsi().upper, '><', rsi_reco.upper(), '[RSI >= {}].{}'.format(resources.rsi().upper, rsi_reco), rsi_reco.upper(), '[RSI <= {}].{}'.format(resources.rsi().lower,rsi_reco))
			signalframes = self.update_signal_indicator(df, signalframes, 'emac', 'EMA(9)', 0.1, ltp, '>=', 'BUY', '[LTP > EMA(9)]', 'SELL', '[LTP < EMA(9)]')
			macd12 = df['macd(12)'].iloc[0]
			macd_reco = self.get_quick_recommendation(full_df, 'macd')
			signalframes = self.update_signal_indicator(df, signalframes, 'macd', 'macdsignal(9)', 0.05, macd12, '>=', macd_reco.upper(), '[MACD > EMA].{}'.format(macd_reco), macd_reco.upper(), '[MACD < EMA].{}'.format(macd_reco))
			length_new = len(signalframes)
			
			if length_new > length_old:
				saved_df = signalframes[len(signalframes) - 1]
				if saved_df.loc[:,'macd(12)'].iloc[0] > saved_df.loc[:,'macdsignal(9)'].iloc[0]:
					saved_df.loc[:,'Signal'].iloc[0] = '{}'.format(saved_df.loc[:,'Signal'].iloc[0])
					signalframes[len(signalframes) - 1] = saved_df
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return signalframes, df
		return signalframes, df

	@tracelog
	def update_signal_indicator(self, df, signalframes, indicator, column, margin, comparator_value, ltp_label_comparator, true_type, true_remarks, false_type, false_remarks):
		deep_df = df.copy(deep=True)
		if self.indicator == indicator or self.indicator == 'all':
			value = round(deep_df[column].iloc[0],3)
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
			return '-'
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

		default_logger().debug('tiny_df:\n{}'.format(tiny_df.to_string(index=False)))
		results, summary = sm.test_strategy(tiny_df)
		if summary is not None and len(summary) > 0:
			default_logger().debug(summary.to_string(index=False))
			last_row = summary.tail(1)
			reco = last_row['Recommendation'].iloc[0]
			return '-' if reco == 'Unknown' else reco
		else:
			return '-'

	def update_confidence_level(self, df):
		rsi = round(df['RSI'].iloc[0],2)
		bbandsl = round(df['BBands-L'].iloc[0],2)
		bbandsu = round(df['BBands-U'].iloc[0],2)
		ema = round(df['EMA(9)'].iloc[0],2)
		macdsignal = round(df['macdsignal(9)'].iloc[0],3)
		macd12 = round(df['macd(12)'].iloc[0],3)
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
			# 'rsi': ['RSI'], 
			'emac': ['EMA(9)'], 
			# 'macd': ['macdsignal(9)', 'macd(12)', 'macdhist(26)']}
			'macd': ['macdhist(26)']}
		col_keys = columns.keys()
		df_keys = df.keys()
		for indicator in col_keys:
			if self.indicator != indicator and self.indicator != 'all':
				for key in columns[indicator]:
					if key in df_keys:
						df.drop([key], axis = 1, inplace = True)
		# if 'MOM' in df_keys:
		# 	df.drop(['MOM'], axis = 1, inplace = True)
		return df
