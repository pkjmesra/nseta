# -*- coding: utf-8 -*-
import pdb
import unittest
import matplotlib.pyplot as plt
from unittest.mock import patch

from click.testing import CliRunner

from nseta.cli.strategycli import test_trading_strategy, forecast_strategy
from nseta.common import urls

class TestStrategycli(unittest.TestCase):
	def setUp(self):
		pass

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'bbands', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Final Portfolio Value", result.output, str(result.output))
		self.assertIn("Optimal parameters", result.output, str(result.output))
		self.assertIn("Final PnL", result.output, str(result.output))
	
	@patch('matplotlib.pyplot.show')
	def test_forecast_strategy(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(forecast_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--strategy', 'bbands', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("final_value", result.output, str(result.output))

	def tearDown(self):
	  urls.session.close()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestStrategycli)
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
