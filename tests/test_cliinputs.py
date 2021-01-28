# -*- coding: utf-8 -*-
import unittest
import io
import sys

from nseta.cli.inputs import *
from nseta.cli.livecli import live_quote
from baseUnitTest import baseUnitTest

class TestCliInputs(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_validate_inputs(self):
		result = validate_inputs('2020-01-01', '2021-01-08', 'SOMESYMBOL', strategy='rsi')
		self.assertTrue(result)

	def test_date_diff_strategy(self):
		result = validate_inputs('2020-12-25', '2021-01-07', 'SOMESYMBOL', strategy='rsi')
		self.assertFalse(result)
		self.assertIn('Please provide start and end date with a time delta of at least 20 days for the selected strategy.', self.capturedOutput.getvalue())

	def test_date_input_format(self):
		# with self.assertRaises(ValueError):
		result = validate_inputs('15-12-2020', '20-01-2020', 'SOMESYMBOL', strategy='rsi')
		self.assertFalse(result)
		self.assertIn('Please provide start and end date in format yyyy-mm-dd', self.capturedOutput.getvalue())

	def test_print_help_msg(self):
		print_help_msg(live_quote)
		self.assertIn('Usage:  [OPTIONS]', self.capturedOutput.getvalue())

	def test_validate_symbol(self):
		result = validate_symbol('SOMESYMBOL')
		self.assertTrue(result)
		result = validate_symbol(None)
		self.assertFalse(result)
		self.assertIn('Please provide security/index code', self.capturedOutput.getvalue())

	def tearDown(self):
		super().tearDown()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestCliInputs)
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
