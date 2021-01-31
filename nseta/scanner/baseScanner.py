import threading, time
import click
import pandas as pd

from nseta.archives.archiver import *
from nseta.common.tradingtime import *
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
		self._archiver = None
		self._response_type = None
		self._sortAscending = False

	@property
	def scanner_type(self):
		return self._scanner_type

	@property
	def stocks(self):
		return self._stocks

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

	@tracelog
	def scan(self, option=None):
		self.option = option
		scannerinstance = scanner(indicator=self.indicator)
		if self.background:
			b = threading.Thread(name='scan_{}_background'.format(self.scanner_type.name), 
					target=self.scan_background, args=[scannerinstance], daemon=True)
			b.start()
			b.join()
		else:
			df, signaldf = self.load_archived_scan_results()
			if df is None or len(df) == 0:
				df, signaldf = scannerinstance.scan(self.stocks, self.scanner_type)
			self.scan_results(df, signaldf)

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
			print('As of {}, nothing to show here.'.format(IST_datetime()))
		if signaldf is not None and len(signaldf) > 0:
			if self.option is not None:
				signaldf = signaldf.sort_values(by=self.option, ascending=self.sortAscending)
			user_signaldf = self.configure_user_display(signaldf, columns=self.signal_columns)
			print("\nAs of {}, {} Signals:\nSymbols marked with (*) have just crossed a crossover point.\n{}".format(IST_datetime(),self.scanner_type.name, user_signaldf.to_string(index=False)))
		else:
			print('As of {}, no signals to show here.'.format(IST_datetime()))
		click.secho('{} scanning finished.'.format(self.scanner_type.name), fg='green', nl=True)

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
				user_df[column_dict[key]] = df[key]
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
			self.clear_cache(True, force_clear=True)
			df, signaldf = scannerinstance.scan(self.stocks, self.scanner_type)
			self.scan_results(df, signaldf, should_cache= False)
			time.sleep(wait_time)
		click.secho('Finished all iterations of scanning {}.'.format(self.scanner_type.name), fg='green', nl=True)
		return iteration
