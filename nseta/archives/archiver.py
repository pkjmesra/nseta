import enum
import os
import pandas as pd
# import shutil
import sys
from datetime import datetime, time

from nseta.common.log import tracelog, default_logger
from nseta.common.tradingtime import current_time_in_ist_trading_time_range

__all__ = ['archiver', 'ResponseType']

class ResponseType(enum.Enum):
	Intraday = 1
	History = 2
	Quote = 3
	Default = 4

class archiver:

	def __init__(self):
		self._archival_dir = os.path.dirname(os.path.realpath(__file__))
		try:
			self._intraday_dir = os.path.join(self.archival_directory, 'intraday')
			if not os.path.exists(self._intraday_dir):
				os.makedirs(self._intraday_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._intraday_dir))
			default_logger().debug(e, exc_info=True)
			pass
		try:
			self._history_dir = os.path.join(self.archival_directory, 'history')
			if not os.path.exists(self._history_dir):
				os.makedirs(self._history_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._history_dir))
			default_logger().debug(e, exc_info=True)
			pass
		try:
			self._quote_dir = os.path.join(self.archival_directory, 'quote')
			if not os.path.exists(self._quote_dir):
				os.makedirs(self._quote_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._quote_dir))
			default_logger().debug(e, exc_info=True)
			pass

	@property
	def archival_directory(self):
		return self._archival_dir

	@property
	def intraday_directory(self):
		return self._intraday_dir

	@property
	def history_directory(self):
		return self._history_dir
	
	@property
	def quote_directory(self):
		return self._quote_dir

	@tracelog
	def get_path(self, symbol, response_type=ResponseType.History):
		if response_type == ResponseType.Intraday:
			return os.path.join(self.intraday_directory, symbol.upper())
		elif response_type == ResponseType.History:
			return os.path.join(self.history_directory, symbol.upper())
		elif response_type == ResponseType.Quote:
			return os.path.join(self.quote_directory, symbol.upper())
		else:
			return os.path.join(self.archival_directory, symbol.upper())

	@tracelog
	def get_directory(self, response_type=ResponseType.History):
		if response_type == ResponseType.Intraday:
			return self.intraday_directory
		elif response_type == ResponseType.History:
			return self.history_directory
		elif response_type == ResponseType.Quote:
			return self.quote_directory
		else:
			return self.archival_directory

	@tracelog
	def archive(self, df, symbol, response_type=ResponseType.Default):
		if df is not None and len(df) > 0:
			df = df.reset_index(drop=True)
			df.to_csv(self.get_path(symbol, response_type), index=False)
		else:
			default_logger().debug("Empty DataFrame cannot be saved for symbol:{} and ResponseType:{}".format(symbol, response_type))

	@tracelog
	def restore(self, symbol, response_type=ResponseType.Default):
		df = None
		file_path = self.get_path(symbol, response_type)
		if os.path.exists(file_path):
			df = pd.read_csv(file_path)
			if df is not None and len(df) > 0:
				df = df.reset_index(drop=True)
				last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
				if current_time_in_ist_trading_time_range():
					cache_warn = 'Last Modified:{}. Fetched {} from the disk cache. You may wish to clear cache (nseta [command] --clear).'.format(str(last_modified), symbol)
					sys.stdout.write("\r{}".format(cache_warn))
				else:
					sys.stdout.write("\rLast Modified: {}. ***** Fetched {} from the disk cache. *****.".format(str(last_modified), symbol))
				sys.stdout.flush()
			else:
				default_logger().debug("Empty DataFrame for file:{}".format(file_path))
		else:
			default_logger().debug("File path does not exist:{}".format(file_path))
		return df

	@tracelog
	def clearcache(self, symbol=None, response_type=ResponseType.Default):
		try:
			if symbol is not None:
				file_path = self.get_path(symbol, response_type)
				if os.path.exists(file_path):
					os.remove(file_path)
					default_logger().debug("File removed:{}".format(file_path))
				else:
					default_logger().debug("File path does not exist:{}".format(file_path))
			else:
				dir_path = self.get_directory(response_type)
				# shutil.rmtree(dir_path) # For some reason even if it succeeds, many a time, the directory remains there.
				# # Let's iterate and remove each individual file.
				# default_logger().debug("Directory removed:{}".format(dir_path))
				directory = os.fsencode(dir_path)
				for file in os.listdir(directory):
					filename = os.fsdecode(file)
					dir_file_path = os.path.join(dir_path, filename)
					os.remove(dir_file_path)
					default_logger().debug("File removed:{}".format(dir_file_path))
		except OSError as e:
			default_logger().debug("Exception in clearcache.")
			default_logger().debug(e, exc_info=True)
			pass
