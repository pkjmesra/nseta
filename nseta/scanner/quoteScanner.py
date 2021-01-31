import threading, time
import click
import pandas as pd
from nseta.live.live import get_quote, get_live_quote, get_data_list
from nseta.scanner.baseScanner import baseScanner
from nseta.common.tradingtime import IST_datetime
from nseta.resources.resources import resources
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger

__all__ = ['quoteScanner']

NAME_LIST = ['Symbol', 'Name', 'ISIN']
QUOTE_LIST = ['Last Updated', 'Prev Close', 'Last Trade Price','Change','% Change', 'Avg. Price', 'Upper Band','Lower Band', 'Adjusted Price']
OHLC_LIST = ['Open', 'High', 'Low', 'Close']
WK52_LIST = ['52 Wk High', '52 Wk Low']
VOLUME_LIST = ['Quantity Traded', 'Total Traded Volume', 'Total Traded Value', 'Delivery Volume', '% Delivery', 'Total Buy Qty.', 'Total Sell Qty.', 'FF Market Cap(cr)', 'Face Value', 'Buy - Sell', 'Free Float']
PIPELINE_LIST = ['Bid Quantity', 'Bid Price', 'Offer_Quantity', 'Offer_Price']

class quoteScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator, background)
		self.response_type = ResponseType.Quote

	@tracelog
	def scan(self, symbol, general, ohlc, wk52, volume, orderbook, background):
		global RUN_IN_BACKGROUND
		try:
			if background:
				b = threading.Thread(name='live_quote_background', target=self.live_quote_background, args=[symbol, general, ohlc, wk52, volume, orderbook], daemon=True)
				b.start()
				b.join()
			else:
				orgdata, df = get_live_quote(symbol, general, ohlc, wk52, volume, orderbook)
				self.format_beautified(orgdata, general, ohlc, wk52, volume, orderbook)
		except Exception as e:
			RUN_IN_BACKGROUND = False
			default_logger().debug(e, exc_info=True)
			click.secho('Failed to fetch live quote', fg='red', nl=True)
			return
		except SystemExit:
			RUN_IN_BACKGROUND = False
			return

	@tracelog
	def live_quote_background(self, symbol, general, ohlc, wk52, volume, orderbook, terminate_after_iter=0, wait_time=resources.scanner().background_scan_frequency_quotes):
		global RUN_IN_BACKGROUND
		RUN_IN_BACKGROUND = True
		iteration = 0
		while RUN_IN_BACKGROUND:
			iteration = iteration + 1
			if terminate_after_iter > 0 and iteration >= terminate_after_iter:
				RUN_IN_BACKGROUND = False
				break
			result = get_quote(symbol)
			self.format_beautified(result, general, ohlc, wk52, volume, orderbook)
			time.sleep(wait_time)
		click.secho('Finished all iterations of scanning live quotes.', fg='green', nl=True)
		return iteration

	def format_beautified(self, orgdata, general, ohlc, wk52, volume, orderbook):
		primary, name_data, quote_data, ohlc_data, wk52_data, volume_data, pipeline_data = get_data_list(orgdata)
		frames = []
		if general:
			frames = self.add_frame(frames, name_data, NAME_LIST)
		frames = self.add_frame(frames, quote_data, QUOTE_LIST)
		if ohlc:
			frames = self.add_frame(frames, ohlc_data, OHLC_LIST)
		if wk52:
			frames = self.add_frame(frames, wk52_data, WK52_LIST)
		if volume:
			frames = self.add_frame(frames, volume_data, VOLUME_LIST)
		click.secho('------------------------------------------', fg='green', nl=True)
		print('As of {}\n'.format(IST_datetime()))
		click.echo(pd.concat(frames).to_string(index=True))
		if orderbook:
			dfpipeline = self.formatted_dataframe(pipeline_data, PIPELINE_LIST, indices=False)
			print('\n')
			click.echo(dfpipeline.to_string(index=False))
		click.secho('------------------------------------------', fg='red', nl=True)

	def format_column(self, columnname, width):
		return columnname.ljust(width) + "|"

	def add_frame(self, frames, list_data, column_names, should_transpose=True):
		df = self.formatted_dataframe(list_data, column_names)
		frames.append(df.transpose() if should_transpose else df)
		return frames

	def formatted_dataframe(self, list_data, column_names, indices=True):
		columns =[]
		for column in column_names:
			columns.append(self.format_column(column,20))
		if indices:
			df = pd.DataFrame(list_data, columns = columns, index = [''])
		else:
			df = pd.DataFrame(list_data, columns = columns)
		return df
