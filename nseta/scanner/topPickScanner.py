from nseta.scanner.intradayScanner import intradayScanner
from nseta.resources.resources import resources
import pandas as pd
from nseta.common.tradingtime import current_datetime_in_ist_trading_time_range
from nseta.common.log import tracelog, default_logger

__all__ = ['topPickScanner']

class topPickScanner(intradayScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,'macd', background)
		self._period_1_signals = None

	@property
	def period_1_signals(self):
		return self._period_1_signals

	@tracelog
	def scan(self, option=None, periodicity="1", analyse=False):
		self.clear_cache(True, force_clear = True)
		super().scan(option= 'Confidence' if option is None else option, periodicity=periodicity, analyse=analyse)

	def scan_background(self, scannerinstance, terminate_after_iter=0, wait_time=resources.scanner().background_scan_frequency_intraday):
		return super().scan_background(scannerinstance, terminate_after_iter=terminate_after_iter, wait_time=wait_time)

	def load_archived_scan_results(self):
		if self.period_1_signals is not None:
			return None, None
		else:
			return super().load_archived_scan_results()

	@tracelog
	def flush_signals(self, signaldf):
		if self.period_1_signals is None:
			self._period_1_signals = signaldf
			default_logger().debug('Period_1_signals:\n{}\n'.format(signaldf))
			self.stocks = signaldf['Symbol'].tolist()
			self.scan(self.option, periodicity="2")
			return False
		else:
			default_logger().debug('Period_1_signals:\n{}\n'.format(self.period_1_signals))
			default_logger().debug('Period_5_signals:\n{}\n'.format(signaldf))
			intersected_rows = []
			for index, row in signaldf.iterrows():
				symbol_period_5 = row['Symbol']
				signal_period_5 = row['Signal']
				df = self.period_1_signals[(self.period_1_signals['Symbol'] == symbol_period_5) & (self.period_1_signals['Signal'] == signal_period_5)]
				# Both period 1 and period 5 are aligned in recommendations
				if df is not None and len(df) > 0:
					if abs(abs(df['macd(12)'].iloc[0]) - abs(df['macdsignal(9)'].iloc[0])) <= 0.15:
						df['Confidence'].iloc[0] = 100
					intersected_rows.append(df)
			intersected_df= pd.concat(intersected_rows)
			return super().flush_signals(intersected_df)
