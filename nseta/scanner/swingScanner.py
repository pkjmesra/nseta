from nseta.scanner.baseScanner import baseScanner
from nseta.resources.resources import resources
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger
from nseta.scanner.topPickScanner import topPickScanner
from nseta.scanner.baseStockScanner import ScannerType

__all__ = ['swingScanner']

class swingScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator, background)
		self.response_type = ResponseType.History
		self.archiver = archiver()

	@tracelog
	def scan(self, option=None, analyse=False):
		self.signal_columns = resources.scanner().swing_scan_columns
		self.sortAscending = True
		super().scan(option='Symbol', analyse=analyse)
		# TODO: Include get-quote results for OHLC of today before market closing hours for better accuracy

	@tracelog
	def scan_background(self, scannerinstance, terminate_after_iter=0, wait_time=0):
		default_logger().debug('Background running not supported yet. Stay tuned. Executing just once.')
		self.background = False
		self.scan(self.option)
		return 0

	def scan_analysis(self, analysis_df):
		scanner = topPickScanner(scanner_type=ScannerType.TopPick, stocks=analysis_df['Symbol'].tolist(), indicator='macd', background=self.background)
		scanner.clear_cache(True, force_clear = True)
		scanner.scan(option=None)