from nseta.scanner.baseScanner import baseScanner
from nseta.resources.resources import resources
from nseta.archives.archiver import *
from nseta.common.log import tracelog

__all__ = ['intradayScanner']

class intradayScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator, background)
		self.response_type = ResponseType.Intraday
		self.archiver = archiver()

	@tracelog
	def scan(self, option=None, periodicity="1", analyse=False):
		self.signal_columns = resources.scanner().intraday_scan_columns
		self.sortAscending = False
		super().scan(option= 'Cnt_Cdl' if option is None else option, periodicity=periodicity, analyse=analyse)

	def scan_background(self, scannerinstance, terminate_after_iter=0, wait_time=resources.scanner().background_scan_frequency_intraday):
		return super().scan_background(scannerinstance, terminate_after_iter=terminate_after_iter, wait_time=wait_time)

