# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 22:01:01 2020

@author: SW274998
"""
import click
import numpy as np
from nseta.common.commons import *
from nseta.common.log import tracelog, default_logger
from nseta.live.liveurls import quote_eq_url, futures_chain_url, holiday_list_url

import json
from bs4 import BeautifulSoup
from datetime import datetime, date, timedelta

__all__ = ['get_data_list','get_live_quote']

OPTIONS_CHAIN_SCHEMA = [str, int, int, int, float, float, float, int, float, float, int,
						float,
						int, float, float, int, float, float, float, int, int, int, str]
OPTIONS_CHAIN_HEADERS = ["Call Chart", "Call OI", "Call Chng in OI", "Call Volume", "Call IV", "Call LTP", "Call Net Chng", "Call Bid Qty", "Call Bid Price", "Call Ask Price", "Call Ask Qty",
						 "Strike Price",
						 "Put Bid Qty", "Put Bid Price", "Put Ask Price", "Put Ask Qty", "Put Net Chng", "Put LTP", "Put IV", "Put Volume", "Put Chng in OI", "Put OI", "Put Chart"]
OPTIONS_CHAIN_INDEX = "Strike Price"

FUTURES_SCHEMA = [str, str, StrDate.default_format(
	format="%d%b%Y"), str, str, float, float, float, float, float, int, float, float]
FUTURES_HEADERS = ["Instrument", "Underlying", "Expiry Date", "Option Type", "Strike Price", "Open Price", "High Price", "Low Price", "Prev. Close", "Last Price", "Volume",
				   "Turnover", "Underlying Value"]
FUTURES_INDEX = "Expiry Date"

NAME_KEYS = ['symbol','companyName', 'isinCode']
QUOTE_KEYS = ['previousClose', 'lastPrice', 'change', 'pChange', 'averagePrice', 'pricebandupper', 'pricebandlower', 'basePrice']
OHLC_KEYS = ['open', 'dayHigh', 'dayLow', 'closePrice']
WK52_KEYS = ['high52', 'low52']
VOLUME_KEYS = ['quantityTraded', 'totalTradedVolume', 'totalTradedValue', 'deliveryQuantity', 'deliveryToTradedQuantity', 'totalBuyQuantity', 'totalSellQuantity', 'cm_ffm', 'faceValue']


eq_quote_referer = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuote.jsp?symbol={}&illiquid=0&smeFlag=0&itpFlag=0"
derivative_quote_referer = "https://www1.nseindia.com/live_market/dynaContent/live_watch/get_quote/GetQuoteFO.jsp?underlying={}&instrument={}&expiry={}&type={}&strike={}"
option_chain_referer = "https://www1.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=-9999&symbol=NIFTY&symbol=BANKNIFTY&instrument=OPTIDX&date=-&segmentLink=17&segmentLink=17"

@tracelog
def get_quote(symbol, series='EQ', instrument=None, expiry=None, option_type=None, strike=None):
	"""
	1. Underlying security (stock symbol or index name)
	2. instrument (FUTSTK, OPTSTK, FUTIDX, OPTIDX)
	3. expiry (ddMMMyyyy)
	4. type (CE/PE for options, - for futures
	5. strike (strike price upto two decimal places
	"""
	if instrument:
		print('Not supported yet')
	else:
		quote_eq_url.session.headers.update(
			{'Referer': eq_quote_referer.format(symbol)})
		res = quote_eq_url(symbol.replace('&','%26'), series)

	html_soup = BeautifulSoup(res.text, 'lxml')
	hresponseDiv = html_soup.find("div", {"id": "responseDiv"})
	d = json.loads(hresponseDiv.get_text())
	#d = json.loads(res.text)['data'][0]
	res = {}
	for k in d.keys():
		v = d[k]
		try:
			v_ = None
			if v.find('.') > 0:
				v_ = float(v.strip().replace(',', ''))
			else:
				v_ = int(v.strip().replace(',', ''))
		except Exception:
			v_ = v
		except SystemExit:
			pass
		res[k] = v_
	return res

@tracelog
def get_futures_chain(symbol):
	r = futures_chain_url(symbol)
	return r

@tracelog
def get_futures_chain_table(symbol):
	futuresscrape = get_futures_chain(symbol)
	html_soup = BeautifulSoup(futuresscrape.text, 'html.parser')
	spdiv = html_soup.find("div", {"id": "tab26Content"})
	sptable = spdiv.find("table")
	tp = ParseTables(soup=sptable, schema=FUTURES_SCHEMA,
					 headers=FUTURES_HEADERS, index=FUTURES_INDEX)
	return tp.get_df()

@tracelog
def get_holidays_list(fromDate,
					  toDate):
	"""This is the function to get exchange holiday list between 2 dates.
		Args:
			fromDate (datetime.date): start date
			toDate (datetime.date): end date
		Returns:
			pandas.DataFrame : A pandas dataframe object
		Raises:
			ValueError:
						1. From Date param is greater than To Date param
	"""
	if fromDate > toDate:
		raise ValueError('Please check start and end dates')

	holidayscrape = holiday_list_url(fromDate.strftime(
		"%d-%m-%Y"), toDate.strftime("%d-%m-%Y"))
	html_soup = BeautifulSoup(holidayscrape.text, 'lxml')
	sptable = html_soup.find("table")
	tp = ParseTables(soup=sptable,
					 schema=[str, StrDate.default_format(
						 format="%d-%b-%Y"), str, str],
					 headers=["Market Segment", "Date", "Day", "Description"], index="Date")
	dfret = tp.get_df()
	dfret = dfret.drop(["Market Segment"], axis=1)
	return dfret

@tracelog
def getworkingdays(dtfrom, dtto):
	# pdb.set_trace()
	dfholiday = get_holidays_list(dtfrom, dtto)
	stalldays = set()
	stweekends = set()

	for i in range((dtto - dtfrom).days + 1):
		dt = dtfrom + timedelta(days=i)
		stalldays.add(dt)

		if dt.isoweekday() in (6, 7):
			stweekends.add(dt)

	# pdb.set_trace()
	stspecial  = set(
	  [date(2020,2,1) # Budget day
	  ]
	)

	#Remove special weekend working days from weekends set
	stweekends -= stspecial
	stworking = (stalldays - stweekends) - set(dfholiday.index.values)
	# stworking = (stalldays - stweekends) - set(dfholiday.index.values)

	# #Special cases where market was open on weekends
	# stspecial  = set(
	  # [datetime.date(2020,2,1) # Budget day
	  # ]
	# )
	# for dtspecial in stspecial:
	  # if (dtspecial >= dtfrom and dtspecial <= dtto):
		# stworking.add(dtspecial)

	return sorted(stworking)

@tracelog
def get_live_quote(symbol, general=True, ohlc=False, wk52=False, volume=False, orderbook=False, keys=[]):
	result = get_quote(symbol)
	# print(result)
	if len(result['data']) == 0:
		default_logger().warn('Wrong or invalid inputs.')
		click.secho("Please check the inputs. Could not fetch the data for {}".format(symbol), fg='red', nl=True)
		return None, None
	primary = format_as_dataframe(result, symbol, general, ohlc, wk52, volume, keys= keys)
	return result, primary

def format_as_dataframe(orgdata, symbol, general, ohlc, wk52, volume, keys=[]):
	primary, name_data, quote_data, ohlc_data, wk52_data, volume_data, pipeline_data = get_data_list(orgdata, keys=keys)
	return primary

def get_data_list(orgdata, keys=[]):
	data = orgdata['data'][0]
	time = orgdata['lastUpdateTime']

	name_data = []
	quote_data = []
	ohlc_data = []
	wk52_data = []
	volume_data = []
	pipeline_data = []
	if len(keys) > 0:
		primary = [time]
		for key in keys:
			if key in data.keys():
				primary.append(data[key])
			elif key == 'FreeFloat':
				try:
					freeFloatMarketCapInCr = float((data['cm_ffm']).replace(' ','').replace(',','')) * 10000000
					faceValue = float((data['faceValue']).replace(' ','').replace(',',''))
					primary.append(int(freeFloatMarketCapInCr/faceValue))
				except Exception as e:
					default_logger().debug(e, exc_info=True)
					primary.append(np.nan)
					continue
			elif key == 'BuySellDiffQty':
				try:
					totalBuyQuantity = float((data['totalBuyQuantity']).replace(' ','').replace(',',''))
					totalSellQuantity = float((data['totalSellQuantity']).replace(' ','').replace(',',''))
					primary.append(float(totalBuyQuantity - totalSellQuantity))
				except Exception as e:
					default_logger().debug(e, exc_info=True)
					primary.append(np.nan)
					continue
		default_logger().debug('\nPrimary:\n{}'.format(primary))

		return [primary], name_data, quote_data, ohlc_data, wk52_data, volume_data, pipeline_data
	else:
		primary = []
		for key in NAME_KEYS:
			name_data.append(data[key])
			primary.append(data[key])
		name_data = [name_data]

		quote_data.append(time)
		primary.append(time)
		for key in QUOTE_KEYS:
			value = (data[key]).replace(' ','').replace(',','')
			quote_data.append(float(value))
			primary.append(float(value))
		quote_data = [quote_data]

		for key in OHLC_KEYS:
			value = (data[key]).replace(' ','').replace(',','')
			ohlc_data.append(float(value))
		ohlc_data = [ohlc_data]

		for key in WK52_KEYS:
			value = (data[key]).replace(' ','').replace(',','')
			wk52_data.append(float(value))
		wk52_data = [wk52_data]

		for key in VOLUME_KEYS:
			try:
				value = float((data[key]).replace(' ','').replace(',',''))
				volume_data.append('{} cr'.format(round(value/10000000,2)) if value > 10000000 else value)
			except Exception:
				volume_data.append(np.nan)
				continue
		try:
			totalBuyQuantity = float((data['totalBuyQuantity']).replace(' ','').replace(',',''))
		except Exception:
			totalBuyQuantity = np.nan
		try:
			totalSellQuantity = float((data['totalSellQuantity']).replace(' ','').replace(',',''))
		except Exception:
			totalSellQuantity = np.nan
		try:
			volume_data.append(float(totalBuyQuantity - totalSellQuantity))
		except Exception:
			volume_data.append(np.nan)
		
		freeFloatMarketCapInCr = float((data['cm_ffm']).replace(' ','').replace(',','')) * 10000000
		faceValue = float((data['faceValue']).replace(' ','').replace(',',''))
		freefloat = int(freeFloatMarketCapInCr/faceValue)
		volume_data.append('{} cr'.format(round(freefloat/10000000,2)) if freefloat > 10000000 else freefloat)

		volume_data = [volume_data]

		for x in range(1,5):
			buy_qty_key = 'buyQuantity' + str(x)
			buy_prc_key = 'buyPrice' + str(x)
			sell_qty_key = 'sellQuantity' + str(x)
			sell_prc_key = 'sellPrice' + str(x)
			columns = [buy_qty_key, buy_prc_key, sell_qty_key, sell_prc_key]
			row = []
			for column in columns:
				row.append(data[column] + "  ")
			pipeline_data.append(row)
		row = []
		row.append('Total Buy Quantity:')
		row.append('{}'.format(str(totalBuyQuantity)))
		row.append('Total Sell Quantity:')
		row.append('{}'.format(str(totalSellQuantity)))
		pipeline_data.append(row)
		return [primary], name_data, quote_data, ohlc_data, wk52_data, volume_data, pipeline_data
