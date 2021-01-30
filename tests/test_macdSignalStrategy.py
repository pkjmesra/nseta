# -*- coding: utf-8 -*-
import unittest
import time
import logging

from nseta.common.log import default_logger
from nseta.strategy.macdSignalStrategy import macdSignalStrategy
from nseta.common import urls
from baseUnitTest import baseUnitTest

class TestMACDSignalStrategy(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_update_ledger_debug(self):
		default_logger().setLevel(logging.DEBUG)
		macd = macdSignalStrategy(requires_ledger=True)
		macd.macd9 = 99
		macd.index(100,100,'2021-01-18')
		macd.index(101,100,'2021-01-18')
		macd.index(102,100,'2021-01-18')
		macd.index(103,100,'2021-01-18')
		macd.index(102,100,'2021-01-18')
		macd.macd9 = 102
		macd.index(101,100,'2021-01-18')
		macd.index(100,100,'2021-01-18')
		report = macd.report.to_string(index=False)
		self.assertTrue(len(report) > 0)

	def tearDown(self):
		super().tearDown()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestMACDSignalStrategy)
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
