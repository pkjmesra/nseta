import pandas as pd
import datetime

from nseta.common.ti import ti
from nseta.scanner.baseStockScanner import baseStockScanner
from nseta.common.history import historicaldata
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger

INTRADAY_KEYS_MAPPING = {
	'Symbol': 'Symbol',
	'Date': 'Date',
	'Open': 'Open',
	'High': 'High',
	'Low': 'Low',
	'Close': 'LTP',
	'Volume': 'Volume',
	'Cum_Volume': 'Cum_Volume',
	'RSI': 'RSI',
	'MOM': 'MOM',
	'OBV' : 'OBV',
	'ATR' : 'ATR',
	'BBands-U': 'BBands-U',
	'BBands-L' : 'BBands-L',
	'SMA(10)': 'SMA(10)',
	'SMA(50)': 'SMA(50)',
	'EMA(9)': 'EMA(9)',
	'macd(12)': 'macd(12)',
	'macdsignal(9)': 'macdsignal(9)',
	'macdhist(26)': 'macdhist(26)',
	'R3': 'R3',
	'R2': 'R2',
	'R1': 'R1',
	'PP': 'PP',
	'S1': 'S1',
	'S2': 'S2',
	'S3': 'S3',
	'Cdl' : 'Cdl',
	'Cnt_Cdl' : 'Cnt_Cdl',
}

# KEY_MAPPING = {
# 	'dt': 'Date',
# 	'Open': 'Open',
# 	'High': 'High',
# 	'Low': 'Low',
# 	'Close': 'Close',
# 	'Volume': 'Volume',
# 	'Cum_Volume': 'Cum_Volume',
# }

__all__ = ['intradayStockScanner', 'INTRADAY_KEYS_MAPPING']

class intradayStockScanner(baseStockScanner):
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
		tailed_df = None
		for symbol in stocks:
			try:
				self.update_progress(symbol)
				df = self.ohlc_intraday_history(symbol)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df, rsi=True, mom=True, bbands=True, obv=True, macd=True, ema=True, atr=True)
					default_logger().debug(df.to_string(index=False))
					for key in df.keys():
						if not key in INTRADAY_KEYS_MAPPING.keys():
							df.drop([key], axis = 1, inplace = True)
						else:
							searchkey = INTRADAY_KEYS_MAPPING[key]
							if key != searchkey:
								if searchkey not in df.keys():
									df[searchkey] = df[key]
								df.drop([key], axis = 1, inplace = True)
					default_logger().debug(df.to_string(index=False))
					tailed_df = df.tail(1)
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
			signaldf = self.trim_columns(signaldf)
		return [tailed_df, signaldf]

	@tracelog
	def ohlc_intraday_history(self, symbol):
		df = None
		try:
			historyinstance = historicaldata()
			arch = archiver()
			df = arch.restore(symbol, ResponseType.Intraday)
			if df is None or len(df) == 0:
				df = historyinstance.daily_ohlc_history(symbol, start=datetime.date.today(), end = datetime.date.today(), intraday=True, type=ResponseType.Intraday, periodicity=self.periodicity)
			if df is not None and len(df) > 0:
				# default_logger().debug("Dataframe for " + symbol + "\n" + str(df))
				df = self.map_keys(df, symbol)
				arch.archive(df, symbol, ResponseType.Intraday)
			else:
				default_logger().debug("Empty dataframe for " + symbol)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			return None
		except SystemExit:
			return None
		return df

	def map_keys(self, df, symbol):
		try:
			# for key in KEY_MAPPING.keys():
			# 	searchkey = KEY_MAPPING[key]
			# 	if searchkey in df:
			# 		df[key] = df[searchkey]
			# 	else:
			# 		df[key] = np.nan
			# 		df[searchkey] = np.nan
			# 	if key in df.keys():
			# 		df.drop([key], axis = 1, inplace = True)
			df['Symbol'] = symbol
			df['datetime'] = df['Date']
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			default_logger().debug('Exception encountered for key: ' + searchkey + "\n")
		return df
