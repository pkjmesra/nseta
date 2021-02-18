from nseta.scanner.baseScanner import baseScanner
from nseta.resources.resources import resources
from nseta.archives.archiver import *
from nseta.common.log import tracelog

__all__ = ['liveScanner']

class liveScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator, background)
		self.response_type = ResponseType.Quote
		self.archiver = archiver()

	@tracelog
	def scan(self, option=None, analyse=False):
		self.signal_columns = resources.scanner().live_scan_columns
		self.sortAscending = False
		super().scan(option='% Delivery', analyse=analyse)

	@tracelog
	def scan_background(self, scannerinstance, terminate_after_iter=0, wait_time=resources.scanner().background_scan_frequency_live):
		return super().scan_background(scannerinstance, terminate_after_iter=terminate_after_iter, wait_time=wait_time)
