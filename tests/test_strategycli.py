# -*- coding: utf-8 -*-
import pdb
import unittest
import matplotlib.pyplot as plt
from unittest.mock import patch
import time

from click.testing import CliRunner

from nseta.cli.strategycli import test_trading_strategy, forecast_strategy
from nseta.common import urls

class TestStrategycli(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_test_trading_strategy_inputs(self):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--start', '2020-08-01', '--end', '2021-01-01'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Please provide security/index code", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_bbands(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'bbands', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_rsi(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'rsi', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_rsi_autosearch(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'rsi', '--autosearch'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_macd(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'macd', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_macd_autosearch(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'macd', '--autosearch'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_smac(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'smac', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	# TODO: Takes 121 seconds to run
	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_smac_autosearch(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'smac', '--autosearch'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_emac(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'emac', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	# TODO: Takes 118 seconds to run
	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_emac_autosearch(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'emac', '--autosearch'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_multi(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'multi', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_multi_autosearch(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'multi', '--autosearch'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_custom(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'custom', '-l', '1.5', '-u', '1.5', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_historical_bbands_autosearch(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'bbands','--autosearch'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_intraday(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'PNB', '--strategy', 'bbands', '--clear', '--intraday'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_intraday_autosearch(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'PNB', '--strategy', 'bbands', '--intraday', '--autosearch'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_test_trading_strategy_intraday_signals(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--symbol', 'PNB', '--strategy', 'rsi', '--clear', '--intraday'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Portfolio_Value", result.output, str(result.output))
	
	def test_forecast_strategy_inputs(self):
		runner = CliRunner()
		result = runner.invoke(test_trading_strategy, args=['--start', '2020-08-01', '--end', '2021-01-01'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Please provide security/index code", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_forecast_strategy_bbands(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(forecast_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'bbands', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_forecast_strategy_rsi(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(forecast_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'rsi', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_forecast_strategy_smac(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(forecast_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'smac', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_forecast_strategy_emac(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(forecast_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'emac', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_forecast_strategy_multi(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(forecast_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'multi', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_forecast_strategy_custom(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(forecast_strategy, args=['--symbol', 'BANDHANBNK', '--start', '2020-08-01', '--end', '2021-01-01', '--strategy', 'custom', '-l', '1.5', '-u', '1.5', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("pnl", result.output, str(result.output))

	def tearDown(self):
		urls.session.close()
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

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
