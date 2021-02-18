# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 20:35:13 2015

@author: SW274998
"""

from nseta.common.commons import URLFetch
from nseta.common.constants import symbol_count
from nseta.common.log import tracelog

from requests import Session
from functools import partial
from cachecontrol import CacheControl

__all__ = ['daily_deliverypositions_url','derivative_expiry_dates_url','derivative_history_url','derivative_price_list_url','index_daily_snapshot_url','index_history_url','index_vix_history_url','daily_volatility_url','nse_intraday_url_new','NSE_SYMBOL_COUNT_URL', 'symbol_count_url', 'get_symbol_count', 'equity_history_url_full', 'equity_history_url', 'price_list_url', 'pr_price_list_zipped_url', 'equity_symbol_list_url', 'index_pe_history_url', 'nse_intraday_url']

session = CacheControl(Session())
# headers = {
	# 'Host': 'www1.nseindia.com',
	# 'Referer': 'https://www1.nseindia.com/products/content/equities/equities/eq_security.htm'}

headers = {'Accept': '*/*',
		   'Accept-Encoding': 'gzip, deflate, br',
		   'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
		   'Connection': 'keep-alive',
		   'Host': 'www1.nseindia.com',
		   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
		   'Upgrade-Insecure-Requests': '1',
		   'Sec-Fetch-Site': 'none',
		   'Sec-Fetch-Mode': 'navigate',
		   'Sec-Fetch-Dest': 'document',
		   'X-Requested-With': 'XMLHttpRequest'}

URLFetchSession = partial(URLFetch, session=session,
						  headers=headers)

NSE_SYMBOL_COUNT_URL = 'http://www1.nseindia.com/marketinfo/sym_map/symbolCount.jsp'

TICKERTAPE_NEWS_URL = URLFetchSession(
	url='https://stocks.tickertape.in/%s?broker=kite&theme=default')
# Periodicity= 1 : Every 1 minute
# Periodicity= 2 : Every 5 minutes
# Periodicity= 3 : Every 15 minutes
# Periodicity= 4 : Every 30 minutes
# Periodicity= 5 : Every 1 hour
# PeriodType=1: Weekly data from the beginning of the trading years
# PeriodType=2/3: Daily data for a given periodicity
nse_intraday_url_full = URLFetchSession(
	url= 'https://www1.nseindia.com/ChartApp/install/charts/data/GetHistoricalNew.jsp',method='post')#'https://www1.nseindia.com/charts/webtame/tame_intraday_getQuote_closing_redgreen.jsp')
"""
New NSE URL: https://www.nseindia.com/api/chart-databyindex?index=SBINEQN
For Stocks, index={Symbol}NEQN. See https://www.nseindia.com/tcharts/04jan2020?index=NIFTY%2050
Segment=CM&Series=EQ&CDExpiryMonth=&FOExpiryMonth=&IRFExpiryMonth=&CDDate1=&CDDate2=&Template=tame_intraday_getQuote_closing_redgreen.jsp&CDSymbol=%s&Periodicity=1&PeriodType=2
"""
nse_intraday_url = partial(nse_intraday_url_full,
							Instrument='FUTSTK',
							Segment='CM', Series='EQ', CDExpiryMonth="", FOExpiryMonth="",
							IRFExpiryMonth="",CDDate1="",CDDate2="",
							Template="tame_intraday_getQuote_closing_redgreen.jsp",
							PeriodType="2", ct0='g1|1|1', ct1='g2|2|1',ctcount='2')

nse_intraday_url_new = URLFetchSession(
	url='https://www.nseindia.com/api/chart-databyindex')

"""
---------------------------------EQUITY--------------------------------------
"""
symbol_count_url = URLFetchSession(
	url='http://www1.nseindia.com/marketinfo/sym_map/symbolCount.jsp')

@tracelog
def get_symbol_count(symbol, force_refresh=False):
	try:
		return fetch_fresh_symbol_count(symbol) if force_refresh else symbol_count[symbol]
	except Exception:
		return fetch_fresh_symbol_count(symbol)
	except SystemExit:
		pass


def fetch_fresh_symbol_count(symbol):
	cnt = symbol_count_url(symbol=symbol).text.lstrip().rstrip()
	symbol_count[symbol] = cnt
	return cnt

"""
# http://www1.nseindia.com/products/dynaContent/common/productsSymbolMapping.jsp?symbol=SBIN&segmentLink=3&symbolCount=1&series=EQ&dateRange=1month&fromDate=2020-12-01&toDate=2020-12-25&dataType=PRICEVOLUMEDELIVERABLE'
"""
equity_history_url_full = URLFetchSession(
	url='http://www1.nseindia.com/products/dynaContent/common/productsSymbolMapping.jsp')

"""
symbol="SBIN"
symbolCount=get_symbol_count(SBIN)
series="EQ"
fromDate="dd-mm-yyyy"
toDate="dd-mm-yyyy"
dd = equity_history_url(symbol='SBIN', series="EQ", fromDate="01-01-2017", toDate="01-01-2017")
"""
equity_history_url = partial(equity_history_url_full,
							 dataType='PRICEVOLUMEDELIVERABLE',
							 segmentLink=3, dateRange="")

"""
1. YYYY
2. MMM
3. ddMMMyyyy
"""
price_list_url = URLFetchSession(
	url='https://www1.nseindia.com/content/historical/EQUITIES/%s/%s/cm%sbhav.csv.zip')

"""
1. ddmmyyyy
"""
daily_volatility_url = URLFetchSession(
	url='http://www1.nseindia.com/archives/nsccl/volt/CMVOLT_%s.CSV')

"""
1. ddmmyyyy
"""
daily_deliverypositions_url = URLFetchSession(
	url='https://www1.nseindia.com/archives/equities/mto/MTO_%s.DAT')


"""
1. ddmmyy
"""
pr_price_list_zipped_url = URLFetchSession(
	url='http://www1.nseindia.com/archives/equities/bhavcopy/pr/PR%s.zip')


"""
--------------------------INDICES---------------------------------------
"""
"""
1. indexType=index name
2. fromDate string dd-mm-yyyy
3. toDate string dd-mm-yyyy
"""
index_history_url = URLFetchSession(
	url='http://www1.nseindia.com/products/dynaContent/equities/indices/historicalindices.jsp')

"""
1. ddmmyyyy
"""
index_daily_snapshot_url = URLFetchSession(
	url='https://archives.nseindia.com/content/indices/ind_close_all_%s.csv')

"""
indexName=NIFTY%2050&fromDate=02-11-2015&toDate=19-11-2015&yield1=undefined&yield2=undefined&yield3=undefined&yield4=all
indexName = Index name
fromDate = from date dd-mm-yyyy
toDate = to Date dd-mm-yyyy
"""
index_pe_history_url = partial(
	URLFetchSession(
		url='http://www1.nseindia.com/products/dynaContent/equities/indices/historical_pepb.jsp?'),
	yield1="undefined",
	yield2="undefined",
	yield3="undefined",
	yield4="all")
"""
http://www1.nseindia.com/products/dynaContent/equities/indices/hist_vix_data.jsp?&fromDate=01-Nov-2015&toDate=19-Nov-2015
fromDate = 'dd-Mmm-yyyy'
toDate = 'dd-Mmm-yyyy'
"""
index_vix_history_url = URLFetchSession(
	url='http://www1.nseindia.com/products/dynaContent/equities/indices/hist_vix_data.jsp')

equity_symbol_list_url = URLFetchSession(
	url='https://www1.nseindia.com/content/equities/EQUITY_L.csv')

index_constituents_url = URLFetchSession(
	"https://www1.nseindia.com/content/indices/ind_%slist.csv")

"""
--------------------------DERIVATIVES---------------------------------------
"""
derivative_expiry_dates_url = URLFetchSession(
	url='http://www1.nseindia.com/products/resources/js/foExp.js')

"""
instrumentType=FUTIDX
symbol=NIFTY
expiryDate=26-11-2015
optionType=select
strikePrice=
dateRange=15days
fromDate= 01-Nov-2015
toDate=19-Nov-2015
segmentLink=9&
symbolCount=
"""
derivative_history_url = partial(
	URLFetchSession(
		url='http://www1.nseindia.com/products/dynaContent/common/productsSymbolMapping.jsp?',
		headers = {**headers, **{'Referer': 'https://www1.nseindia.com/products/content/derivatives/equities/historical_fo.htm'}}
		#headers = (lambda a,b: a.update(b) or a)(headers.copy(),{'Referer': 'https://www1.nseindia.com/products/content/derivatives/equities/historical_fo.htm'})
		),
	segmentLink=9,
	symbolCount='')
"""
http://www1.nseindia.com/content/historical/DERIVATIVES/2015/NOV/fo18NOV2015bhav.csv.zip
1.year yyyy
2.Month MMM
3.date ddMMMyyyy

"""
derivative_price_list_url = URLFetchSession(
	url="http://www1.nseindia.com/content/historical/DERIVATIVES/%s/%s/fo%sbhav.csv.zip")


"""
--------------------------CURRENCY---------------------------------------
"""
"""
fromDate dd-mm-yyyy (from date)
toDate dd-mm-yyyy (to date)
"""
rbi_rate_history_url = URLFetchSession(
	"https://www1.nseindia.com/products/dynaContent/derivatives/currency/fxRbiRateHist.jsp")
