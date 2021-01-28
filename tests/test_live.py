import datetime
import unittest
import json
import requests
import six

from bs4 import BeautifulSoup
from baseUnitTest import baseUnitTest
from tests import htmls
from nseta.live.liveurls import quote_eq_url, quote_derivative_url, option_chain_url, futures_chain_url
from nseta.live.live import get_quote, get_futures_chain_table, get_holidays_list, getworkingdays
from nseta.common.commons import (is_index, is_index_derivative,
						   NSE_INDICES, INDEX_DERIVATIVES,
						   ParseTables, StrDate, unzip_str,
						   ThreadReturns, URLFetch)

class TestLive(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def runTest(self):
		for key in TestUrls.__dict__.keys():
			if key.find('test') == 0:
				TestUrls.__dict__[key](self)

	def test_get_quote_eq(self):
		q = get_quote(symbol='SBIN')
		comp_name = q['data'][0]['companyName']
		self.assertEqual(comp_name, "State Bank of India")

	def test_get_futures_chain(self):
		"""
		1. Underlying security (stock symbol or index name)
		"""
		n = datetime.datetime.now()
		dftable = get_futures_chain_table('NIFTY')

		# Atleast 3 expiry sets should be open
		self.assertGreaterEqual(len(dftable), 3)

		(dtnear, dtnext, dtfar) = dftable.index.tolist()
		self.assertLess(dtnear, dtnext)
		self.assertLess(dtnext, dtfar)

	def test_get_holiday_list(self):
		"""
		Check holiday list for first quarter for 2019 against the expected data
		-----------------------------------------------------------
		Date               Day Of the Week             Description
		------------------------------------------------------------
		2019-03-04          Monday           Mahashivratri
		2019-03-21        Thursday                    Holi
		"""
		fromdate = datetime.date(2019, 1, 1)
		todate = datetime.date(2019, 3, 31)
		lstholiday = get_holidays_list(fromdate, todate)
		self.assertEqual(len(lstholiday), 2)
		self.assertFalse(
			lstholiday[lstholiday['Description'] == "Mahashivratri"].empty)
		self.assertFalse(
			lstholiday[lstholiday['Day'] == "Thursday"].empty)

		with self.assertRaises(ValueError):
			get_holidays_list(todate, fromdate)

	def test_working_day(self):
		# 20 to 28th aug
		independenceday = datetime.date(2021, 8, 15)
		workingdays = getworkingdays(datetime.date(
			2021, 8, 13), datetime.date(2021, 8, 17))
		self.assertFalse(independenceday in workingdays)
		self.assertEqual(len(workingdays), 3)

		# working days in March 2019
		# 31 day month with 2 holidays
		workingdays = getworkingdays(datetime.date(
			2021, 3, 1), datetime.date(2021, 3, 31))
		self.assertEqual(len(workingdays), 23)

		# working day for special dates on weekend
		workingdays = getworkingdays(datetime.date(
			2020, 1, 31), datetime.date(2020, 2, 3))
		self.assertEqual(len(workingdays), 3)
		
	def tearDown(self):
		super().tearDown()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestLive)
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
