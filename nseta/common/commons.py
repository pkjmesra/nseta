# -*- coding: utf-8 -*-
"""
Created on Mon Aug 23 10:10:30 2020.

@author: SW274998
"""
import requests
from nseta.common.constants import NSE_INDICES, INDEX_DERIVATIVES
from nseta.resources.resources import *
from nseta.common.log import default_logger
from nseta.common.tradingtime import IST_datetime
import datetime
from functools import partial
try:
	import pandas as pd
except ImportError:
	pass

import enum
import zipfile
import threading
import six

import numpy as np

from six.moves.urllib.parse import urlparse

__all__ = ['ParseNews','Recommendation','months','Direction','concatenated_dataframe','is_index','is_index_derivative', 'StrDate', 'ParseTables', 'unzip_str', 'ThreadReturns', 'URLFetch']

class Direction(enum.Enum):
	Down = 1
	Neutral = 2
	Up = 3
	V = 4
	InvertedV = 5
	LowerLow = 6
	HigherHigh = 7
	OverBought = 8
	OverSold = 9
	PossibleReversalUpward = 10
	PossibleReversalDownward = 11

class Recommendation(enum.Enum):
	Unknown = 1
	Buy = 2
	Sell = 3
	Hold = 4

def is_index(index):
	return index in NSE_INDICES

def is_index_derivative(index):
	return index in INDEX_DERIVATIVES

months = ["Unknown",
	"January",
	"Febuary",
	"March",
	"April",
	"May",
	"June",
	"July",
	"August",
	"September",
	"October",
	"November",
	"December"]


class StrDate(datetime.date):
	"""
	for pattern-
		https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior

	"""
	def __new__(cls, date, format):

		if(isinstance(date,datetime.date)):
			return datetime.date.__new__(datetime.date, date.year,
										 date.month, date.day)
		dt = datetime.datetime.strptime(date, format)
		if(isinstance(dt,datetime.datetime)):
			return dt
		return datetime.date.__new__(datetime.date, dt.year,
									 dt.month, dt.day)

	@classmethod
	def default_format(cls, format):
		"""
		returns a new class with a default parameter format in the __new__
		method. so that string conversions would be simple in TableParsing with
		single parameter
		"""
		class Date_Formatted(cls):
			pass
		Date_Formatted.__new__ = partial(cls.__new__, format = format)
		return Date_Formatted

class ParseTables:
	def __init__(self, *args, **kwargs):
		self.schema = kwargs.get('schema')
		self.bs = kwargs.get('soup')
		self.headers = kwargs.get('headers')
		self.index = kwargs.get('index')
		self._parse()

	def _parse(self):
		trs = self.bs.find_all('tr')
		lists = []
		schema = self.schema
		for tr in trs:
			tds = tr.find_all('td')
			if len(tds) == len(schema):
				lst = []
				for i in range(0, len(tds)):
					txt = tds[i].text.replace('\n','').replace(' ','').replace(',','')
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
				lists.append(lst)
		self.lists = lists

	def get_tables(self):
		return self.lists

	def get_df(self):
		if self.index:
			return pd.DataFrame(self.lists, columns=self.headers).set_index(self.index)
		else:
			return pd.DataFrame(self.lists, columns=self.headers)

	def parse_lists(self, text):
		rows = text.split('\n')
		lists = []
		schema = self.schema
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
				except SystemExit:
					pass
				lst.append(val)
				i += 1
			lists.append(lst)
		self.lists = lists
		return lists

	def parse_g1_g2(self, text, symbol):
		rows = text.split('~')
		lists = []
		schema = self.schema
		candle = None
		cnt_candle = 0
		for row in rows:
			if not row:
				continue
			cols = row.split('|')
			i = 0
			lst = []
			for cell in cols:
				txt = cell
				# date|g1_o|g1_h|g1_l|g1_c|g2|g2_CUMVOL
				if txt == 'date':
					# We don't want to parse the first header row.
					break
				if schema[i]==float or schema[i]==int:
					txt = cell.replace(' ','').replace(',','')
				try:
					val = schema[i](txt)
				except Exception:
					if schema[i]==float or schema[i]==int:
						val = np.nan
					else:
						val = ''
				except SystemExit:
					pass
				lst.append(val)
				i += 1
			if len(lst) > 4:
				o = lst[1]
				c = lst[4]
				if c > o:
					# Bullish candle
					if candle is None or candle == '+':
						cnt_candle += 1
					else:
						cnt_candle = 1
					candle = '+'
				elif o > c:
					# Bearish candle
					if candle is None or candle == '-':
						cnt_candle += 1
					else:
						cnt_candle = 1
					candle = '-'
				lst.append(candle)
				lst.append(cnt_candle)
				lists.append(lst)
		self.lists = lists
		if len(lists) == 0:
			default_logger().debug('\nFor {}, no response received for NSE Intraday request. Please report to the developer.\n'.format(symbol))
		return lists

def unzip_str(zipped_str, file_name = None):
	if isinstance(zipped_str, six.binary_type):
		fp = six.BytesIO(zipped_str)
	else:
		fp = six.BytesIO(six.b(zipped_str))

	zf = zipfile.ZipFile(file=fp)
	if not file_name:
		file_name = zf.namelist()[0]
	return zf.read(file_name).decode('utf-8')

class ParseNews:
	def __init__(self, *args, **kwargs):
		self.bs = kwargs.get('soup')

	def parse_news(self, symbol=None):
		diff_hrs = None
		try:
			news_text = self.bs.find_all('script')
			next_all_data = (news_text[1].text).split('__NEXT_DATA__ = ')
			next_data = next_all_data[1].split(';__NEXT_LOADED_PAGES__')
			false = False
			true = True
			null = None
			default_logger().debug('false:{}:true{}:null:{}'.format(false, true, null))
			news_dict = eval(next_data[0])
			news = news_dict['props']['pageProps']['news'][0]
			headline = news['headline']
			pub_date = datetime.datetime.fromisoformat(news['date'].replace('Z', '+00:00'))
			diff = (IST_datetime() - pub_date).total_seconds()
			diff_hrs = abs(int(divmod(diff, 3600)[0]))
			diff_hrs_str = '{}h ago'.format(diff_hrs) if diff_hrs <=24 else '{}d ago'.format(int(diff_hrs/24))
			publisher = news['publisher']
			lst=[symbol, diff_hrs, diff_hrs_str, publisher, headline]
			self.news_list = [lst]
			default_logger().debug('news_dict:\n{}\n'.format(news_dict))
		except Exception as e:
			default_logger().debug(e, exc_info=True)
		return '' if diff_hrs is None else '({}){}...'.format(diff_hrs_str, headline[:resources.scanner().max_column_length])

class ThreadReturns(threading.Thread):
	def run(self):
		self.result = self._target(*self._args, **self._kwargs)

class URLFetch:

	def __init__(self, url, method='get', json=False, session=None,
				 headers = None, proxy = None):
		self.url = url
		self.method = method
		self.json = json

		if not session:
			self.session = requests.Session()
		else:
			self.session = session

		if headers:
			self.update_headers(headers)
		if proxy:
			self.update_proxy(proxy)
		else:
			self.update_proxy('')
	'''
	def set_session(self, session):
		self.session = session
		return self

	def get_session(self, session):
		self.session = session
		return self

	def __enter__(self):
		return self

	def close(self):
		self.session.close()

	def __exit__(self, exc_type, exc_value, traceback):
		self.close()
	'''

	def __call__(self, *args, **kwargs):
		u = urlparse(self.url)
		self.session.headers.update({'Host': u.hostname})
		url = self.url%(args)
		if self.method == 'get':
			return self.session.get(url, params=kwargs, proxies = self.proxy )
		elif self.method == 'post':
			if self.json:
				return self.session.post(url, json=kwargs, proxies = self.proxy )
			else:
				return self.session.post(url, data=kwargs, proxies = self.proxy )

	def update_proxy(self, proxy):
		self.proxy = proxy
		self.session.proxies.update(self.proxy)

	def update_headers(self, headers):
		self.session.headers.update(headers)

def concatenated_dataframe(df1, df2):
	if df1 is not None and len(df1) > 0:
		if df2 is not None and len(df2) > 0:
			df = pd.concat((df1, df2))
		else:
			df = df1
	elif df2 is not None and len(df2) > 0:
		df = df2
	else:
		df = None
	return df

def human_format(num):
	if not resources.default().numeric_to_human_format:
		return num
	try:
		if abs(num) < 1000:
			return num
		num = float('{:.3g}'.format(num))
		magnitude = 0
		while abs(num) >= 1000:
			magnitude += 1
			num /= 1000.0
		return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
	except Exception:
		return num
