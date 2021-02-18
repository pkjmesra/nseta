import pandas as pd
import numpy as np
import datetime
import sys

from bs4 import BeautifulSoup
from nseta.common.commons import ParseNews
from nseta.common.history import historicaldata
from nseta.live.live import get_live_quote
from nseta.common.ti import ti
from nseta.common.urls import TICKERTAPE_NEWS_URL
from nseta.resources.resources import *
from nseta.scanner.baseStockScanner import baseStockScanner
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger
from nseta.common.tradingtime import *

__all__ = ['volumeStockScanner']

VOLUME_KEYS = ['TDYVol','FreeFloat','ATR','NATR','TRANGE','Volatility','ATRE-F','ATRE-S','ATRE','Avg7DVol','Remarks','PPoint', 'S1-R3','Symbol', 'Date', 'LTP', 'VWAP', 'Yst%Del', '7DayAvgVolume', 'Yst7DVol(%)', 'TodaysVolume','TDYVol(%)', '7DVol(%)', 'Tdy%Del', 'T0BuySellDiff', '%Change']

class volumeStockScanner(baseStockScanner):
	def __init__(self, indicator='all'):
		super().__init__(indicator=indicator)
		self._keys = ['symbol','previousClose', 'lastPrice', 'deliveryToTradedQuantity', 'BuySellDiffQty', 'totalTradedVolume', 'pChange', 'FreeFloat']

	@property
	def keys(self):
		return self._keys

	@tracelog
	def scan_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		signaldf = None
		tiinstance = ti()
		historyinstance = historicaldata()
		# Time frame you want to pull data from
		start_date = datetime.datetime.now()-datetime.timedelta(days=self.last_x_days_timedelta())
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
					df = tiinstance.update_ti(df, rsi=True, mom=True, bbands=True, obv=True, macd=True, ema=True, atr=True, pivots=True, trange=True, atre=True, volatility=True, natr=True)
					default_logger().debug(df.to_string(index=False))
					df = df.tail(7)
					primary = arch.restore('{}_live_quote'.format(symbol), ResponseType.Volume)
					if primary is None or len(primary) == 0:
						result, primary = get_live_quote(symbol, keys = self.keys)
					else:
						df_today = primary
					if (primary is not None and len(primary) > 0):
						if df_today is None:
							df_today = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP', 'Tdy%Del', 'T0BuySellDiff', 'TotalTradedVolume','pChange', 'FreeFloat'], index = [''])
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

		df['FreeFloat'] = np.nan
		df['LTP']=np.nan
		df['%Change'] = np.nan
		df['TDYVol(%)']= np.nan
		df['TDYVol']= np.nan
		df['7DVol(%)'] = np.nan
		df['Remarks']='NA'
		df['Yst7DVol(%)']= np.nan
		df['Avg7DVol'] = np.nan
		df['Yst%Del'] = df['%Deliverable'].apply(lambda x: round(x*100, 1))
		df['Tdy%Del']= np.nan
		df['PPoint']= df['PP']
		df['S1-R3']= np.nan
		

		volume_yest = df['Volume'].iloc[0]
		vwap = df['VWAP'].iloc[n-1]
		df['VWAP'].iloc[n-1] = '₹ {}'.format(vwap)
		ltp = str(df_today['LTP'].iloc[0]).replace(',','')
		ltp = float(ltp)
		today_volume = float(str(df_today['TotalTradedVolume'].iloc[0]).replace(',',''))
		today_vs_yest = round(100* (today_volume - volume_yest)/volume_yest, 1)
		df['Date'].iloc[n-1] = df_today['Updated'].iloc[0]
		df['%Change'].iloc[n-1] = '{} %'.format(df_today['pChange'].iloc[0])
		freeFloat = df_today['FreeFloat'].iloc[0]
		df['FreeFloat'].iloc[n-1] = freeFloat
		df['Avg7DVol'].iloc[n-1] = avg_volume
		df['TDYVol(%)'].iloc[n-1] = today_vs_yest
		df['7DVol(%)'].iloc[n-1] = round(100* (today_volume - avg_volume)/avg_volume, 1)
		df['LTP'].iloc[n-1] = '₹ {}'.format(ltp)
		df['Yst7DVol(%)'].iloc[n-1] = round((100 * (volume_yest - avg_volume)/avg_volume), 1)
		df['Tdy%Del'].iloc[n-1] = df_today['Tdy%Del'].iloc[0]
		df['Yst%Del'].iloc[n-1] = df['Yst%Del'].iloc[0]
		df['TDYVol']= today_volume
		r3 = df['R3'].iloc[n-1]
		r2 = df['R2'].iloc[n-1]
		r1 = df['R1'].iloc[n-1]
		pp = df['PP'].iloc[n-1]
		s1 = df['S1'].iloc[n-1]
		s2 = df['S2'].iloc[n-1]
		s3 = df['S3'].iloc[n-1]
		crossover_point = False
		symbol = df['Symbol'].iloc[n-1]
		for pt, pt_name in zip([r3,r2,r1,pp,s1,s2,s3], ['R3', 'R2', 'R1', 'PP', 'S1', 'S2', 'S3']):
			# Stocks that are within 0.075% of crossover points
			if abs((ltp-pt)*100/ltp) - resources.scanner().crossover_reminder_percent <= 0:
				crossover_point = True
				df['Remarks'].iloc[n-1]= '** {}'.format(pt_name)
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
				else:
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
				else:
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
			resp = TICKERTAPE_NEWS_URL(symbol.upper())
			bs = BeautifulSoup(resp.text, 'lxml')
			news = ParseNews(soup=bs)
			df['News'] = news.parse_news().ljust(38)
			signalframescopy.append(df)
		return df, df_today, signalframescopy
