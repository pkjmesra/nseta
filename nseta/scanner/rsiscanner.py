import os
import os.path
from os import path

import pandas as pd

from nseta.live.live import get_live_quote
from nseta.common.log import logdebug, default_logger
import talib as ta

__all__ = ['scanner']

class scanner:
	def __init__(self, scan_intraday=False):
		self._intraday = scan_intraday
		self._stocksdict = {}
		self._keys = ['symbol','previousClose', 'lastPrice']

	@property
	def keys(self):
		return self._keys

	@property
	def intraday(self):
		return self._intraday

	@intraday.setter
	def intraday(self, value):
		self._intraday = value

	@property
	def stocksdict(self):
		return self._stocksdict

	def scan(self, stocks=[], start_date=None, end_date=None):
		dir_path = ""
		if not path.exists("stocks.py"):
			dir_path = os.path.dirname(os.path.realpath(__file__)) + "/"
		# If stocks array is empty, pull stock list from stocks.txt file
		stocks = stocks if len(stocks) > 0 else [
			line.rstrip() for line in open(dir_path + "stocks.py", "r")]
		# Time frame you want to pull data from
		# start_date = datetime.datetime.now()-datetime.timedelta(days=365)
		# end_date = datetime.datetime.now()
		frames = []
		for stock in stocks:
			try:
				result, primary = get_live_quote(stock, keys = self.keys)
				row = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP'], index = [''])
				value = (row['LTP'][0]).replace(' ','').replace(',','')
				if stock in self.stocksdict:
					(self.stocksdict[stock]).append(float(value))
				else:
					self.stocksdict[stock] = [float(value)]
				index = len(self.stocksdict[stock])
				if index >= 15:
					dfclose = pd.DataFrame(self.stocksdict[stock], columns = ['Close'])
					rsi = ta.RSI(dfclose['Close'],14)
					row['RSI'] = rsi[index -1]
				frames.append(row)
			except Exception as e:
				default_logger().error("Exception encountered for " + stock)
				default_logger().error(e, exc_info=True)
				pass
		df = pd.concat(frames).to_string(index=False)
		print(df)
