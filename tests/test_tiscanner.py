# -*- coding: utf-8 -*-
import pdb
import unittest

from nseta.scanner.tiscanner import scanner
from nseta.common import urls

class TestTIScanner(unittest.TestCase):
	def setUp(self):
		pass

	def test_default_indicator(self):
		s = scanner('NA')
		self.assertEqual(s.indicator, 'all')

	def test_scan_intraday_more_than_n(self):
		s = scanner('bbands')
		n = 4
		df, signaldf = s.scan_intraday(['HDFC', 'SBIN','BANDHANBNK', 'PNB'])
		self.assertEqual(len(df), n)

	def test_scan_live_queue_all(self):
		s = scanner('all')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_rsi(self):
		s = scanner('rsi')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_ema(self):
		s = scanner('ema')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		self.assertEqual(len(signaldf), 1)

	def test_scan_live_queue_macd(self):
		s = scanner('macd')
		n = range(15)
		for iteration in n:
			df, signaldf = s.scan_live(['HDFC'])
		self.assertEqual(len(df), 1)
		self.assertEqual(len(signaldf), 1)

	def tearDown(self):
	  urls.session.close()

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
