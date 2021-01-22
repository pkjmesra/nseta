# -*- coding: utf-8 -*-
import pdb
import unittest
import io
import sys
import time

import logging
from nseta.common import log
from nseta.common.log import *


class TestLog(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()
		capturedOutput = io.StringIO()                  # Create StringIO object
		sys.stdout = capturedOutput                     #  and redirect stdout.
		self.stream_handler = logging.StreamHandler(sys.stdout)
		default_logger().addHandler(self.stream_handler)
		self.capturedOutput = capturedOutput

	def test_debug_log(self):
		log.setup_custom_logger('nseta', logging.DEBUG, False, filter=None)
		default_logger().debug('test_debug_log')
		sys.stdout.flush()
		self.assertIn('test_debug_log', self.capturedOutput.getvalue())

	def test_debug_log_filter(self):
		log.setup_custom_logger('nseta', logging.DEBUG, False, filter='test_log.py')
		default_logger().debug('test_debug_log_filter')
		self.assertIn('test_debug_log_filter', self.capturedOutput.getvalue())
		self.assertIn('test_log.py', self.capturedOutput.getvalue())
	
	def test_debug_log_filter_info(self):
		log.setup_custom_logger('nseta', logging.INFO, False, filter='test_debug_log_filter_info')
		default_logger().info('test_debug_log_filter_info')
		self.assertIn('test_debug_log_filter_info', self.capturedOutput.getvalue())
		
	def test_debug_log_filter_warn(self):
		log.setup_custom_logger('nseta', logging.WARN, False, filter='test_debug_log_filter_warn')
		default_logger().warn('test_debug_log_filter_warn')
		self.assertIn('test_debug_log_filter_warn', self.capturedOutput.getvalue())
		
	def test_debug_log_filter_error(self):
		log.setup_custom_logger('nseta', logging.ERROR, False, filter='test_debug_log_filter_error')
		default_logger().error('test_debug_log_filter_error')
		self.assertIn('test_debug_log_filter_error', self.capturedOutput.getvalue())
		
	def test_debug_log_filter_critical(self):
		log.setup_custom_logger('nseta', logging.CRITICAL, False, filter='test_debug_log_filter_critical')
		default_logger().critical('test_debug_log_filter_critical')
		self.assertIn('test_debug_log_filter_critical', self.capturedOutput.getvalue())

	def tearDown(self):
		default_logger().removeHandler(self.stream_handler)
		sys.stdout = sys.__stdout__                     # Reset redirect.
		log.setup_custom_logger('nseta', logging.INFO, False, filter=None)
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestLog)
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
