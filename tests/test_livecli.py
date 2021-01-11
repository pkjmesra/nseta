# -*- coding: utf-8 -*-
import pdb
import unittest

from click.testing import CliRunner
import time

from nseta.cli.livecli import live_quote, scan, live_quote_background, scan_live_background, scan_intraday_background
from nseta.common import urls
from nseta.scanner.tiscanner import scanner

class TestLivecli(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_live_quote(self):
		runner = CliRunner()
		result = runner.invoke(live_quote, args=['--symbol', 'BANDHANBNK', '-gowvb'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Symbol              |            BANDHANBNK", result.output, str(result.output))
		self.assertIn("Name                |  Bandhan Bank Limited", result.output, str(result.output))
		self.assertIn("ISIN                |          INE545U01014", result.output, str(result.output))
		self.assertIn("Last Updated        |", result.output, str(result.output))
		self.assertIn("Prev Close", result.output, str(result.output))
		self.assertIn("Last Trade Price", result.output, str(result.output))
		self.assertIn("Change", result.output, str(result.output))
		self.assertIn("% Change", result.output, str(result.output))
		self.assertIn("Avg. Price", result.output, str(result.output))
		self.assertIn("Open", result.output, str(result.output))
		self.assertIn("52 Wk High", result.output, str(result.output))
		self.assertIn("Total Traded Volume", result.output, str(result.output))
		self.assertIn("% Delivery", result.output, str(result.output))
		self.assertIn("Bid Quantity        | Bid Price           | Offer_Quantity      | Offer_Price", result.output, str(result.output))

	def test_scan_intraday(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--intraday', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Intraday scanning finished.", result.output, str(result.output))

	def test_scan_intraday_background(self):
		s = scanner('rsi')
		result = scan_intraday_background(s, ['HDFC'], 'emac', terminate_after_iter=2, wait_time=2)
		self.assertEqual(result , 2)

	def test_scan_live(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--live', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Live scanning finished.", result.output, str(result.output))

	def test_scan_live_background(self):
		s = scanner('rsi')
		result = scan_live_background(s, ['HDFC'], 'emac', terminate_after_iter=2, wait_time=2)
		self.assertEqual(result , 2)

	def test_scan_swing(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--swing', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Swing scanning finished.", result.output, str(result.output))

	def test_live_quote_inputs(self):
		runner = CliRunner()
		result = runner.invoke(live_quote, args=['-gowvb'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

	def test_scan_live_quote_background(self):
		result = live_quote_background('HDFC', True, True, True, True, True, terminate_after_iter=2, wait_time=2)
		self.assertEqual(result , 2)

	def test_scan_inputs(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--swing', '--intraday', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Choose only one of --live, --intraday or --swing options.", result.output, str(result.output))
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Choose at least one of the --live, --intraday (recommended) or --swing options.", result.output, str(result.output))
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

	def tearDown(self):
		urls.session.close()
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))


if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestLivecli)
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
