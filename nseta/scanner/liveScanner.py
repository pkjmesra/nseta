from nseta.scanner.baseScanner import baseScanner
from nseta.resources.resources import resources
from nseta.archives.archiver import *
from nseta.scanner.tiscanner import scanner
from nseta.common.log import tracelog

__all__ = ['liveScanner']

class liveScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator, background)
		self.response_type = ResponseType.Quote
		self.archiver = archiver()

	@tracelog
	def scan(self, option=None):
		self.signal_columns = resources.scanner().live_scan_columns
		scannerinstance = scanner(indicator=self.indicator)
		self.scanner_func = scannerinstance.scan_live
		super().scan(option='% Delivery')

	@tracelog
	def scan_background(self, terminate_after_iter=0, wait_time=resources.scanner().background_scan_frequency_live):
		return super().scan_background(terminate_after_iter=terminate_after_iter, wait_time=wait_time)
