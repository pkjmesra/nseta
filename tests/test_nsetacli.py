# -*- coding: utf-8 -*-
import pdb
import unittest
import time

from click.testing import CliRunner

from nseta.cli.nsetacli import nsetacli
import nseta

class TestNSEtacli(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_nsetacli_entry(self):
		runner = CliRunner()
		result = runner.invoke(nsetacli, args=['--debug', '--trace'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Debug mode is on", result.output, str(result.output))
		self.assertIn("Tracing mode is on", result.output, str(result.output))
	
	def test_nsetacli_cmd_options(self):
		runner = CliRunner()
		result = runner.invoke(nsetacli, args=[])
		self.assertEqual(result.exit_code , 0)
		self.assertIn("Usage: nsetacli [OPTIONS] COMMAND [ARGS]", result.output, str(result.output))

	def test_nsetacli_version(self):
		runner = CliRunner()
		result = runner.invoke(nsetacli, args=['--version'])
		self.assertEqual(result.exit_code , 0)
		self.assertIn('nseta ' + nseta.__version__ , result.output, str(result.output))

	def tearDown(self):
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestNSEtacli)
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
