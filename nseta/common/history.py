# -*- coding: utf-8 -*-
"""
Created on Tue Aug 24 11:23:30 2020.

Originally adapted from @author: SW274998
"""

from nseta.common.urls import *
from nseta.common.commons import *
from nseta.common.constants import *
from nseta.common.log import tracelog, default_logger
from nseta.archives.archiver import *

import six
from datetime import date, timedelta
from bs4 import BeautifulSoup
import pandas as pd
import inspect
import io

__all__ = ['historicaldata', 'EQUITY_HEADERS', 'INTRADAY_EQUITY_HEADERS']

dd_mmm_yyyy = StrDate.default_format(format="%d-%b-%Y")
dd_mm_yyyy = StrDate.default_format(format="%d-%m-%Y")
dd_mm_yyyy_H_M_S = StrDate.default_format(format="%d-%m-%Y %H:%M:%S")
dd_mm_yyyy_H_M = StrDate.default_format(format="%d-%m-%Y %H:%M")

EQUITY_SCHEMA = [str, str,
				 dd_mmm_yyyy,
				 float, float, float, float,
				 float, float, float, int, float,
				 int, int, float]
EQUITY_HEADERS = ["Symbol", "Series", "Date", "Prev Close",
				  "Open", "High", "Low", "Last", "Close", "VWAP",
				  "Volume", "Turnover", "Trades", "Deliverable Volume",
				  "%Deliverable"]
EQUITY_SCALING = {"Turnover": 100000,
				  "%Deliverable": 0.01}

INTRADAY_EQUITY_SCHEMA = [dd_mm_yyyy_H_M_S,float, str, float, float]
INTRADAY_EQUITY_HEADERS = ["Date", "Open", "High", "Low","Close"] # ["Date", "pltp", "nltp", "previousclose","allltp"]
INTRADAY_EQUITY_SCALING = {}

INTRADAY_EQUITY_SCHEMA_NEW = [dd_mm_yyyy_H_M,float, float, float, float, int, int, int]
INTRADAY_EQUITY_HEADERS_NEW = ["Date", "Open", "High", "Low","Close", 'Volume', 'Cum_Volume', 'Cdl', 'Cnt_Cdl'] # ["Date", "pltp", "nltp", "previousclose","allltp"]

FUTURES_SCHEMA = [str, dd_mmm_yyyy, dd_mmm_yyyy,
				  float, float, float, float,
				  float, float, int, float,
				  int, int, float]

FUTURES_HEADERS = ['Symbol', 'Date', 'Expiry',
				   'Open', 'High', 'Low', 'Close',
				   'Last', 'Settle Price', 'Number of Contracts', 'Turnover',
				   'Open Interest', 'Change in OI', 'Underlying']
FUTURES_SCALING = {"Turnover": 100000}

OPTION_SCHEMA = [str, dd_mmm_yyyy, dd_mmm_yyyy, str, float,
				 float, float, float, float,
				 float, float, int, float,
				 float, int, int, float]
OPTION_HEADERS = ['Symbol', 'Date', 'Expiry', 'Option Type', 'Strike Price',
				  'Open', 'High', 'Low', 'Close',
				  'Last', 'Settle Price', 'Number of Contracts', 'Turnover',
				  'Premium Turnover', 'Open Interest', 'Change in OI', 'Underlying']
OPTION_SCALING = {"Turnover": 100000,
				  "Premium Turnover": 100000}


INDEX_SCHEMA = [dd_mmm_yyyy,
				float, float, float, float,
				int, float]
INDEX_HEADERS = ['Date',
				 'Open', 'High', 'Low', 'Close',
				 'Volume', 'Turnover']
INDEX_SCALING = {'Turnover': 10000000}

VIX_INDEX_SCHEMA = [dd_mmm_yyyy,
					float, float, float, float,
					float, float, float]
VIX_INDEX_HEADERS = ['Date',
					 'Open', 'High', 'Low', 'Close',
					 'Previous', 'Change', '%Change']
VIX_SCALING = {'%Change': 0.01}

INDEX_PE_SCHEMA = [dd_mmm_yyyy,
				   float, float, float]
INDEX_PE_HEADERS = ['Date', 'P/E', 'P/B', 'Div Yield']

RBI_REF_RATE_SCHEMA = [dd_mmm_yyyy, float, float, float, float]
RBI_REF_RATE_HEADERS = ['Date', '1 USD', '1 GBP', '1 EURO', '100 YEN']

class historicaldata:
	"""
		symbol = "SBIN" (stock name, index name and VIX)
		start = date(yyyy,mm,dd)
		end = date(yyyy,mm,dd)
		index = True, False (True even for VIX)
		---------------
		futures = True, False
		option_type = "CE", "PE", "CA", "PA"
		strike_price = integer number
		expiry_date = date(yyyy,mm,dd)

	"""

	@tracelog
	def daily_ohlc_history(self, symbol, start, end, periodicity="1", series='EQ', intraday=False, type=ResponseType.Default):
		"""This is the function to get the historical prices of any security (index,
			stocks, derviatives, VIX) etc.

			Args:
				symbol (str): Symbol for stock, index or any security
				start (datetime.date): start date
				end (datetime.date): end date
				index (boolean): False by default, True if its a index
				futures (boolean): False by default, True for index and stock futures
				expiry_date (datetime.date): Expiry date for derivatives, Compulsory for futures and options
				option_type (str): It takes "CE", "PE", "CA", "PA" for European and American calls and puts
				strike_price (int): Strike price, Compulsory for options
				series (str): Defaults to "EQ", but can be "BE" etc (refer NSE website for details)

			Returns:
				pandas.DataFrame : A pandas dataframe object 

			Raises:
				ValueError:
							1. strike_price argument missing or not of type int when options_type is provided
							2. If there's an Invalid value in option_type, valid values-'CE' or 'PE' or 'CA' or 'CE'
							3. If both futures='True' and option_type='CE' or 'PE'
		"""
		frame = inspect.currentframe()
		args, _, _, kwargs = inspect.getargvalues(frame)
		del(kwargs['frame'])
		del(kwargs['self'])
		start = kwargs['start']
		end = kwargs['end']
		# if intraday:
		# 	get_intraday_history(symbol)
		if (not intraday) and ((end - start) > timedelta(130)):
			kwargs1 = dict(kwargs)
			kwargs2 = dict(kwargs)
			kwargs1['end'] = start + timedelta(130)
			kwargs2['start'] = kwargs1['end'] + timedelta(1)

			t1 = ThreadReturns(target=self.daily_ohlc_history, kwargs=kwargs1)
			t2 = ThreadReturns(target=self.daily_ohlc_history, kwargs=kwargs2)
			t1.start()
			t2.start()
			t1.join()
			t2.join()
			return concatenated_dataframe(t1.result, t2.result)
		else:
			return self.daily_ohlc_history_quanta(**kwargs)

	'''
	#Not being used right now. TODO: Switch to new NSE site.
	@tracelog
	def get_intraday_history(self, symbol):
		resp = nse_intraday_url_new(index=symbol.upper())
		# print(resp)
		data = resp.json()
		print('name:', data['name'])
		print('identifier:', data['identifier'])
		print('close price:', data['closePrice'])

		prices = data['grapthData'][:10]

		for item in prices:
			dt = datetime.datetime.utcfromtimestamp(item[0]/1000)
			value = item[1]
			print(dt, value)
'''
	@tracelog
	def daily_ohlc_history_quanta(self, **kwargs):
		symbol = kwargs['symbol']
		start = kwargs['start']
		end = kwargs['end']
		response_type = kwargs['type']
		df = self.unarchive_history(symbol, start, end, response_type)
		if df is not None and len (df) > 0:
			return df
		try:
			url, params, schema, headers, scaling, csvnode = self.validate_params(**kwargs)
			df = self.url_to_df(url=url,
						   params=params,
						   schema=schema,
						   headers=headers, scaling=scaling, csvnode=csvnode)
			if (df is not None and len(df) > 0) and ('Symbol' in headers and 'Symbol' in df.keys()):
				# Check if we received the correct Symbol in response what we expected
				expected_symbol = symbol
				received_symbol = df['Symbol'].iloc[0]
				if received_symbol.upper() != expected_symbol.upper():
					default_logger().debug(df.to_string(index=False))
					default_logger().debug('Unexpected symbol "{}" received. Retrying...'.format(received_symbol))
					params['symbolCount'] = get_symbol_count(expected_symbol, force_refresh=True)
					# We don't want to recursively call daily_ohlc_history_quanta and risk getting into an infinite loop
					# if the expected symbol is again not received.
					df = self.url_to_df(url=url,
						params=params,
						schema=schema,
						headers=headers, scaling=scaling, csvnode=csvnode)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
		if df is not None and len(df) > 0:
			self.archive_history(df, symbol, start, end, response_type)
		return df


	@tracelog
	def url_to_df(self, url, params, schema, headers, scaling={}, csvnode=None):
		resp = url(**params)
		bs = BeautifulSoup(resp.text, 'lxml')
		tp = ParseTables(soup=bs,
						 schema=schema,
						 headers=headers) # index="Date"
		if csvnode is not None:
			if csvnode == 'data':
				tp.parse_lists(bs.find(csvnode).text)
			elif csvnode == 'g2_CUMVOL':
				tp.parse_g1_g2(bs.text, params['CDSymbol'])
		df = tp.get_df()
		for key, val in six.iteritems(scaling):
			df[key] = val * df[key]
		if df is None or len(df) == 0:
			default_logger().debug('\nIncorrect/invalid or no response received from server:\n{}'.format(resp.text))
		return df


	@tracelog
	def validate_params(self, symbol, start, end, periodicity="1", series='EQ', intraday=False, type=ResponseType.Default):
		"""
					symbol = "SBIN" (stock name, index name and VIX)
					start = date(yyyy,mm,dd)
					end = date(yyyy,mm,dd)
					index = True, False (True even for VIX)
					---------------
					futures = True, False
					option_type = "CE", "PE", "CA", "PA"
					strike_price = integer number
					expiry_date = date(yyyy,mm,dd)
		"""

		params = {}
		csvnode = None
		if start > end:
			raise ValueError('Please check start and end dates')

		if (not intraday):
			params['symbol'] = symbol
			params['series'] = series
			params['symbolCount'] = get_symbol_count(symbol)
			params['fromDate'] = start.strftime('%d-%m-%Y')
			params['toDate'] = end.strftime('%d-%m-%Y')
			url = equity_history_url
			schema = EQUITY_SCHEMA
			headers = EQUITY_HEADERS
			scaling = EQUITY_SCALING
		elif intraday:
			params['CDSymbol'] = symbol
			params['Periodicity'] = periodicity
			url = nse_intraday_url
			schema = INTRADAY_EQUITY_SCHEMA_NEW # INTRADAY_EQUITY_SCHEMA
			headers = INTRADAY_EQUITY_HEADERS_NEW # INTRADAY_EQUITY_HEADERS
			scaling = INTRADAY_EQUITY_SCALING
			csvnode = 'g2_CUMVOL' # "data"

		return url, params, schema, headers, scaling, csvnode


	@tracelog
	def get_index_pe_history(self, symbol, start, end):
		frame = inspect.currentframe()
		args, _, _, kwargs = inspect.getargvalues(frame)
		del(kwargs['frame'])
		del(kwargs['self'])
		start = kwargs['start']
		end = kwargs['end']
		if (end - start) > timedelta(130):
			kwargs1 = dict(kwargs)
			kwargs2 = dict(kwargs)
			kwargs1['end'] = start + timedelta(130)
			kwargs2['start'] = kwargs1['end'] + timedelta(1)
			t1 = ThreadReturns(target=self.get_index_pe_history, kwargs=kwargs1)
			t2 = ThreadReturns(target=self.get_index_pe_history, kwargs=kwargs2)
			t1.start()
			t2.start()
			t1.join()
			t2.join()
			return pd.concat((t1.result, t2.result))
		else:
			return self.get_index_pe_history_quanta(**kwargs)


	@tracelog
	def get_index_pe_history_quanta(self, symbol, start, end):
		"""This function will fetch the P/E, P/B and dividend yield for a given index

			Args:
				symbol (str): Symbol for stock, index or any security
				start (datetime.date): start date
				end (datetime.date): end date

			Returns:
				pandas.DataFrame : A pandas dataframe object 
		"""
		if symbol in DERIVATIVE_TO_INDEX:
			index_name = DERIVATIVE_TO_INDEX[symbol]
		else:
			index_name = symbol
		resp = index_pe_history_url(indexName=index_name,
									fromDate=start.strftime('%d-%m-%Y'),
									toDate=end.strftime('%d-%m-%Y'))

		bs = BeautifulSoup(resp.text, 'lxml')
		tp = ParseTables(soup=bs,
						 schema=INDEX_PE_SCHEMA,
						 headers=INDEX_PE_HEADERS, index="Date")
		df = tp.get_df()
		return df


	@tracelog
	def get_price_list(self, dt, series='EQ'):
		MMM = dt.strftime("%b").upper()
		yyyy = dt.strftime("%Y")

		"""
		1. YYYY
		2. MMM
		3. ddMMMyyyy
		"""
		res = price_list_url(yyyy, MMM, dt.strftime("%d%b%Y").upper())
		txt = unzip_str(res.content)
		fp = six.StringIO(txt)
		df = pd.read_csv(fp)
		del df['Unnamed: 13']
		return df[df['SERIES'] == series]

	"""
	Get Price range for all Indices
	"""
	@tracelog
	def get_indices_price_list(self, dt):
		res = index_daily_snapshot_url(dt.strftime("%d%m%Y"))
		df = pd.read_csv(io.StringIO(res.content.decode('utf-8')))
		df = df.rename(columns={"Index Name": "NAME",
								"Index Date": "TIMESTAMP",
								"Open Index Value": "OPEN",
								"High Index Value": "HIGH",
								"Low Index Value": "LOW",
								"Closing Index Value": "CLOSE",
								"Points Change": "CHANGE",
								"Change(%)": "CHANGEPCT",
								"Volume": "TOTTRDQTY",
								"Turnover (Rs. Cr.)": "TOTTRDVAL",
								"P/E": "PE",
								"P/B": "PB",
								"Div Yield": "DIVYIELD"})
		return df

	'''
	@tracelog
	def get_rbi_ref_history(self, start, end):
		frame = inspect.currentframe()
		args, _, _, kwargs = inspect.getargvalues(frame)
		del(kwargs['frame'])
		del(kwargs['self'])
		start = kwargs['start']
		end = kwargs['end']
		if (end - start) > timedelta(130):
			kwargs1 = dict(kwargs)
			kwargs2 = dict(kwargs)
			kwargs1['end'] = start + timedelta(130)
			kwargs2['start'] = kwargs1['end'] + timedelta(1)
			t1 = ThreadReturns(target=self.get_rbi_ref_history, kwargs=kwargs1)
			t2 = ThreadReturns(target=self.get_rbi_ref_history, kwargs=kwargs2)
			t1.start()
			t2.start()
			t1.join()
			t2.join()
			return concatenated_dataframe(t1.result, t2.result)
		else:
			return self.get_rbi_ref_history_quanta(**kwargs)

	@tracelog
	def get_rbi_ref_history_quanta(self, start, end):
		"""
			Args:
				start (datetime.date): start date
				end (datetime.date): end date

			Returns:
				pandas.DataFrame : A pandas dataframe object 
		"""
		resp = rbi_rate_history_url(fromDate=start.strftime('%d-%m-%Y'),
									toDate=end.strftime('%d-%m-%Y'))

		bs = BeautifulSoup(resp.text, 'lxml')
		tp = ParseTables(soup=bs,
						 schema=RBI_REF_RATE_SCHEMA,
						 headers=RBI_REF_RATE_HEADERS, index="Date")
		df = tp.get_df()
		return df
	'''
	@tracelog
	def archive_history(self, df, symbol, start_date, end_date, response_type=ResponseType.Default):
		symbol = symbol if response_type == ResponseType.Intraday else '{}_{}_{}'.format(symbol, start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))
		arch = archiver()
		arch.archive(df, symbol, response_type)

	@tracelog
	def unarchive_history(self, symbol, start_date, end_date, response_type=ResponseType.Default):
		symbol = symbol if response_type == ResponseType.Intraday else '{}_{}_{}'.format(symbol, start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y'))
		arch = archiver()
		df = arch.restore(symbol, response_type)
		return df