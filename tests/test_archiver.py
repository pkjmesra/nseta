# -*- coding: utf-8 -*-
import pdb
import unittest
import pandas as pd
import os
import time

from nseta.archives.archiver import *

class TestArchiver(unittest.TestCase):
	def setUp(self):
		self.startTime = time.time()

	def test_get_path_default(self):
		a = archiver()
		result = a.get_path('SomeSymbol', ResponseType.Default)
		self.assertIn('/nseta/archives/SOMESYMBOL', result)

	def test_get_directory_default(self):
		a = archiver()
		result = a.get_directory(ResponseType.Default)
		self.assertIn('/nseta/archives', result)

	def test_clearcache(self):
		a = archiver()
		symbol = 'Symbol'
		response_type = ResponseType.Default
		a.archive(pd.DataFrame({'A':['B'],'C':['D']}), symbol, response_type)
		file_path = a.get_path(symbol, response_type)
		self.assertTrue(os.path.exists(file_path))
		a.clearcache(symbol, response_type, force_clear=True)
		self.assertFalse(os.path.exists(file_path))

	def tearDown(self):
		t = time.time() - self.startTime
		print('%s: %.3f' % (self.id().ljust(100), t))

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestArchiver)
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
