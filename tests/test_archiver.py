# -*- coding: utf-8 -*-
import unittest
import pandas as pd
import os

from nseta.archives.archiver import *
from nseta.resources.resources import *
from baseUnitTest import baseUnitTest

class TestArchiver(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_get_path(self):
		a = archiver()
		result = a.get_path('SomeSymbol', ResponseType.Default)
		self.assertIn('/run/SOMESYMBOL', result)
		result = a.get_path('SomeSymbol', ResponseType.Intraday)
		self.assertIn('/run/intraday/SOMESYMBOL', result)
		result = a.get_path('SomeSymbol', ResponseType.History)
		self.assertIn('/run/history/SOMESYMBOL', result)
		result = a.get_path('SomeSymbol', ResponseType.Quote)
		self.assertIn('/run/quote/SOMESYMBOL', result)
		result = a.get_path('SomeSymbol', ResponseType.Volume)
		self.assertIn('/run/volume/SOMESYMBOL', result)

	def test_get_directory(self):
		a = archiver()
		result = a.get_directory(ResponseType.Default)
		self.assertIn('/run', result)
		result = a.get_directory(ResponseType.Intraday)
		self.assertIn('/run/intraday', result)
		result = a.get_directory(ResponseType.History)
		self.assertIn('/run/history', result)
		result = a.get_directory(ResponseType.Quote)
		self.assertIn('/run/quote', result)
		result = a.get_directory(ResponseType.Volume)
		self.assertIn('/run/volume', result)

	def test_all_directories_created(self):
		test_dir = os.path.dirname(os.path.realpath(__file__))
		res_dir = os.path.join(test_dir, 'fixtures')
		res = resources(res_dir=res_dir)
		user_dir = res.config_valueforkey('DEFAULT',"UserDataDirectory")
		a = archiver(data_dir=user_dir)
		self.assertTrue(os.path.exists(a.archival_directory))
		self.assertTrue(os.path.exists(a.run_directory))
		self.assertTrue(os.path.exists(a.logs_directory))
		self.assertTrue(os.path.exists(a.intraday_directory))
		self.assertTrue(os.path.exists(a.history_directory))
		self.assertTrue(os.path.exists(a.quote_directory))
		self.assertTrue(os.path.exists(a.volume_directory))

	def test_archive(self):
		a = archiver()
		df = pd.DataFrame({'A':['B'],'C':['D']})
		symbol = 'RANDOM_TEST_ARCHIVE'
		a.archive(df, symbol, ResponseType.Default)
		self.assertTrue(os.path.exists(a.get_path(symbol,ResponseType.Default)))
		a.archive(df, symbol, ResponseType.Intraday)
		self.assertTrue(os.path.exists(a.get_path(symbol,ResponseType.Intraday)))
		a.archive(df, symbol, ResponseType.History)
		self.assertTrue(os.path.exists(a.get_path(symbol,ResponseType.History)))
		a.archive(df, symbol, ResponseType.Quote)
		self.assertTrue(os.path.exists(a.get_path(symbol,ResponseType.Quote)))
		a.archive(df, symbol, ResponseType.Volume)
		self.assertTrue(os.path.exists(a.get_path(symbol,ResponseType.Volume)))
		
		df_empty = pd.DataFrame(columns=['A'])
		symbol = 'RANDOM_TEST_ARCHIVE_EMPTY'
		a.archive(df_empty, symbol, ResponseType.Default)
		self.assertFalse(os.path.exists(a.get_path(symbol,ResponseType.Default)))
		a.archive(df_empty, symbol, ResponseType.Intraday)
		self.assertFalse(os.path.exists(a.get_path(symbol,ResponseType.Intraday)))
		a.archive(df_empty, symbol, ResponseType.History)
		self.assertFalse(os.path.exists(a.get_path(symbol,ResponseType.History)))
		a.archive(df_empty, symbol, ResponseType.Quote)
		self.assertFalse(os.path.exists(a.get_path(symbol,ResponseType.Quote)))
		a.archive(df_empty, symbol, ResponseType.Volume)
		self.assertFalse(os.path.exists(a.get_path(symbol,ResponseType.Volume)))

	def test_restore(self):
		a = archiver()
		symbol = 'NONEXISTING'
		result = a.restore(symbol, ResponseType.Default)
		self.assertEqual(result, None)
		result = a.restore(symbol, ResponseType.Intraday)
		self.assertEqual(result, None)
		result = a.restore(symbol, ResponseType.History)
		self.assertEqual(result, None)
		result = a.restore(symbol, ResponseType.Quote)
		self.assertEqual(result, None)
		result = a.restore(symbol, ResponseType.Volume)
		self.assertEqual(result, None)

		df_empty = pd.DataFrame(columns=['A'])
		symbol = 'RANDOM_TEST_RESTORE_EMPTY'
		df_empty.to_csv(a.get_path(symbol, ResponseType.Default), index=False)
		result = a.restore(symbol, ResponseType.Default)
		self.assertTrue(result.empty)
		df_empty.to_csv(a.get_path(symbol, ResponseType.Intraday), index=False)
		result = a.restore(symbol, ResponseType.Intraday)
		self.assertTrue(result.empty)
		df_empty.to_csv(a.get_path(symbol, ResponseType.History), index=False)
		result = a.restore(symbol, ResponseType.History)
		self.assertTrue(result.empty)
		df_empty.to_csv(a.get_path(symbol, ResponseType.Quote), index=False)
		result = a.restore(symbol, ResponseType.Quote)
		self.assertTrue(result.empty)
		df_empty.to_csv(a.get_path(symbol, ResponseType.Volume), index=False)
		result = a.restore(symbol, ResponseType.Volume)
		self.assertTrue(result.empty)

		symbol = 'RANDOM_TEST_RESTORE'
		df_non_empty = pd.DataFrame({'A':[symbol],'B':['C']})
		df_non_empty.to_csv(a.get_path(symbol, ResponseType.Default), index=False)
		result = a.restore(symbol, ResponseType.Default)
		self.assertTrue(result['A'].iloc[0] == symbol)
		self.assertIn('Fetched RANDOM_TEST_RESTORE from the disk cache.', self.capturedOutput.getvalue())
		df_non_empty.to_csv(a.get_path(symbol, ResponseType.Intraday), index=False)
		result = a.restore(symbol, ResponseType.Intraday)
		self.assertTrue(result['A'].iloc[0] == symbol)
		self.assertIn('Fetched RANDOM_TEST_RESTORE from the disk cache.', self.capturedOutput.getvalue())
		df_non_empty.to_csv(a.get_path(symbol, ResponseType.History), index=False)
		result = a.restore(symbol, ResponseType.History)
		self.assertTrue(result['A'].iloc[0] == symbol)
		self.assertIn('Fetched RANDOM_TEST_RESTORE from the disk cache.', self.capturedOutput.getvalue())
		df_non_empty.to_csv(a.get_path(symbol, ResponseType.Quote), index=False)
		result = a.restore(symbol, ResponseType.Quote)
		self.assertTrue(result['A'].iloc[0] == symbol)
		self.assertIn('Fetched RANDOM_TEST_RESTORE from the disk cache.', self.capturedOutput.getvalue())
		df_non_empty.to_csv(a.get_path(symbol, ResponseType.Volume), index=False)
		result = a.restore(symbol, ResponseType.Volume)
		self.assertTrue(result['A'].iloc[0] == symbol)
		self.assertIn('Fetched RANDOM_TEST_RESTORE from the disk cache.', self.capturedOutput.getvalue())

	def test_restore_from_path(self):
		a = archiver()
		symbol = 'RANDOM_TEST_RESTORE_FROM_PATH'
		df_non_empty = pd.DataFrame({'A':[symbol],'B':['C']})
		df_non_empty.to_csv(a.get_path(symbol, ResponseType.Default), index=False)
		result = archiver.restore_from_path(a.get_path(symbol, ResponseType.Default))
		self.assertTrue(result['A'].iloc[0] == symbol)

	def test_clearcache(self):
		a = archiver()
		symbol = 'CLEARCACHE'
		response_type = ResponseType.Default
		a.archive(pd.DataFrame({'A':['B'],'C':['D']}), symbol, response_type)
		file_path = a.get_path(symbol, response_type)
		self.assertTrue(os.path.exists(file_path))
		a.clearcache(symbol, response_type, force_clear=True)
		self.assertFalse(os.path.exists(file_path))
		a.archive(pd.DataFrame({'A':['B'],'C':['D']}), symbol, response_type)
		self.assertTrue(os.path.exists(file_path))
		a.clearcache(response_type=response_type, force_clear=True)
		self.assertFalse(os.path.exists(file_path))

	def tearDown(self):
		super().tearDown()

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
