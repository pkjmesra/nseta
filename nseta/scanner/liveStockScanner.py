import pandas as pd
import talib as ta

from nseta.live.live import get_live_quote
from nseta.resources.resources import *
from nseta.scanner.baseStockScanner import baseStockScanner
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger

__all__ = ['liveStockScanner']

class liveStockScanner(baseStockScanner):
	def __init__(self, indicator='all'):
		super().__init__(indicator=indicator)
		self._keys = ['symbol','previousClose', 'lastPrice', 'deliveryToTradedQuantity', 'BuySellDiffQty', 'totalTradedVolume', 'pChange', 'FreeFloat']

	@property
	def keys(self):
		return self._keys

	@tracelog
	def scan_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		df = None
		signaldf = None
		for stock in stocks:
			try:
				self.update_progress(stock)
				result, primary = get_live_quote(stock, keys = self.keys)
				if primary is not None and len(primary) > 0:
					row = pd.DataFrame(primary, columns = ['Updated', 'Symbol', 'Close', 'LTP', '% Delivery', 'Buy - Sell', 'TotalTradedVolume', 'pChange', 'FreeFloat'], index = [''])
					value = (row['LTP'][0]).replace(' ','').replace(',','')
					if stock in self.stocksdict:
						(self.stocksdict[stock]).append(float(value))
					else:
						self.stocksdict[stock] = [float(value)]
					index = len(self.stocksdict[stock])
					if index >= 15:
						dfclose = pd.DataFrame(self.stocksdict[stock], columns = ['Close'])
						rsi = ta.RSI(dfclose['Close'],resources.rsi().period)
						rsivalue = rsi[index -1]
						row['RSI'] = rsivalue
						default_logger().debug(stock + " RSI:" + str(rsi))
						if rsivalue > resources.rsi().upper or rsivalue < resources.rsi().lower:
							signalframes.append(row)
					frames.append(row)
			except Exception as e:
				default_logger().debug("Exception encountered for " + stock)
				default_logger().debug(e, exc_info=True)
		if len(frames) > 0:
			df = pd.concat(frames)
			# default_logger().debug(df.to_string(index=False))
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
			# default_logger().debug(signaldf.to_string(index=False))
		return [df, signaldf]
