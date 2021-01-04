import enum
import os
import pandas as pd

__all__ = ['archiver', 'ResponseType']

class ResponseType(enum.Enum):
	Intraday = 1
	History = 2
	Quote = 3
	Default = 4

class archiver:

	def __init__(self):
		self._archival_dir = os.path.dirname(os.path.realpath(__file__))
		self._intraday_dir = os.path.join(self.archival_directory, 'intraday')
		if not os.path.exists(self._intraday_dir):
			os.makedirs(self._intraday_dir)
		self._history_dir = os.path.join(self.archival_directory, 'history')
		if not os.path.exists(self._history_dir):
			os.makedirs(self._history_dir)
		self._quote_dir = os.path.join(self.archival_directory, 'quote')
		if not os.path.exists(self._quote_dir):
			os.makedirs(self._quote_dir)

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

	def get_path(self, symbol, response_type=ResponseType.History):
		if response_type == ResponseType.Intraday:
			return os.path.join(self.intraday_directory, symbol.upper())
		elif response_type == ResponseType.History:
			return os.path.join(self.history_directory, symbol.upper())
		elif response_type == ResponseType.Quote:
			return os.path.join(self.quote_directory, symbol.upper())
		else:
			return os.path.join(self.archival_directory, symbol.upper())

	def archive(self, df, symbol, response_type=ResponseType.Default):
		# df = df.reset_index(drop=True)
		df.to_csv(self.get_path(symbol, response_type))

	def restore(self, symbol, response_type=ResponseType.Default):
		df = None
		file_path = self.get_path(symbol, response_type)
		if os.path.exists(file_path):
			df = pd.read_csv(file_path)
		return df

