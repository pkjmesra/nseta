# -*- coding: utf-8 -*-
import pdb
import unittest
import pandas as pd
import os
import time

from datetime import datetime
from nseta.common.tradingtime import *

class TestTradingTime(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_ist_time(self):
		t = IST_time()
		self.assertTrue(datetime.now(), t)

	def test_ist_date(self):
		t = IST_date()
		self.assertTrue(datetime.now(), t)

	def test_is_trading_day(self):
		t = IST_datetime()
		self.assertEqual(t.weekday() <= 4, is_trading_day())

	def test_is_datetime_between(self):
		t = IST_datetime()
		b = datetime(t.year, t.month, t.day, 23, 58).time()
		e = datetime(t.year, t.month, t.day, 0, 5).time()
		c = datetime(t.year, t.month, t.day, 0, 3).time()
		self.assertTrue(is_datetime_between(b, e, c))

	def tearDown(self):
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestTradingTime)
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
