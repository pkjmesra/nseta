import threading, time
import click
import pandas as pd

from nseta.archives.archiver import *
from nseta.common.commons import human_format
from nseta.common.tradingtime import *
from nseta.resources.resources import *
from nseta.scanner.stockscanner import scanner
from nseta.common.log import tracelog, default_logger

class baseScanner:

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		self._scanner_type = scanner_type
		self._stocks = stocks
		self._indicator = indicator
		self._background = background
		self._option = None
		self._signal_columns = None
		self._scannerinstance = None
		self._archiver = None
		self._response_type = None
		self._sortAscending = False
		self._analyse = False

	@property
	def scanner_type(self):
		return self._scanner_type

	@property
	def scannerinstance(self):
		return self._scannerinstance

	@property
	def stocks(self):
		return self._stocks

	@stocks.setter
	def stocks(self, value):
		self._stocks = value

	@property
	def indicator(self):
		return self._indicator

	@property
	def sortAscending(self):
		return self._sortAscending

	@sortAscending.setter
	def sortAscending(self, value):
		self._sortAscending = value

	@property
	def background(self):
		return self._background

	@background.setter
	def background(self, value):
		self._background = value

	@property
	def archiver(self):
		return self._archiver

	@archiver.setter
	def archiver(self, value):
		self._archiver = value

	@property
	def response_type(self):
		return self._response_type

	@response_type.setter
	def response_type(self, value):
		self._response_type = value

	@property
	def signal_columns(self):
		return self._signal_columns

	@signal_columns.setter
	def signal_columns(self, value):
		self._signal_columns = value

	@property
	def option(self):
		return self._option

	@option.setter
	def option(self, value):
		self._option = value

	@property
	def analyse(self):
		return self._analyse

	@analyse.setter
	def analyse(self, value):
		self._analyse = value

	@tracelog
	def scan(self, option=None, periodicity=None, analyse=False):
		self.option = option
		self.analyse = analyse
		if self.scannerinstance is None:
			self._scannerinstance = scanner(indicator=self.indicator)
		if periodicity is not None:
			self.scannerinstance.periodicity = periodicity
		if self.background:
			b = threading.Thread(name='scan_{}_background'.format(self.scanner_type.name), 
					target=self.scan_background, args=[self.scannerinstance], daemon=True)
			b.start()
			b.join()
		else:
			df, signaldf = self.load_archived_scan_results()
			if df is None or len(df) == 0:
				df, signaldf = self.scannerinstance.scan(self.stocks, self.scanner_type)
			self.scan_results(df, signaldf)

	def scan_analysis(self, analysis_df):
		default_logger().debug('Analysis should be done in the child class.')

	def scan_results_file_names(self):
		return 'df_Scan_Results.{}'.format(self.indicator), 'signaldf_Scan_Results.{}'.format(self.indicator)

	@tracelog
	def load_archived_scan_results(self):
		df_file_name , signaldf_file_name = self.scan_results_file_names()
		df = self.archiver.restore(df_file_name, self.response_type)
		signaldf = self.archiver.restore(signaldf_file_name, self.response_type)
		return df, signaldf

	@tracelog
	def save_scan_results_archive(self, df, signaldf, should_cache=True):
		if should_cache or not current_datetime_in_ist_trading_time_range():
			df_file_name , signaldf_file_name = self.scan_results_file_names()
			if df is not None and len(df) > 0:
				self.archiver.archive(df, df_file_name, self.response_type)
				default_logger().debug('Saved to: {}'.format(df_file_name))
			if signaldf is not None and len(signaldf) > 0:
				self.archiver.archive(signaldf, signaldf_file_name,self.response_type)
				default_logger().debug('Saved to: {}'.format(signaldf_file_name))
	
	@tracelog
	def scan_results(self, df, signaldf, should_cache=True):
		if df is not None and len(df) > 0:
			self.save_scan_results_archive(df, signaldf, should_cache)
			default_logger().debug("\nAs of {}, all Stocks LTP and Signals:\n{}".format(IST_datetime(),df.to_string(index=False)))
		else:
			print('\nAs of {}, nothing to show here.'.format(IST_datetime()))
		if signaldf is not None and len(signaldf) > 0:
			ret = self.flush_signals(signaldf)
			if not ret:
				return
		else:
			print('\nAs of {}, no signals to show here.'.format(IST_datetime()))
		self.scan_finished()

	def scan_finished(self):
		self.scannerinstance.scan_finished(self.scanner_type)
		click.secho('{} scanning finished.'.format(self.scanner_type.name), fg='green', nl=True)

	def left_align(self, df, max_col_width=80):
		#convert tuple to dictionary
		# dict( 
		# 	[
		# 		#create a tuple such that (column name, max length of values in column or the column header itself)
		# 		(v, df[v].apply(lambda r: len(str(r)) if r!=None else 0).max()) 
		# 			for v in df.columns.values #iterates over all column values
		# 	])
		res1 = dict([(v, max(len(v),df[v].apply(lambda r: len(str(r)) if r!=None else 0).max()))for v in df.columns.values])
		#dict(zip(df, measurer(df.values.astype(str)).max(axis=0)))
		pd.set_option('display.max_colwidth', max_col_width)
		pd.set_option('display.max_rows', len(self.stocks))
		# pd.set_option('display.width', 1000)
		for key in res1.keys():
			old_key = key
			adj_key = old_key.ljust(res1[key])
			s = df[key]
			try:
				if adj_key == key:
					df.drop([key], axis = 1, inplace = True)
				df[adj_key] = s.apply(lambda x: x.ljust(res1[key]))
			except Exception:
				df[adj_key] = s
			finally:
				if adj_key != key:
					df.drop([key], axis = 1, inplace = True)
		return df

	def flush_signals(self, signaldf):
		if self.option is not None and len(self.option) > 0:
			signaldf = signaldf.sort_values(by=self.option, ascending=self.sortAscending)
		signaldf = signaldf.head(resources.scanner().scan_results_max_count)
		analysis_df = signaldf.copy(deep=True)
		user_signaldf = self.configure_user_display(signaldf, columns=self.signal_columns)
		print("\nAs of {}, {} Signals:\nSymbols marked with (*) have just crossed a crossover point.\n\n{}\n\n".format(IST_datetime(),self.scanner_type.name, self.left_align(user_signaldf, resources.scanner().max_column_length).to_string(index=False)))
		if self.analyse:
			self.scan_analysis(analysis_df)
		return True

	@tracelog
	def configure_user_display(self, df, columns=None):
		if columns is None:
			return df
		column_dict = {}
		for column in columns:
			kvp = column.rsplit('=',1)
			if len(kvp) > 1:
				column_dict[kvp[0]] = kvp[1]
			else:
				column_dict[kvp[0]] = kvp[0]
		column_keys = column_dict.keys()
		column_values = column_dict.values()
		user_df = pd.DataFrame(columns=column_values)
		keys = df.keys()
		for key in keys:
			if key in column_keys:
				user_df[column_dict[key]] = df[key].apply(lambda x: human_format(x))
		user_df = user_df.dropna(axis=1) 
		user_df = user_df.reset_index(drop=True) 
		return user_df

	@tracelog
	def clear_cache(self, clear, force_clear=False):
		if clear or self.background:
			df_file_name = 'df_Scan_Results.{}'.format(self.indicator)
			signaldf_file_name = 'signaldf_Scan_Results.{}'.format(self.indicator)
			self.archiver.clearcache(df_file_name, self.response_type, force_clear=force_clear)
			self.archiver.clearcache(signaldf_file_name, self.response_type, force_clear=force_clear)
			self.archiver.clearcache(response_type=self.response_type, force_clear=force_clear)

	@tracelog
	def scan_background_interrupt(self):
		global RUN_IN_BACKGROUND
		RUN_IN_BACKGROUND = False

	@tracelog
	def scan_background(self, scannerinstance, terminate_after_iter=0, wait_time=0):
		global RUN_IN_BACKGROUND
		RUN_IN_BACKGROUND = True
		iteration = 0
		while RUN_IN_BACKGROUND:
			iteration = iteration + 1
			if terminate_after_iter > 0 and iteration >= terminate_after_iter:
				RUN_IN_BACKGROUND = False
				break
			if scannerinstance is None:
				default_logger().debug('scannerinstance is None. Cannot proceed with background scanning')
				break
			self._scannerinstance = scannerinstance
			self.clear_cache(True, force_clear=True)
			if not current_datetime_in_ist_trading_time_range():
				click.secho('Running the {} scan for one last time because it is outside the trading hours'.format(self.scanner_type.name), fg='red', nl=True)
				terminate_after_iter = iteration
			df, signaldf = scannerinstance.scan(self.stocks, self.scanner_type)
			self.scan_results(df, signaldf, should_cache= False)
			time.sleep(wait_time)
		click.secho('Finished all iterations of scanning {}.'.format(self.scanner_type.name), fg='green', nl=True)
		return iteration
