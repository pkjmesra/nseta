# -*- coding: utf-8 -*-
import unittest
import matplotlib.pyplot as plt
from unittest.mock import patch

from click.testing import CliRunner

from nseta.cli.plotscli import plot_ta
import nseta.common.urls as urls
from baseUnitTest import baseUnitTest

class TestStrategycli(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_plot_ta_inputs(self):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--start', '2020-08-01', '--end', '2021-01-01'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Please provide security/index code", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_all(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'ALL'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): ALL, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_no_option(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): ALL, plotted.", result.output, str(result.output))
	
	@patch('matplotlib.pyplot.show')
	def test_plot_ta_price(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'PRICE'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): PRICE, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_rsi(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'RSI'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): RSI, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_ema(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'EMA'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): EMA, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_sma(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'SMA'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): SMA, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_ssto(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'SSTO', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): SSTO, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_fsto(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'FSTO'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): FSTO, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_adx(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'ADX'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): ADX, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_macd(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'MACD'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): MACD, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_mom(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'MOM'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): MOM, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_dmi(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'DMI'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): DMI, plotted.", result.output, str(result.output))

	@patch('matplotlib.pyplot.show')
	def test_plot_ta_bbands(self, mock_pyplot):
		runner = CliRunner()
		result = runner.invoke(plot_ta, args=['--symbol', 'BANDHANBNK', '--start', '2020-11-01', '--end', '2021-01-01', '--plot-type', 'BBANDS'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Technical indicator(s): BBANDS, plotted.", result.output, str(result.output))

	def tearDown(self):
		super().tearDown()

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
