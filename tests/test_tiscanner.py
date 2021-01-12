# -*- coding: utf-8 -*-
import pdb
import unittest
import time
import pandas as pd

from nseta.scanner.tiscanner import scanner
from nseta.common import urls

class TestTIScanner(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_default_indicator(self):
		s = scanner('NA')
		self.assertEqual(s.indicator, 'all')

	def test_empty_dataframe(self):
		s = scanner('emac')
		df, signaldf = s.scan_intraday(['SOMESYMBOL'])
		self.assertEqual(df, None)
		self.assertEqual(signaldf, None)

	def test_scan_intraday_more_than_n(self):
		s = scanner('bbands')
		n = 4
		df, signaldf = s.scan_intraday(['HDFC', 'SBIN','BANDHANBNK', 'PNB'])
		self.assertEqual(len(df), n)

	# TODO: Takes 126 seconds to run
	def test_scan_live_queue_all(self):
		s = scanner('all')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_rsi(self):
		s = scanner('rsi')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_ema(self):
		s = scanner('emac')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_macd(self):
		s = scanner('macd')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		# self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_bbands(self):
		s = scanner('bbands')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)

	def test_scan_live_confidence_level_buy_route(self):
		s = scanner('all')
		df = pd.DataFrame({'RSI': [70], 'MOM': [4], 'macd(12)':[3] , 'macdsignal(9)':[2.5], 'LTP': [100], 'BBands-L': [101],'BBands-U': [105], 'EMA(9)': [99], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], ' >> 90 %  <<')

	def test_scan_live_confidence_level_buy_alternate_route(self):
		s = scanner('rsi')
		df = pd.DataFrame({'RSI': [55], 'MOM': [4], 'macd(12)':[-1] , 'macdsignal(9)':[-2], 'LTP': [100.1], 'BBands-L': [100], 'BBands-U': [105],'EMA(9)': [105], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], '50 %')

	def test_scan_live_confidence_level_buy_alternate_route_emac(self):
		s = scanner('emac')
		df = pd.DataFrame({'RSI': [55], 'MOM': [4], 'macd(12)':[-1] , 'macdsignal(9)':[-2], 'macdsignal(9)':[-2], 'LTP': [100.1], 'BBands-L': [100], 'BBands-U': [105],'EMA(9)': [105], 'Signal': ['BUY'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], '50 %')

	def test_scan_live_confidence_level_sell_route(self):
		s = scanner('all')
		df = pd.DataFrame({'RSI': [35], 'MOM': [-1], 'macd(12)':[-2] , 'macdsignal(9)':[-1], 'LTP': [105], 'BBands-L': [101],'BBands-U': [100], 'EMA(9)': [106], 'Signal': ['SELL'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], ' >> 90 %  <<')

	def test_scan_live_confidence_level_sell_alternate_route(self):
		s = scanner('rsi')
		df = pd.DataFrame({'RSI': [35], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [105], 'BBands-L': [101],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], '50 %')

	def test_scan_live_confidence_level_sell_alternate_route_emac(self):
		s = scanner('emac')
		df = pd.DataFrame({'RSI': [35], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [105], 'BBands-L': [101],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Confidence': ['NA']})
		df = s.update_confidence_level(df)
		self.assertEqual(df['Confidence'].iloc[0], '60 %')
	
	def test_update_signal_indicator(self):
		s = scanner('bbands')
		df = pd.DataFrame({'RSI': [35], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'bbands', 'BBands-L', 0.05, 101, '<=', 'BUY', '[LTP < BBands-L]', 'BUY', '[LTP ~ BBands-L]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'BUY')
		self.assertEqual(df['Remarks'].iloc[0], '[LTP < BBands-L]')

	def test_update_signal_indicator_alternate(self):
		s = scanner('bbands')
		df = pd.DataFrame({'RSI': [35], 'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101.04], 'BBands-L': [101],'BBands-U': [105.1], 'EMA(9)': [104], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signal_indicator(df, [], 'bbands', 'BBands-L', 0.05, 101.04, '<=', 'BUY', '[LTP < BBands-L]', 'BUY', '[LTP ~ BBands-L]')
		df = pd.concat(signalframes)
		self.assertEqual(df['Signal'].iloc[0], 'BUY')
		self.assertEqual(df['Remarks'].iloc[0], '[LTP ~ BBands-L]')

	def test_update_signals_sanity(self):
		s = scanner('bbands')
		df = pd.DataFrame({'MOM': [-1], 'macd(12)':[1] , 'macdsignal(9)':[2], 'LTP': [101], 'BBands-L': [101.04],'BBands-U': [105.1], 'Signal': ['SELL'], 'Remarks': ['NA'], 'Confidence': ['NA']})
		signalframes = s.update_signals([], None)
		self.assertEqual(signalframes, [])
		signalframes = s.update_signals([], pd.DataFrame(columns=['RSI']))
		self.assertEqual(signalframes, [])
		signalframes = s.update_signals([], df)
		self.assertEqual(signalframes, [])

	def tearDown(self):
		urls.session.close()
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestTIScanner)
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
