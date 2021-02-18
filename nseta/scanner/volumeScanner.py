from nseta.scanner.baseScanner import baseScanner
from nseta.scanner.topPickScanner import topPickScanner
from nseta.resources.resources import resources
from nseta.archives.archiver import *
from nseta.common.tradingtime import IST_datetime
from nseta.common.log import tracelog
from nseta.scanner.baseStockScanner import ScannerType

__all__ = ['volumeScanner']

class volumeScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator, background)
		self.response_type = ResponseType.Volume
		self.archiver = archiver()

	@tracelog
	def scan(self, option=None, analyse=False):
		self.signal_columns = resources.scanner().volume_scan_columns
		self.sortAscending = False
		super().scan(option='TDYVol(%)' if option is None else option, analyse=analyse)

	def scan_background(self, scannerinstance, terminate_after_iter=0, wait_time=resources.scanner().background_scan_frequency_intraday):
		return super().scan_background(scannerinstance, terminate_after_iter=terminate_after_iter, wait_time=wait_time)

	def scan_results(self, df, signaldf, should_cache=True):
		if signaldf is not None and len(signaldf) > 0:
			str_signal_stocks_list = '{}'.format(signaldf['Symbol'].tolist())
			should_enum = resources.scanner().enumerate_volume_scan_signals
			csv_signals = str_signal_stocks_list.replace('[','').replace(']','').replace("'",'').replace(' ','') if should_enum else ''
			if should_enum:
				print("\nAs of {}, volume Signals: {}\n".format(IST_datetime(), csv_signals))
		super().scan_results(df, signaldf, should_cache)

	def scan_analysis(self, analysis_df):
		scanner = topPickScanner(scanner_type=ScannerType.TopPick, stocks=analysis_df['Symbol'].tolist(), indicator='macd', background=self.background)
		scanner.clear_cache(True, force_clear = True)
		scanner.scan(option='')
