import pandas as pd
import datetime
import sys

from nseta.common.history import historicaldata
from nseta.common.ti import ti
from nseta.scanner.baseStockScanner import baseStockScanner
from nseta.scanner.intradayStockScanner import INTRADAY_KEYS_MAPPING
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger

__all__ = ['swingStockScanner']

SWING_PERIOD = 90

class swingStockScanner(baseStockScanner):
	def __init__(self, indicator='all'):
		super().__init__(indicator=indicator)

	@tracelog
	def scan_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		df = None
		signaldf = None
		tiinstance = ti()
		historyinstance = historicaldata()
		tailed_df = None
		# Time frame you want to pull data from
		start_date = datetime.datetime.now()-datetime.timedelta(days=SWING_PERIOD)
		end_date = datetime.datetime.now()
		for symbol in stocks:
			try:
				self.update_progress(symbol)
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date, type=ResponseType.History)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df, rsi=True, mom=True, bbands=True, obv=True, macd=True, ema=True, atr=True)
					df = df.sort_values(by='Date',ascending=True)
					default_logger().debug(df.to_string(index=False))
					for key in df.keys():
						# Symbol Series       Date  Prev Close     Open     High      Low     Last    Close     VWAP    Volume      Turnover  Trades  Deliverable Volume  %Deliverable
						if not key in INTRADAY_KEYS_MAPPING.keys():
							df.drop([key], axis = 1, inplace = True)
						elif (key in INTRADAY_KEYS_MAPPING.keys()):
							searchkey = INTRADAY_KEYS_MAPPING[key]
							if key != searchkey:
								df[searchkey] = df[key]
								df.drop([key], axis = 1, inplace = True)
					tailed_df = df.tail(1)
					default_logger().debug(tailed_df.to_string(index=False))
					frames.append(tailed_df)
					signalframes, df = self.update_signals(signalframes, tailed_df, df)
			except Exception as e:
				default_logger().debug("Exception encountered for " + symbol)
				default_logger().debug(e, exc_info=True)
			except SystemExit:
				sys.exit(1)
		if len(frames) > 0:
			tailed_df = pd.concat(frames)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [tailed_df, signaldf]
