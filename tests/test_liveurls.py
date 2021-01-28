import datetime
import unittest
import json
import requests
import six

import timeout_decorator

from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from tests import htmls
from nseta.live.liveurls import quote_eq_url, quote_derivative_url, futures_chain_url, holiday_list_url
import nseta.common.urls as urls
from baseUnitTest import baseUnitTest
from nseta.common.commons import (is_index, is_index_derivative,
						   NSE_INDICES, INDEX_DERIVATIVES,
						   ParseTables, StrDate, unzip_str,
						   ThreadReturns, URLFetch)

LOCAL_TIMEOUT = 60
class TestLiveUrls(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()
		proxy_on = False
		if proxy_on:
			urls.session.proxies.update({'http': 'proxy1.wipro.com:8080'})

	def runTest(self):
		for key in TestUrls.__dict__.keys():
			if key.find('test') == 0:
				TestUrls.__dict__[key](self)

	def test_quote_eq_url(self):
		resp = quote_eq_url('SBIN', 'EQ')
		html_soup = BeautifulSoup(resp.text, 'lxml')
		hresponseDiv = html_soup.find("div", {"id": "responseDiv"})
		d = json.loads(hresponseDiv.get_text())
		self.assertEqual(d['data'][0]['symbol'], 'SBIN')

	def test_quote_derivative_url(self):
		base_expiry_date = datetime(2020,12,31)
		expiry_date = self.get_next_expiry_date(base_expiry_date).strftime("%d%b%Y").upper()
		resp = quote_derivative_url("NIFTY", "FUTIDX", expiry_date, '-', '-')
		html_soup = BeautifulSoup(resp.text, 'lxml')
		hresponseDiv = html_soup.find("div", {"id": "responseDiv"})
		d = json.loads(hresponseDiv.get_text().strip())
		self.assertEqual(d['data'][0]['underlying'], 'NIFTY')

	# @timeout_decorator.timeout(LOCAL_TIMEOUT)
	# def test_option_chain_url(self):
	#     """
	#         1. Underlying symbol
	#         2. instrument (FUTSTK, OPTSTK, FUTIDX, OPTIDX)
	#         3. expiry date (ddMMMyyyy) where dd is not padded with zero when date is single digit
	#     """

	#     resp = option_chain_url('SBIN', 'OPTSTK', '30JAN2020')
	#     self.assertGreaterEqual(resp.text.find('Open Interest'), 0)

	@timeout_decorator.timeout(LOCAL_TIMEOUT)
	def test_futures_chain_url(self):
		"""
			1. Underlying symbol
		"""

		resp = futures_chain_url('NIFTY')
		self.assertGreaterEqual(resp.text.find('Expiry Date'), 0)

	def test_holiday_list_url(self):
		resp = holiday_list_url("01Jan2019", "31Mar2019")
		self.assertGreaterEqual(resp.text.find('Holi'), 0)

	def tearDown(self):
		super().tearDown()

	def get_next_expiry_date(self, base_expiry_date):
		new_expiry_date = base_expiry_date
		if base_expiry_date < datetime.now():
			new_expiry_date = self.get_next_expiry_date(base_expiry_date + timedelta(28))
		return new_expiry_date

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestLiveUrls)
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
