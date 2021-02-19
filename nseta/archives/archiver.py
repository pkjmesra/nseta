import enum
import os
import pandas as pd
# import shutil
import sys
from datetime import datetime, timezone
import pytz

from nseta.common.log import tracelog, default_logger
from nseta.common.tradingtime import *
from nseta.resources.resources import *

__all__ = ['archiver', 'ResponseType']

class ResponseType(enum.Enum):
	Intraday = 1
	History = 2
	Quote = 3
	Volume = 4
	Default = 5
	Unknown = 6

class archiver:

	def __init__(self, data_dir=None):
		user_data_dir = resources.default().user_data_dir if data_dir is None else data_dir
		if user_data_dir is not None:
			try:
				if user_data_dir.startswith('~'):
					user_data_dir = user_data_dir.replace('~',os.path.expanduser('~'))
				original_umask = os.umask(0)
				if not os.path.exists(user_data_dir):
					os.makedirs(user_data_dir, mode=0o777)
					os.chmod(user_data_dir, mode=0o777)
				self._archival_dir = user_data_dir
			except OSError as e:
				default_logger().debug("Exception in archiver while creating user specified DIR:{}.".format(user_data_dir))
				default_logger().debug(e, exc_info=True)
				self._archival_dir = os.path.dirname(os.path.realpath(__file__))
			finally:
				os.umask(original_umask)
		else:
			self._archival_dir = os.path.dirname(os.path.realpath(__file__))
		try:
			self._logs_dir = os.path.join(self.archival_directory, 'logs')
			if not os.path.exists(self._logs_dir):
				os.makedirs(self._logs_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._logs_dir))
			default_logger().debug(e, exc_info=True)
		try:
			self._run_dir = os.path.join(self.archival_directory, 'run')
			if not os.path.exists(self._run_dir):
				os.makedirs(self._run_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._run_dir))
			default_logger().debug(e, exc_info=True)
		try:
			self._intraday_dir = os.path.join(self.run_directory, 'intraday')
			if not os.path.exists(self._intraday_dir):
				os.makedirs(self._intraday_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._intraday_dir))
			default_logger().debug(e, exc_info=True)
		try:
			self._history_dir = os.path.join(self.run_directory, 'history')
			if not os.path.exists(self._history_dir):
				os.makedirs(self._history_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._history_dir))
			default_logger().debug(e, exc_info=True)
		try:
			self._quote_dir = os.path.join(self.run_directory, 'quote')
			if not os.path.exists(self._quote_dir):
				os.makedirs(self._quote_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._quote_dir))
			default_logger().debug(e, exc_info=True)
		try:
			self._volume_dir = os.path.join(self.run_directory, 'volume')
			if not os.path.exists(self._volume_dir):
				os.makedirs(self._volume_dir)
		except OSError as e:
			default_logger().debug("Exception in archiver while creating DIR:{}.".format(self._volume_dir))
			default_logger().debug(e, exc_info=True)

	@property
	def archival_directory(self):
		return self._archival_dir

	@property
	def logs_directory(self):
		return self._logs_dir

	@property
	def run_directory(self):
		return self._run_dir

	@property
	def intraday_directory(self):
		return self._intraday_dir

	@property
	def history_directory(self):
		return self._history_dir
	
	@property
	def quote_directory(self):
		return self._quote_dir

	@property
	def volume_directory(self):
		return self._volume_dir

	@tracelog
	def get_path(self, symbol, response_type=ResponseType.History):
		if response_type == ResponseType.Intraday:
			return os.path.join(self.intraday_directory, symbol.upper())
		elif response_type == ResponseType.History:
			return os.path.join(self.history_directory, symbol.upper())
		elif response_type == ResponseType.Quote:
			return os.path.join(self.quote_directory, symbol.upper())
		elif response_type == ResponseType.Volume:
			return os.path.join(self.volume_directory, symbol.upper())
		elif response_type == ResponseType.Unknown:
			return None
		else:
			return os.path.join(self.run_directory, symbol.upper())

	@tracelog
	def get_directory(self, response_type=ResponseType.History):
		if response_type == ResponseType.Intraday:
			return self.intraday_directory
		elif response_type == ResponseType.History:
			return self.history_directory
		elif response_type == ResponseType.Quote:
			return self.quote_directory
		elif response_type == ResponseType.Volume:
			return self.volume_directory
		elif response_type == ResponseType.Unknown:
			return None
		else:
			return self.run_directory

	@tracelog
	def archive(self, df, symbol, response_type=ResponseType.Default):
		if df is not None and len(df) > 0:
			try:
				df = df.reset_index(drop=True)
				df.to_csv(self.get_path(symbol, response_type), index=False)
			except Exception as e:
				default_logger().debug("Exception in archiving for {} in {}.\n{}".format(symbol, response_type,df))
				default_logger().debug(e, exc_info=True)
				return None
		else:
			default_logger().debug("Empty DataFrame cannot be saved for symbol:{} and ResponseType:{}".format(symbol, response_type))

	@tracelog
	def restore(self, symbol, response_type=ResponseType.Default):
		df = None
		file_path = self.get_path(symbol, response_type)
		if file_path is None:
			return None
		if os.path.exists(file_path):
			try:
				df = pd.read_csv(file_path)
			except Exception as e:
				default_logger().debug("Exception in restore for {} in {}.".format(symbol, response_type))
				default_logger().debug(e, exc_info=True)
				return None
			if df is not None and len(df) > 0:
				df = df.reset_index(drop=True)
				last_modified = self.utc_to_local(self.get_last_modified_datetime(file_path))
				if current_datetime_in_ist_trading_time_range():
					cache_warn = 'Last Modified:{}. Fetched {} from the disk cache. You may wish to clear cache (nseta [command] --clear).'.format(str(last_modified), symbol)
					sys.stdout.write("\r{}".format(cache_warn))
				else:
					sys.stdout.write("\rLast Modified: {}. Fetched {} from the disk cache.".format(str(last_modified), symbol))
				sys.stdout.flush()
			else:
				default_logger().debug("Empty DataFrame for file:{}".format(file_path))
		else:
			default_logger().debug("File path does not exist:{}".format(file_path))
		return df

	@staticmethod
	def restore_from_path(file_path):
		df = None
		if os.path.exists(file_path):
			try:
				df = pd.read_csv(file_path)
			except Exception as e:
				default_logger().debug("Exception in restore for {}.".format(file_path))
				default_logger().debug(e, exc_info=True)
				return None
		return df

	@tracelog
	def clear_all(self, deep_clean=True,response_type=ResponseType.Default):
		directory = self.get_directory(response_type)
		if directory is None:
			return
		self.remove_cached_file(directory, force_clear=deep_clean, prefix= None if deep_clean else 'DF_')
		self.remove_cached_file(directory, force_clear=deep_clean, prefix= None if deep_clean else 'SIGNALDF_')
		if deep_clean:
			self.remove_cached_file(self.logs_directory, force_clear=True)

	@tracelog
	def clearcache(self, symbol=None, response_type=ResponseType.Default, force_clear=False):
		self.clear_all(deep_clean=False, response_type=response_type)
		try:
			if symbol is not None:
				file_path = self.get_path(symbol, response_type)
				if file_path is None:
					return
				if os.path.exists(file_path):
					self.remove_cached_file(file_path, force_clear)
				else:
					default_logger().debug("File path does not exist:{}".format(file_path))
			else:
				dir_path = self.get_directory(response_type)
				if dir_path is None:
					return
				# shutil.rmtree(dir_path) # For some reason even if it succeeds, many a time, the directory remains there.
				# # Let's iterate and remove each individual file.
				# default_logger().debug("Directory removed:{}".format(dir_path))
				self.remove_dir(dir_path, force_clear)
		except OSError as e:
			default_logger().debug("Exception in clearcache.")
			default_logger().debug(e, exc_info=True)

	def get_last_modified_datetime(self, file_path):
		last_modified = datetime.utcfromtimestamp(os.path.getmtime(file_path))
		return last_modified
	
	def utc_to_local(self, utc_dt):
		return pytz.utc.localize(utc_dt).replace(tzinfo=timezone.utc).astimezone(tz=None)

	@tracelog
	def remove_cached_file(self, file_path, force_clear=False, prefix=None):
		last_modified_unaware = self.get_last_modified_datetime(file_path)
		last_modified_aware = pytz.utc.localize(last_modified_unaware)
		should_clear = datetime_in_ist_trading_time_range(last_modified_aware)
		if should_clear or force_clear or prefix is not None:
			if os.path.isdir(file_path):
				self.remove_dir(file_path, force_clear, prefix=prefix)
			elif should_clear or force_clear:
				os.remove(file_path)
				default_logger().debug("File removed:{}".format(file_path))
		else:
			default_logger().debug("\nFetching from server will get the same data. If you want to force clear, use 'force_clear=True' option.")
			default_logger().debug("\nFile NOT removed:{}.\n Last Modified:{}".format(file_path, str(last_modified_aware)))

	def remove_dir(self, dir_path, force_clear=False, prefix=None):
		directory = os.fsencode(dir_path)
		for file in os.listdir(directory):
			filename = os.fsdecode(file)
			dir_file_path = os.path.join(dir_path, filename)
			self.remove_cached_file(dir_file_path, force_clear=True if prefix is not None and filename.upper().startswith(prefix) else force_clear, prefix=prefix)
