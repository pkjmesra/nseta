# -*- coding: utf-8 -*-
import unittest
import logging

from nseta.common.log import default_logger
from nseta.strategy.rsiSignalStrategy import rsiSignalStrategy
from nseta.common import urls
from baseUnitTest import baseUnitTest

class TestRSISignalStrategy(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_update_ledger_debug(self):
		default_logger().setLevel(logging.DEBUG)
		rsi = rsiSignalStrategy(requires_ledger=True)
		for i in [80,81,82,83,84,85,86,87,86,85,84,83,82,81,80]:
			rsi.index(i,i,'2021-01-18')
		report = rsi.report.to_string(index=False)
		self.assertIn('Base-delta',report,report)

	def tearDown(self):
		default_logger().setLevel(logging.INFO)
		super().tearDown()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestRSISignalStrategy)
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
