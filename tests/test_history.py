# -*- coding: utf-8 -*-
"""
Created on Tue Nov 24 21:57:53 2015

@author: Swapnil Jariwala
"""
import pandas as pd
from nseta.common.history import historicaldata
from nseta.common.urls import get_symbol_count
from nseta.common import urls
from nseta.common import history
from nseta.archives.archiver import ResponseType
from baseUnitTest import baseUnitTest
import time

import unittest
from datetime import date, timedelta
import six

class TestHistory(baseUnitTest):
		def setUp(self, redirect_logs=True):
				super().setUp()
				self.start = date(2020, 12, 30)
				self.end = date(2021, 1, 8)
				self.historicaldata = historicaldata()

		def test_validate_params(self):
				# test stock history param validation
				(url, params, schema,
				 headers, scaling, csvnode) = self.historicaldata.validate_params(symbol='SBIN',
																						 start=date(2020, 12, 30),
																						 end=date(2021, 1, 8))

				params_ref = {"symbol": "SBIN", "symbolCount": '1',
											"series": "EQ", "fromDate": "30-12-2020",
											"toDate": "08-01-2021"}
				self.assertEqual(params, params_ref)
				self.assertEqual(url, urls.equity_history_url)
				self.assertEqual(schema, history.EQUITY_SCHEMA)

				negative_args = []
				# start>end
				negative_args.append({'symbol': 'SBIN', 'end': date(2020, 12, 30),
															'start': date(2021, 1, 8)})
				# test for exceptions
				for n_arg in negative_args:
						with self.assertRaises(ValueError):
								self.historicaldata.validate_params(**n_arg)

		def test_get_price_list(self):
				testdate = date(2021, 1, 7)
				testsymbol = 'IDFCFIRSTB'

				# Check Stock
				dfpleq = self.historicaldata.get_price_list(testdate, 'EQ')
				stk = dfpleq[dfpleq['SYMBOL'] == 'IDFCFIRSTB'].squeeze()
				self.assertEqual(stk['CLOSE'], 45.8)

				# Check Bond
				testsymbol = 'NHAI'
				dfpln1 = self.historicaldata.get_price_list(testdate, 'N1')
				bond = dfpln1[dfpln1['SYMBOL'] == testsymbol].squeeze()
				self.assertEqual(bond['CLOSE'], 1064.34)

		def test_get_indices_price_list(self):
				testdate = date(2021, 1, 7)

				# Check closing for index
				dfplidx = self.historicaldata.get_indices_price_list(testdate)
				idxname = dfplidx[dfplidx['NAME'] == 'Nifty 100'].squeeze()
				self.assertEqual(idxname['CLOSE'], 14305.5)

		# Test for data for problematic symbols BBTC,ALOKINDS,IRB,M&MFIN,POWERINDIA,PVR,SBICARD,SUMICHEM,SUVENPHAR

		'''
			For some symbols, get_history() returns data of the wrong (but similarly named scrip). 
			Test to ensure the symbol_count is updated

			Requested symbol  Returned Scrip
			DVL DTIL
			GOKUL GOKULAGRO
			ICIL  ICICILOVOL
			JSL JSLHISAR
		'''
		def test_daily_ohlc_history_for_DVL_GOKUL_symbols(self):
				result = self.historicaldata.daily_ohlc_history('DVL', start=date.today()-timedelta(4), end = date.today(), type=ResponseType.Volume)
				row1 = result['Symbol'].iloc[0]
				row2 = (result['Symbol']).iloc[1]
				self.assertEqual('DVL', row1 if row1 == 'DVL' else row2)
				result = self.historicaldata.daily_ohlc_history('GOKUL', start=(date.today()-timedelta(4)), end = date.today(), type=ResponseType.Volume)
				row1 = result['Symbol'].iloc[0]
				self.assertEqual('GOKUL', row1)
				result = self.historicaldata.daily_ohlc_history('ICIL', start=(date.today()-timedelta(4)), end = date.today(), type=ResponseType.Volume)
				row1 = result['Symbol'].iloc[0]
				self.assertEqual('ICIL', row1)
				result = self.historicaldata.daily_ohlc_history('JSL', start=(date.today()-timedelta(4)), end = date.today(), type=ResponseType.Volume)
				row1 = result['Symbol'].iloc[0]
				self.assertEqual('JSL', row1)

		# def test_get_rbi_ref_history(self):
		# 	start_date = date.today()-timedelta(131)
		# 	result = self.historicaldata.get_rbi_ref_history(start_date, date.today())
		# 	print(result)

		def tearDown(self):
				super().tearDown()


if __name__ == '__main__':

		suite = unittest.TestLoader().loadTestsFromTestCase(TestHistory)
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
