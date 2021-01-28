from nseta.common.commons import *
from nseta.common.urls import *
from nseta.common.constants import NSE_INDICES, INDEX_DERIVATIVES
import datetime
import time

import unittest
import pandas as pd
from bs4 import BeautifulSoup
from tests import htmls
import json
import requests
from six.moves.urllib.parse import urlparse
from baseUnitTest import baseUnitTest

import six


def text_to_list(text, schema):
	rows = text.split('\n')
	lists = []
	for row in rows:
		if not row:
			continue
		cols = row.split(',')
		i = 0
		lst = []
		for cell in cols:
			txt = cell
			if schema[i]==float or schema[i]==int:
				txt = cell.replace(' ','').replace(',','')
			try:
				val = schema[i](txt)
			except Exception:
				if schema[i]==float or schema[i]==int:
					val = np.nan
				else:
					val = ''
					#raise ValueError("Error in %d. %s(%s)"%(i, str(schema[i]), txt))
			except SystemExit:
				pass
			lst.append(val)
			i += 1
		lists.append(lst)
	"""
	for i in range(0, len(lists)):
		for j in range(0, len(lists[i])):
			lists[i][j] = schema[i](lists[i][j])
	"""
	return lists


class TestCommons(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()

	def test_is_index(self):
		for i in NSE_INDICES:
			self.assertTrue(is_index(i))

	def test_is_index_derivative(self):
		for i in INDEX_DERIVATIVES:
			self.assertTrue(is_index_derivative(i))

	def test_ParseTables(self):
		# test equity tables

		dd_mmm_yyyy = StrDate.default_format(format="%d-%b-%Y")
		schema = [str, str,
				  dd_mmm_yyyy,
				  float, float, float, float,
				  float, float, float, int, float,
				  int, int, float]
		bs = BeautifulSoup(htmls.html_equity, features='lxml')
		t = ParseTables(soup=bs,
						schema=schema)
		lst = text_to_list(htmls.csv_equity, schema=schema)
		self.assertEqual(lst, t.get_tables())

		# test derivative tables
		schema = [str, dd_mmm_yyyy, dd_mmm_yyyy,
				  float, float, float, float,
				  float, float, int, float,
				  int, int, float]
		bs = BeautifulSoup(htmls.html_derivative, features='lxml')
		t = ParseTables(soup=bs,
						schema=schema)
		lst = text_to_list(htmls.csv_derivative, schema)
		self.assertEqual(lst, t.get_tables())

		# test index tables
		schema = [dd_mmm_yyyy,
				  float, float, float, float,
				  int, float]
		bs = BeautifulSoup(htmls.html_index, features='lxml')
		t = ParseTables(soup=bs,
						schema=schema)
		lst = text_to_list(htmls.csv_index, schema)
		self.assertEqual(lst, t.get_tables())

	def test_ParseTables_headers(self):
		# test equity tables
		dd_mmm_yyyy = StrDate.default_format(format="%d-%b-%Y")
		# schema for equity history values
		schema = [str, str,
				  dd_mmm_yyyy,
				  float, float, float, float,
				  float, float, float, int, float,
				  int, int, float]
		headers = ["Symbol", "Series", "Date", "Prev Close",
				   "Open", "High", "Low", "Last", "Close", "VWAP",
				   "Volume", "Turnover", "Trades", "Deliverable Volume",
				   "%Deliverble"]
		bs = BeautifulSoup(htmls.html_equity, features='lxml')
		t = ParseTables(soup=bs,
						schema=schema, headers=headers, index='Date')
		lst = text_to_list(htmls.csv_equity, schema)
		df = t.get_df()
		self.assertIn("Symbol", df.columns, str(df.columns))

	def test_ParseTables_parse_lists(self):
		csv_data_node='{}\n{}\n{}\n'.format(
			'07-01-2021 09:15:00,2662.4500,,2638.8500,2662.4500', 
			'07-01-2021 09:16:00,2658.6000,,2638.8500,2658.6000', 
			'07-01-2021 09:17:00,2660.0500,,2638.8500,2660.0500')
		dd_mm_yyyy_H_M_S = StrDate.default_format(format="%d-%m-%Y %H:%M:%S")
		INTRADAY_EQUITY_SCHEMA = [dd_mm_yyyy_H_M_S,float, str, float, float]
		INTRADAY_EQUITY_HEADERS = ["Date", "Open", "High", "Low","Close"]
		bs = BeautifulSoup(htmls.html_equity, features='lxml')
		t = ParseTables(soup=bs,
						schema=INTRADAY_EQUITY_SCHEMA, 
						headers=INTRADAY_EQUITY_HEADERS, 
						index='Date')
		lst = text_to_list(csv_data_node, INTRADAY_EQUITY_SCHEMA)
		self.assertEqual(lst, t.parse_lists(csv_data_node))

	def test_StrDate(self):
		dd_mmm_yyyy = StrDate.default_format(format="%d-%b-%Y")
		dt1 = dd_mmm_yyyy(date="12-Nov-2012")
		dt2 = datetime.datetime(2012, 11, 12)
		self.assertEqual(dt1, dt2)

	def test_unzip_str(self):
		self.assertEqual(htmls.unzipped, unzip_str(htmls.zipped))

	def test_ThreadReturns(self):
		def square(ip):
			return ip**2
		t1 = ThreadReturns(target=square, kwargs={'ip': 2})
		t1.start()
		t1.join()
		self.assertEqual(t1.result, 4)

	def test_concatenated_dataframe(self):
		df1 = pd.DataFrame({'A':[123.01], 'B':['Symbol1'], 'C':['2020-01-07']})
		df2 = pd.DataFrame({'A':[122.00], 'B':['Symbol2'], 'C':['2020-01-08']})
		df_actual = concatenated_dataframe(df1, df2)
		df_expected = pd.concat((df1, df2))
		self.assertEqual(df_actual['B'].iloc[0], df_expected['B'].iloc[0])
		self.assertEqual(df_actual['B'].iloc[1], df_expected['B'].iloc[1])

	def tearDown(self):
		super().tearDown()

class TestURLFetch(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()
		self.proxy_on = False
		self.session = requests.Session()
		if self.proxy_on:
			self.session.proxies.update(
				{'http': 'proxy1.wipro.com:8080', 'https': 'proxy.wipro.com:8080'})
		self.session.headers.update({'User-Agent': 'Testing'})
		super().setUp()

	def test_get(self):
		url = 'http://httpbin.org/get'
		http_get = URLFetch(url=url, session=self.session)
		try:
			resp = http_get(key1='val1', key2='val2')
		except requests.exceptions.ConnectionError:
			raise requests.exceptions.ConnectionError(
				'Error fetching (check proxy settings):', url)
		json = resp.json()
		self.assertEqual(json['args']['key1'], 'val1')
		self.assertEqual(json['args']['key2'], 'val2')

	def test_urls_with_args_and_data(self):
		url = 'http://httpbin.org/%s'
		http_post = URLFetch(url=url, method='post', session=self.session)
		try:
			resp = http_post('post', key1='val1', key2='val2')
		except requests.exceptions.ConnectionError as e:
			raise requests.exceptions.ConnectionError(
				'Error fetching (check proxy settings):', url)
		rjson = resp.json()
		self.assertEqual(rjson['form']['key1'], 'val1')
		self.assertEqual(rjson['form']['key2'], 'val2')

	def test_post(self):
		url = 'http://httpbin.org/post'
		http_post = URLFetch(url=url, method='post', session=self.session)
		try:
			resp = http_post(key1='val1', key2='val2')
		except requests.exceptions.ConnectionError as e:
			raise requests.exceptions.ConnectionError(
				'Error fetching (check proxy settings):', url)
		rjson = resp.json()
		self.assertEqual(rjson['form']['key1'], 'val1')
		self.assertEqual(rjson['form']['key2'], 'val2')

	def test_json(self):
		url = 'http://httpbin.org/post'
		http_get = URLFetch(url=url, method='post',
							json=True, session=self.session)
		try:
			resp = http_get(key1='val1', key2='val2')
		except requests.exceptions.ConnectionError as e:
			raise requests.exceptions.ConnectionError(
				'Error fetching (check proxy settings):', url)
		rjson = resp.json()

		self.assertEqual(json.loads(rjson['data']), {u'key1': u'val1',
													 u'key2': u'val2'})

	def test_cookies(self):
		url = 'http://httpbin.org/cookies/set'
		http_cookie = URLFetch(url=url, session=self.session)
		try:
			resp = http_cookie(var1=1, var2='a')
		except requests.exceptions.ConnectionError as e:
			raise requests.exceptions.ConnectionError(
				'Error fetching (check proxy settings):', url)
		rjson = resp.json()
		ok_cookie = 0
		for cookie in self.session.cookies:
			if cookie.name == 'var1' and cookie.value == '1':
				ok_cookie += 1
			if cookie.name == 'var2' and cookie.value == 'a':
				ok_cookie += 1
		self.assertEqual(ok_cookie, 2)

		url = 'http://httpbin.org/get'
		http_get = URLFetch(url=url, session=self.session)
		try:
			resp = http_get(key1='val1', key2='val2')
		except requests.exceptions.ConnectionError as e:
			raise requests.exceptions.ConnectionError(
				'Error fetching (check proxy settings):', url)
		rjson = resp.json()
		self.assertGreaterEqual(rjson['headers']['Cookie'].find('var1=1'), 0)

	def test_headers(self):
		url = 'http://httpbin.org/get'
		http_get = URLFetch(url=url, session=self.session)
		try:
			resp = http_get(key1='val1', key2='val2')
		except requests.exceptions.ConnectionError as e:
			raise requests.exceptions.ConnectionError(
				'Error fetching (check proxy settings):', url)
		json = resp.json()
		self.assertEqual(json['headers']['Host'], 'httpbin.org')
		self.assertEqual(json['headers']['User-Agent'], 'Testing')

	def tearDown(self):
		self.session.close()
		super().tearDown()


if __name__ == '__main__':
	# unittest.main()

	suite = unittest.TestLoader().loadTestsFromTestCase(TestCommons)
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
