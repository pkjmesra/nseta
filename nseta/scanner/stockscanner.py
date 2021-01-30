import inspect
import numpy as np
import pandas as pd
import talib as ta
import datetime
import sys

from nseta.common.commons import *
from nseta.archives.archiver import *
from nseta.common.history import historicaldata
from nseta.resources.resources import *
from nseta.common.log import tracelog, default_logger
from nseta.common.ti import ti
from nseta.live.live import get_live_quote
from nseta.common.tradingtime import *
from nseta.scanner.baseStockScanner import baseStockScanner, TECH_INDICATOR_KEYS, ScannerType

__all__ = ['KEY_MAPPING', 'scanner', 'TECH_INDICATOR_KEYS', 'ScannerType']

SWING_PERIOD = 90

KEY_MAPPING = {
	'dt': 'Date',
	'open': 'Open',
	'High': 'High',
	'Low': 'Low',
	'close': 'Close',
	# 'volume': 'Volume',
}

VOLUME_KEYS = ['Remarks','PPoint', 'S1-R3','Symbol', 'Date', 'LTP', 'VWAP', 'Yst%Del', '7DayAvgVolume', 'Yst7DVol(%)', 'TodaysVolume','TDYVol(%)', '7DVol(%)', 'Tdy%Del', 'T0BuySellDiff', '%Change']

INTRADAY_KEYS_MAPPING = {
	'Symbol': 'Symbol',
	'Date': 'Date',
	'Close': 'LTP',
	# 'Low': 'Prev_Close',
	'RSI': 'RSI',
	'MOM': 'MOM',
	'BBands-U': 'BBands-U',
	'BBands-L' : 'BBands-L',
	# 'SMA(10)': 'SMA(10)',
	# 'SMA(50)': 'SMA(50)',
	'EMA(9)': 'EMA(9)',
	'macd(12)': 'macd(12)',
	'macdsignal(9)': 'macdsignal(9)',
	'macdhist(26)': 'macdhist(26)',
	# 'PP':'PP',
	# 'R1': 'R1',
	# 'S1': 'S1',
	# 'R2': 'R2',
	# 'S2': 'S2',
	# 'R3': 'R3',
	# 'S3': 'S3',
}

# PIVOT_KEYS =['PP', 'R1','S1','R2','S2','R3','S3']

class scanner(baseStockScanner):
	def __init__(self, indicator='all'):
		super().__init__(indicator=indicator)
		self._keys = ['symbol','previousClose', 'lastPrice', 'deliveryToTradedQuantity', 'BuySellDiffQty', 'totalTradedVolume', 'pChange']

	@property
	def keys(self):
		return self._keys

	def get_func_name(self, scanner_type=ScannerType.Unknown):
		scanner_dict = {(ScannerType.Intraday).name:self.scan_intraday_quanta,
			(ScannerType.Live).name:self.scan_live_quanta,
			(ScannerType.Swing).name:self.scan_swing_quanta,
			(ScannerType.Volume).name:self.scan_volume_quanta}
		return scanner_dict[scanner_type.name]

	@tracelog
	def scan_live_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		df = None
		signaldf = None
		for stock in stocks:
			try:
				self.update_progress(stock)
				result, primary = get_live_quote(stock, keys = self.keys)
				if primary is not None and len(primary) > 0:
					row = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP', '% Delivery', 'Buy - Sell', 'TotalTradedVolume', 'pChange'], index = [''])
					value = (row['LTP'][0]).replace(' ','').replace(',','')
					if stock in self.stocksdict:
						(self.stocksdict[stock]).append(float(value))
					else:
						self.stocksdict[stock] = [float(value)]
					index = len(self.stocksdict[stock])
					if index >= 15:
						dfclose = pd.DataFrame(self.stocksdict[stock], columns = ['Close'])
						rsi = ta.RSI(dfclose['Close'],resources.rsi().period)
						rsivalue = rsi[index -1]
						row['RSI'] = rsivalue
						default_logger().debug(stock + " RSI:" + str(rsi))
						if rsivalue > resources.rsi().upper or rsivalue < resources.rsi().lower:
							signalframes.append(row)
					frames.append(row)
			except Exception as e:
				default_logger().debug("Exception encountered for " + stock)
				default_logger().debug(e, exc_info=True)
		if len(frames) > 0:
			df = pd.concat(frames)
			# default_logger().debug(df.to_string(index=False))
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
			# default_logger().debug(signaldf.to_string(index=False))
		return [df, signaldf]

	@tracelog
	def scan_intraday_quanta(self, **kwargs):
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
					df = tiinstance.update_ti(df)
					for key in df.keys():
						if not key in INTRADAY_KEYS_MAPPING.keys():
							df.drop([key], axis = 1, inplace = True)
						else:
							searchkey = INTRADAY_KEYS_MAPPING[key]
							if key != searchkey:
								if searchkey not in df.keys():
									df[searchkey] = df[key]
								df.drop([key], axis = 1, inplace = True)
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
		return [tailed_df, signaldf]

	@tracelog
	def scan_swing_quanta(self, **kwargs):
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
					df = tiinstance.update_ti(df)
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

	@tracelog
	def scan_volume_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		signaldf = None
		tiinstance = ti()
		historyinstance = historicaldata()
		# Time frame you want to pull data from
		start_date = datetime.datetime.now()-datetime.timedelta(days=self.last_7_days_timedelta())
		arch = archiver()
		end_date = datetime.datetime.now()
		for symbol in stocks:
			df_today = None
			primary = None
			df = None
			try:
				self.update_progress(symbol)
				df = historyinstance.daily_ohlc_history(symbol, start_date, end_date, type=ResponseType.Volume)
				if df is not None and len(df) > 0:
					df = tiinstance.update_ti(df)
					default_logger().debug(df.to_string(index=False))
					primary = arch.restore('{}_live_quote'.format(symbol), ResponseType.Volume)
					if primary is None or len(primary) == 0:
						result, primary = get_live_quote(symbol, keys = self.keys)
					else:
						df_today = primary
					if (primary is not None and len(primary) > 0):
						if df_today is None:
							df_today = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP', 'Tdy%Del', 'T0BuySellDiff', 'TotalTradedVolume','pChange'], index = [''])
							arch.archive(df_today, '{}_live_quote'.format(symbol), ResponseType.Volume)
						df, df_today, signalframes = self.format_scan_volume_df(df, df_today, signalframes)
						frames.append(df)
				else:
					default_logger().debug("Could not fetch daily_ohlc_history for {}".format(symbol))
			except Exception as e:
				default_logger().debug("Exception encountered for {}".format(symbol))
				default_logger().debug(e, exc_info=True)
				continue
			except SystemExit:
				sys.exit(1)
		if len(frames) > 0:
			df = pd.concat(frames)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [df, signaldf]

	@tracelog
	def ohlc_intraday_history(self, symbol):
		df = None
		try:
			historyinstance = historicaldata()
			arch = archiver()
			df = arch.restore(symbol, ResponseType.Intraday)
			if df is None or len(df) == 0:
				df = historyinstance.daily_ohlc_history(symbol, start=datetime.date.today(), end = datetime.date.today(), intraday=True, type=ResponseType.Intraday)
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
			for key in KEY_MAPPING.keys():
				searchkey = KEY_MAPPING[key]
				if searchkey in df:
					df[key] = df[searchkey]
				else:
					df[key] = np.nan
					df[searchkey] = np.nan
				if key in df.keys():
					df.drop([key], axis = 1, inplace = True)
			df['Symbol'] = symbol
			df['datetime'] = df['Date']
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			default_logger().debug('Exception encountered for key: ' + searchkey + "\n")
		return df

	def format_scan_volume_df(self, df, df_today, signalframes):
		default_logger().debug(df_today.to_string(index=False))
		signalframescopy = signalframes
		df_today = df_today.tail(1)
		df = df.sort_values(by='Date',ascending=True)
		# Get the 7 day average volume
		total_7day_volume = df['Volume'].sum()
		avg_volume = round(total_7day_volume/7,2)
		n = 1
		if current_datetime_in_ist_trading_time_range():
			# The last record will still be from yesterday
			df = df.tail(n)
		else:
			# When after today's trading session, we want to compare with yesterday's
			# The 2nd last record will be from yesterday
			n = 2
			df = df.tail(n)

		df['LTP']=np.nan
		df['%Change'] = np.nan
		df['TDYVol(%)']= np.nan
		df['7DVol(%)'] = np.nan
		df['Remarks']='NA'
		df['Yst7DVol(%)']= np.nan
		df['Yst%Del'] = df['%Deliverable'].apply(lambda x: round(x*100, 2))
		df['Tdy%Del']= np.nan
		df['PPoint']= df['PP']
		df['S1-R3']= np.nan
		

		volume_yest = df['Volume'].iloc[0]
		vwap = df['VWAP'].iloc[n-1]
		ltp = str(df_today['LTP'].iloc[0]).replace(',','')
		ltp = float(ltp)
		today_volume = float(str(df_today['TotalTradedVolume'].iloc[0]).replace(',',''))
		today_vs_yest = round(100* (today_volume - volume_yest)/volume_yest)
		df['Date'].iloc[n-1] = df_today['Updated'].iloc[0]
		df['%Change'].iloc[n-1] = df_today['pChange'].iloc[0]
		df['LTP'].iloc[n-1] = ltp
		df['TDYVol(%)'].iloc[n-1] = today_vs_yest
		df['7DVol(%)'].iloc[n-1] = round(100* (today_volume - avg_volume)/avg_volume)
		df['Yst7DVol(%)'].iloc[n-1] = round((100 * (volume_yest - avg_volume)/avg_volume))
		df['Tdy%Del'].iloc[n-1] = df_today['Tdy%Del'].iloc[0]
		df['Yst%Del'].iloc[n-1] = df['Yst%Del'].iloc[0]
		r3 = df['R3'].iloc[n-1]
		r2 = df['R2'].iloc[n-1]
		r1 = df['R1'].iloc[n-1]
		pp = df['PP'].iloc[n-1]
		s1 = df['S1'].iloc[n-1]
		s2 = df['S2'].iloc[n-1]
		s3 = df['S3'].iloc[n-1]
		crossover_point = False
		for pt, pt_name in zip([r3,r2,r1,pp,s1,s2,s3], ['R3', 'R2', 'R1', 'PP', 'S1', 'S2', 'S3']):
			# Stocks that are within 0.075% of crossover points
			if abs((ltp-pt)*100/ltp) - resources.scanner().crossover_reminder_percent <= 0:
				crossover_point = True
				df['Symbol'].iloc[n-1] = '** {}'.format(df['Symbol'].iloc[n-1])
				df['Remarks'].iloc[n-1]= pt_name
				df['S1-R3'].iloc[n-1] = pt
				break
		if not crossover_point:
			if ltp >= pp:
				df['Remarks'].iloc[n-1]='LTP >= PP'
				df['S1-R3'].iloc[n-1] = pp
				if ltp >= r3:
					df['Remarks'].iloc[n-1]='LTP >= R3'
					df['S1-R3'].iloc[n-1] = r3
				elif ltp >= r2:
					df['Remarks'].iloc[n-1]='LTP >= R2'
					df['S1-R3'].iloc[n-1] = r2
				elif ltp >= r1:
					df['Remarks'].iloc[n-1]='LTP >= R1'
					df['S1-R3'].iloc[n-1] = r1
				elif ltp < r1:
					df['Remarks'].iloc[n-1]='PP <= LTP < R1'
					df['S1-R3'].iloc[n-1] = r1
			else:
				df['Remarks'].iloc[n-1]='LTP < PP'
				df['S1-R3'].iloc[n-1] = pp
				if ltp >= s1:
					df['Remarks'].iloc[n-1]='PP > LTP >= S1'
					df['S1-R3'].iloc[n-1] = s1
				elif ltp >= s2:
					df['Remarks'].iloc[n-1]='LTP >= S2'
					df['S1-R3'].iloc[n-1] = s2
				elif ltp >= s3:
					df['Remarks'].iloc[n-1]='LTP >= S3'
					df['S1-R3'].iloc[n-1] = s3
				elif ltp < s3:
					df['Remarks'].iloc[n-1]='LTP < S3'
					df['S1-R3'].iloc[n-1] = s3
		if current_datetime_in_ist_trading_time_range():
			df['T0BuySellDiff']= np.nan
			df['T0BuySellDiff'].iloc[n-1] = df_today['T0BuySellDiff'].iloc[0]

		df = df.tail(1)
		default_logger().debug(df.to_string(index=False))
		for key in df.keys():
			# Symbol                  Date     VWAP     LTP %Change  TDYVol(%)  7DVol(%)    Remarks  Yst7DVol(%)  Yst%Del Tdy%Del   PPoint    S1-R3
			if not key in VOLUME_KEYS:
				df.drop([key], axis = 1, inplace = True)
		default_logger().debug(df.to_string(index=False))
		if today_vs_yest > 0 or ltp >= vwap or crossover_point:
			signalframescopy.append(df)
		return df, df_today, signalframescopy

	# def buy_solid():
		# OBV trending upwards
		# RSI trending upwards. If not, then if it's closer to lower limit, strong buy
		# MACD trending upwards and +ve. MACD > MACD 12
		# LTP line > EMA9 and LTP > MA50
		# MOM +ve and trending upwards
