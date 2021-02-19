import pandas as pd
from bs4 import BeautifulSoup

from nseta.scanner.baseStockScanner import baseStockScanner
from nseta.common.urls import TICKERTAPE_NEWS_URL
from nseta.common.commons import ParseNews
from nseta.common.log import tracelog, default_logger

__all__ = ['stockNewsScanner']

class stockNewsScanner(baseStockScanner):
	def __init__(self, indicator='all'):
		super().__init__(indicator=indicator)

	@tracelog
	def scan_quanta(self, **kwargs):
		stocks = kwargs['items']
		frames = []
		signalframes = []
		df = None
		signaldf = None
		for symbol in stocks:
			try:
				self.update_progress(symbol)
				resp = TICKERTAPE_NEWS_URL(symbol.upper())
				bs = BeautifulSoup(resp.text, 'lxml')
				news = ParseNews(soup=bs)
				news.parse_news(symbol.upper())
				df = pd.DataFrame(news.news_list, columns=['Symbol', 'h', 'Hours_ago','Publisher', 'Headline'])
				if df is not None and len(df) > 0:
					signalframes.append(df)
					default_logger().debug(df.to_string(index=False))
			except Exception as e:
				default_logger().debug("Exception encountered for " + symbol)
				default_logger().debug(e, exc_info=True)
			except SystemExit:
				sys.exit(1)
		if len(signalframes) > 0:
			signaldf = pd.concat(signalframes)
		return [df, signaldf]

