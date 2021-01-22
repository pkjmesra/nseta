# -*- coding: utf-8 -*-
import pdb
import unittest
import time

from nseta.resources.resources import resources

class TestResources(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_default_config(self):
		r = resources()
		self.assertTrue(r is not None)

	def test_config_section(self):
		r = resources()
		result = r.config_section('SCANNER')
		self.assertTrue(result['UserStocks'] is not None)

	def test_invalid_config_section(self):
		r = resources()
		result = r.config_section('NON_EXISTING')
		self.assertEqual(result, None)

	def test_config_valueforkey(self):
		r = resources()
		result = r.config_valueforkey('DEFAULT', 'DefaultStocks')
		self.assertEqual(result, 'stocks.txt')

	def test_invalid_config_valueforkey(self):
		r = resources()
		result = r.config_valueforkey('NON_EXISTING', 'NON_EXISTING_KEY')
		self.assertEqual(result, None)
		result = r.config_valueforkey('DEFAULT', 'NON_EXISTING_KEY')
		self.assertEqual(result, None)

	def test_default_stocks(self):
		result = resources.default_stocks()
		self.assertTrue(len(result) > 0)

	def tearDown(self):
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestResources)
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
