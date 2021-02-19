from nseta.scanner.baseScanner import baseScanner
from nseta.common.log import tracelog
from nseta.archives.archiver import *
from nseta.common.tradingtime import IST_datetime

__all__ = ['newsScanner']

class newsScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator=indicator, background=background)
		self.response_type = ResponseType.Unknown
		self.archiver = archiver()

	@tracelog
	def scan(self, option=None, analyse=False):
		self.sortAscending = True
		super().scan(option= 'h' if option is None else option, analyse=analyse)

	@tracelog
	def flush_signals(self, signaldf):
		if self.option is not None and len(self.option) > 0:
			signaldf = signaldf.sort_values(by=self.option, ascending=self.sortAscending)
		user_signaldf = self.configure_user_display(signaldf, columns=self.signal_columns)
		user_signaldf.drop(['h'], axis = 1, inplace = True)
		df = self.left_align(user_signaldf)
		print("\nAs of {}, {}:\n{}\n".format(IST_datetime(),self.scanner_type.name, df.to_string(index=False)))
		return True

