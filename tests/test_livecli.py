# -*- coding: utf-8 -*-
import unittest
import time
import threading
import logging

from click.testing import CliRunner

from nseta.cli.livecli import live_quote, scan
from nseta.common import urls
from nseta.scanner.stockscanner import *
from baseUnitTest import baseUnitTest
from nseta.scanner.scannerFactory import *
from nseta.common.log import default_logger

class TestLivecli(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

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
		s = scannerFactory.scanner(ScannerType.Intraday, ['HDFC'], 'emac', True)
		scannerinstance = scanner(indicator='rsi')
		result = s.scan_background(scannerinstance, terminate_after_iter=2, wait_time=2)
		self.assertEqual(result , 2)

	def test_scan_live(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--live', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Live scanning finished.", result.output, str(result.output))

	def test_scan_live_background(self):
		s = scannerFactory.scanner(ScannerType.Live, ['HDFC'], 'emac', True)
		scannerinstance = scanner(indicator='rsi')
		result = s.scan_background(scannerinstance, terminate_after_iter=2, wait_time=2)
		self.assertEqual(result , 2)

	def test_scan_swing(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--swing', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Swing scanning finished.", result.output, str(result.output))

	def test_scan_swing_background(self):
		s = scannerFactory.scanner(ScannerType.Swing, ['HDFC'], 'emac', True)
		scannerinstance = scanner(indicator='rsi')
		result = s.scan_background(scannerinstance, terminate_after_iter=2, wait_time=0)
		self.assertEqual(result , 0)
		self.assertFalse(s.background)

	def test_scan_volume(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK', '--volume', '--clear', '--orderby', '7DVol(%)'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Volume scanning finished.", result.output, str(result.output))

	def test_scan_volume_intraday(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK', '--volume', '--clear', '--orderby', 'TDYVol(%)'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Volume scanning finished.", result.output, str(result.output))
	
	def test_scan_volume_background(self):
		s = scannerFactory.scanner(ScannerType.Volume, ['HDFC'], 'emac', True)
		scannerinstance = scanner(indicator='rsi')
		result = s.scan_background(scannerinstance, terminate_after_iter=2, wait_time=2)
		self.assertEqual(result , 2)

	def test_live_quote_inputs(self):
		runner = CliRunner()
		result = runner.invoke(live_quote, args=['-gowvb'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

	def test_scan_live_quote_background(self):
		scanner = scannerFactory.scanner(ScannerType.Quote)
		result = scanner.live_quote_background('HDFC', True, True, True, True, True, terminate_after_iter=2, wait_time=2)
		self.assertEqual(result , 2)

	def test_scan_inputs(self):
		runner = CliRunner()
		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--swing', '--intraday', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Choose only one of --live, --intraday, --swing or --volume options.", result.output, str(result.output))
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

		result = runner.invoke(scan, args=['--stocks', 'BANDHANBNK,HDFC', '--indicator', 'all', '--clear'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Choose at least one of the --live, --intraday (recommended) , --volume or --swing options.", result.output, str(result.output))
		self.assertIn("Usage:  [OPTIONS]", result.output, str(result.output))

	def test_scan_base_background(self):
		scanner_type= ScannerType.Intraday
		s = scannerFactory.scanner(scanner_type, ['HDFC'], 'rsi', True)
		b = threading.Thread(name='scan_test_background', 
					target=s.scan, args=['Symbol'], daemon=True)
		b.start()
		time.sleep(0.5)
		s.scan_background_interrupt()
		b.join()
		self.assertIn("This run of {} scan took".format(scanner_type.name), self.capturedOutput.getvalue())
		self.assertIn("Finished all iterations of scanning {}".format(scanner_type.name), self.capturedOutput.getvalue())

	def test_scan_background_None_instance(self):
		scanner = scannerFactory.scanner(ScannerType.Intraday)
		result = scanner.scan_background(None, terminate_after_iter=2, wait_time=2)
		self.assertIn("Finished all iterations of scanning Intraday.", self.capturedOutput.getvalue())

	def tearDown(self):
		super().tearDown()

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
