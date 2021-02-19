# -*- coding: utf-8 -*-
import unittest
import pandas as pd

from nseta.scanner.stockscanner import *
from nseta.scanner.volumeStockScanner import volumeStockScanner
from nseta.common import urls
from baseUnitTest import baseUnitTest

class Teststockscanner(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_default_indicator(self):
		s = scanner('NA')
		self.assertEqual(s.indicator, 'all')

	def test_empty_dataframe(self):
		s = scanner('emac')
		df, signaldf = s.scan(['SOMESYMBOL'], scanner_type=ScannerType.Intraday)
		self.assertEqual(df, None)
		self.assertEqual(signaldf, None)

	def test_scan_intraday_more_than_n(self):
		s = scanner('bbands')
		s.periodicity = "1"
		n = 4
		df, signaldf = s.scan(['HDFC', 'SBIN','BANDHANBNK', 'PNB'], scanner_type=ScannerType.Intraday)
		self.assertEqual(len(df), n)

	def test_scan_swing(self):
		s = scanner()
		n = 1
		df, signaldf = s.scan(['HDFC'], scanner_type=ScannerType.Swing)
		self.assertEqual(len(df), n)

	def test_scan_volume(self):
		s = scanner()
		n = 1
		df, signaldf = s.scan(['HDFC'], scanner_type=ScannerType.Volume)
		self.assertEqual(len(df), n)

	# TODO: Takes 126 seconds to run
	def test_scan_live_queue_all(self):
		s = scanner('all')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan(['HDFC'], scanner_type=ScannerType.Live)
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_rsi(self):
		s = scanner('rsi')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan(['HDFC'], scanner_type=ScannerType.Live)
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_ema(self):
		s = scanner('emac')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan(['HDFC'], scanner_type=ScannerType.Live)
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_macd(self):
		s = scanner('macd')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan(['HDFC'], scanner_type=ScannerType.Live)
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_bbands(self):
		s = scanner('bbands')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan(['HDFC'], scanner_type=ScannerType.Live)
		self.assertEqual(len(df), 1)

	def test_scan_live_confidence_level_buy_route(self):
		s = scanner('all')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [70], 'MOM': [4], 'macd(12)':[3] , 'macdsignal(9)':[2.5], 'LTP': [100], 'BBands-L': [101],'BBands-U': [105], 'EMA(9)': [99], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 90)

	def test_scan_live_confidence_level_buy_alternate_route(self):
		s = scanner('rsi')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [55], 'MOM': [4], 'macd(12)':[-1] , 'macdsignal(9)':[-2], 'LTP': [100.1], 'BBands-L': [100], 'BBands-U': [105],'EMA(9)': [105], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 50)

	def test_scan_live_confidence_level_buy_alternate_route_smac(self):
		s = scanner('smac')
		df = pd.DataFrame({'RSI': [55], 'MOM': [4], 'macd(12)':[-1] , 'macdsignal(9)':[-2], 'LTP': [102], 'BBands-L': [100], 'BBands-U': [105],'EMA(9)': [105], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 30)

	def test_scan_live_confidence_level_buy_alternate_route_bbands(self):
		s = scanner('bbands')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [55], 'MOM': [4], 'macd(12)':[-1] , 'macdsignal(9)':[-2], 'LTP': [100.1], 'BBands-L': [100], 'BBands-U': [105],'EMA(9)': [105], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 40)

	def test_scan_live_confidence_level_buy_alternate_route_all(self):
		s = scanner('all')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [55], 'MOM': [4], 'macd(12)':[-1] , 'macdsignal(9)':[-2], 'LTP': [100.1], 'BBands-L': [100], 'BBands-U': [105],'EMA(9)': [105], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 40)

	def test_scan_live_confidence_level_buy_alternate_route_emac(self):
		s = scanner('emac')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [55], 'MOM': [4], 'macd(12)':[-1] , 'macdsignal(9)':[-2], 'macdsignal(9)':[-2], 'LTP': [100.1], 'BBands-L': [100], 'BBands-U': [105],'EMA(9)': [105], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 50)

	def test_scan_live_confidence_level_sell_route(self):
		s = scanner('all')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [35], 'MOM': [-1], 'macd(12)':[-2] , 'macdsignal(9)':[-1], 'LTP': [105], 'BBands-L': [101],'BBands-U': [100], 'EMA(9)': [106], 'Signal': ['SELL'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 90)

	def test_scan_live_confidence_level_sell_alternate_route(self):
		s = scanner('rsi')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [55], 'MOM': [2], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [105], 'BBands-L': [101],'BBands-U': [105.4], 'EMA(9)': [104], 'Signal': ['SELL'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 30)

	def test_scan_live_confidence_level_sell_alternate_route_emac(self):
		s = scanner('emac')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [55], 'MOM': [-1], 'macd(12)':[-2] , 'macdsignal(9)':[-3], 'LTP': [105], 'BBands-L': [101],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 30)

	def test_scan_live_confidence_level_none(self):
		s = scanner('emac')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [55], 'MOM': [-1], 'macd(12)':[-2] , 'macdsignal(9)':[-3], 'LTP': [105], 'BBands-L': [101],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['Misc'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], 0)
	
	def test_update_signal_indicator_bbands(self):
		s = scanner('bbands')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [35], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.1],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'bbands', 'BBands-L', 0.05, 101, '<=', 'BUY', '[LTP < BBands-L]', 'BUY', '[LTP ~ BBands-L]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'BUY')
		self.assertEqual(df['Remarks'].iloc[0], '[LTP < BBands-L]')

	def test_update_signal_indicator_bbands_alternate(self):
		s = scanner('bbands')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [35], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101.04], 'BBands-L': [101],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'bbands', 'BBands-L', 0.05, 101.1, '<=', 'BUY', '[LTP < BBands-L]', 'BUY', '[LTP ~ BBands-L]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'BUY')
		self.assertEqual(df['Remarks'].iloc[0], '[LTP ~ BBands-L]')

	def test_update_signal_indicator_rsi_true_value(self):
		s = scanner('rsi')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [85], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'rsi', 'RSI', 25, 75, '><', 'SELL', '[RSI >= 75]', 'BUY', '[RSI <= 25]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'SELL')
		self.assertEqual(df['Remarks'].iloc[0], '[RSI >= 75]')

	def test_update_signal_indicator_rsi_with_signalframes(self):
		s = scanner('rsi')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [20], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['BUY'], 'Remarks': ['BUY'], 'Confidence': [80]})
		signalframes = s.update_signal_indicator(df, [df], 'rsi', 'RSI', 25, 75, '><', 'SELL', '[RSI >= 75]', 'BUY', '[RSI <= 25]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'BUY,BUY')
		self.assertEqual(df['Confidence'].iloc[0], 80)

	def test_update_signal_indicator_rsi_true_value(self):
		s = scanner('rsi')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [85], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'rsi', 'RSI', 25, 75, '><', 'SELL', '[RSI >= 75]', 'BUY', '[RSI <= 25]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'SELL')
		self.assertEqual(df['Remarks'].iloc[0], '[RSI >= 75]')

	def test_update_signal_indicator_emac_true_value(self):
		s = scanner('emac')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [85], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'emac', 'EMA(9)', 0.1, 104.2, '>=', 'BUY', '[LTP > EMA(9)]', 'SELL', '[LTP < EMA(9)]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'BUY')
		self.assertEqual(df['Remarks'].iloc[0], '[LTP > EMA(9)]')

	def test_update_signal_indicator_emac_false_value(self):
		s = scanner('emac')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [85], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'EMA(9)': [104.2], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'emac', 'EMA(9)', 0.1, 104, '>=', 'BUY', '[LTP > EMA(9)]', 'SELL', '[LTP < EMA(9)]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'SELL')
		self.assertEqual(df['Remarks'].iloc[0], '[LTP < EMA(9)]')

	def test_update_signal_indicator_no_label_comparator_value(self):
		s = scanner('emac')
		df = pd.DataFrame({'Symbol':['Symbol'], 'RSI': [85], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'EMA(9)': [104.2], 'Signal': ['NA'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'emac', 'EMA(9)', 0.1, 104, '==', 'BUY', '[LTP > EMA(9)]', 'SELL', '[LTP < EMA(9)]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'NA')
		self.assertEqual(df['Remarks'].iloc[0], 'NA')

	def test_update_signals_sanity(self):
		s = scanner('bbands')
		df = pd.DataFrame({'Symbol':['Symbol'], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes, df_ret = s.update_signals([], None)
		self.assertEqual(signalframes, [])
		signalframes, df_ret = s.update_signals([], pd.DataFrame(columns=['RSI']))
		self.assertEqual(signalframes, [])
		signalframes, df_ret = s.update_signals([], df)
		self.assertEqual(signalframes, [])

	def test_format_scan_volume_df_ltp_R3_crossover(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25],'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['107'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today, [])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['R3'].iloc[0])

	def test_format_scan_volume_df_ltp_R3(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['140'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today, [])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['R3'].iloc[0])

	def test_format_scan_volume_df_ltp_R2_crossover(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['106'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['R2'].iloc[0])

	def test_format_scan_volume_df_ltp_R2(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [140,140]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['120'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['R2'].iloc[0])

	def test_format_scan_volume_df_ltp_R1_crossover(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['105'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['R1'].iloc[0])

	def test_format_scan_volume_df_ltp_R1(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [130,130],'R3': [140,140]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['120'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['R1'].iloc[0])

	def test_format_scan_volume_df_ltp_PP_R1(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['104.5'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['R1'].iloc[0])
		self.assertEqual(df_result['Remarks'].iloc[0], 'PP <= LTP < R1')

	def test_format_scan_volume_df_ltp_S1(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['103.5'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['S1'].iloc[0])

	def test_format_scan_volume_df_ltp_S2(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['102.5'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['S2'].iloc[0])

	def test_format_scan_volume_df_ltp_S3(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-16'], 'pChange': [.25], 'FreeFloat':[20000000],'T0BuySellDiff': [2000.00], 'LTP':['101.5'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['S3'].iloc[0])

	def test_format_scan_volume_df_ltp_PP_S3(self):
		s = volumeStockScanner()
		df = pd.DataFrame({'Symbol':['Symbol','AnotherSymbol'], 'Date': ['2021-01-15','2021-01-16'], 'Volume':[7777,7777] , '%Deliverable':[0.28,0.28], 'PP': [104,104], 'VWAP': [101.04,101.04],'S1': [103,103], 'S2': [102,102],'S3': [101,101],'R1': [105,105],'R2': [106,106],'R3': [107,107]})
		df_today = pd.DataFrame({'TotalTradedVolume': ['8888'], 'Updated': ['2021-01-15'], 'pChange': [.25], 'FreeFloat':[5000000],'T0BuySellDiff': [2000.00], 'LTP':['100'] , 'Tdy%Del':[0.28]})
		df_result, df_today_result, signalframes = s.format_scan_volume_df(df, df_today,[])
		self.assertEqual(df_result['S1-R3'].iloc[0], df['S3'].iloc[0])
		self.assertEqual(df_result['Remarks'].iloc[0], 'LTP < S3')

	def tearDown(self):
		super().tearDown()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(Teststockscanner)
	result = unittest.TextTestRunner(verbosity=2).run(suite)
	if six.PY2:
		if result.wasSuccessful():
			print("tests OK")
		for (test, error) in result.errors:
			print("=========Error in: %s===========" % test)
			print(error)
			print("======================================")

		for (test, failures) in result.failures:
			print("=========Error in: %s===========" % test)
			print(failures)
			print("======================================")
