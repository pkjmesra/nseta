# -*- coding: utf-8 -*-
import unittest
from click.testing import CliRunner
from nseta.cli.historycli import history, pe_history
from baseUnitTest import baseUnitTest

class TestHistorycli(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_history(self):
		runner = CliRunner()
		result = runner.invoke(history, args=['--symbol', 'BANDHANBNK', '--start', '2020-01-01', '--end', '2020-01-08', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("History for symbol:BANDHANBNK", result.output, str(result.output))
		self.assertIn("Saved to: BANDHANBNK.csv", result.output, str(result.output))

	def test_pe_history(self):
		runner = CliRunner()
		result = runner.invoke(pe_history, args=['--symbol', 'BANDHANBNK', '--start', '2020-01-01', '--end', '2020-01-08'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("PE History for symbol:BANDHANBNK", result.output, str(result.output))
		self.assertIn("Saved to: BANDHANBNK.csv", result.output, str(result.output))

	def test_pe_history_130_days(self):
		runner = CliRunner()
		result = runner.invoke(pe_history, args=['--symbol', 'BANDHANBNK', '--start', '2020-06-01', '--end', '2020-12-31'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("PE History for symbol:BANDHANBNK", result.output, str(result.output))
		self.assertIn("Saved to: BANDHANBNK.csv", result.output, str(result.output))

	def test_history_inputs(self):
		runner = CliRunner()
		result = runner.invoke(history, args=['--start', '2020-01-01', '--end', '2020-01-08'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

	def test_history_pickle(self):
		runner = CliRunner()
		result = runner.invoke(history, args=['--symbol', 'BANDHANBNK', '--start', '2020-01-01', '--end', '2020-01-08', '--format', 'pkl'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Saved to: BANDHANBNK.pkl", result.output, str(result.output))

	def test_pe_history_inputs(self):
		runner = CliRunner()
		result = runner.invoke(pe_history, args=['--start', '2020-01-01', '--end', '2020-01-08'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

	def test_pe_history_pickle(self):
		runner = CliRunner()
		result = runner.invoke(pe_history, args=['--symbol', 'BANDHANBNK', '--start', '2020-01-01', '--end', '2020-01-08', '--format', 'pkl'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Saved to: BANDHANBNK.pkl", result.output, str(result.output))

	def tearDown(self):
		super().tearDown()


if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestHistorycli)
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
