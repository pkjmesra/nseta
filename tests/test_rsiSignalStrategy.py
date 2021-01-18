# -*- coding: utf-8 -*-
import pdb
import unittest
import time
import logging

from nseta.common.log import default_logger
from nseta.strategy.rsiSignalStrategy import rsiSignalStrategy
from nseta.common import urls

class TestRSISignalStrategy(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_update_ledger_debug(self):
		default_logger().setLevel(logging.DEBUG)
		rsi = rsiSignalStrategy()
		for i in [80,81,82,83,84,85,86,87,86,85,84,83,82,81,80]:
			rsi.index(i,i,'2021-01-18')
		report = rsi.report.to_string(index=False)
		self.assertIn('Base-delta',report,report)

	def tearDown(self):
		urls.session.close()
		default_logger().setLevel(logging.INFO)
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

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
