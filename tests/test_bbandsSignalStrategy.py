# -*- coding: utf-8 -*-
import pdb
import unittest
import time
import logging

from nseta.common.log import default_logger
from nseta.strategy.bbandsSignalStrategy import bbandsSignalStrategy
from nseta.common import urls

class TestBbandsSignalStrategy(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_update_ledger_debug(self):
		default_logger().setLevel(logging.DEBUG)
		bbands = bbandsSignalStrategy(requires_ledger=True)
		bbands.index(100,100,100,'2021-01-18')
		report = bbands.report.to_string(index=False)
		self.assertIn('BBands-U',report,report)
		self.assertIn('BBands-L',report,report)

	def tearDown(self):
		urls.session.close()
		default_logger().setLevel(logging.INFO)
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestBbandsSignalStrategy)
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
