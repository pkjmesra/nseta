import pandas as pd
import numpy as np

from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction
from nseta.strategy.simulatedorder import simulatedorder, OrderType
from nseta.strategy.basesignalstrategy import basesignalstrategy

__all__ = ['macdSignalStrategy']

class macdSignalStrategy(basesignalstrategy):
	def __init__(self, strict=False, intraday=False):
		super().__init__()
		# Cross over above zero line for buy or below zero line for sell
		self._strict = strict
		self._prc = 0
		self._order_queue = simulatedorder(OrderType.MIS if intraday else OrderType.Delivery)
		self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Pattern':[],'Direction':[], 'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[]}

	@tracelog
	def test_strategy(self, df):
		# TODO: What if keys are in lowercase or dt/datetime is used instead of date/Date
		try:
			rowindex = 0
			df = df.dropna()
			for macd in (df['macd(12)']).values:
				if macd is not None:
					price =(df.iloc[rowindex])['Close']
					ts =(df.iloc[rowindex])['Date']
					self.index(macd, price, ts)
				rowindex = rowindex + 1
			default_logger().debug("\n{}\n".format(self.basereport.to_string(index=False)))
			if self.order_queue.holdings_size < 0:
				buy_sell = 'BUY'
			elif self.order_queue.holdings_size > 0:
			 	buy_sell = 'SELL'
			else:
			 	buy_sell = 'SQR-OFF'
			self.order_queue.square_off(self.price)
			self.update_ledger(buy_sell)
			self.pnl = self.order_queue.pnl
			df_summary_dict = {'Symbol':[df['Symbol'].iloc[0]], 'Strategy':['MACD'], 'PnL':[self.pnl], 'Recommendation': [str(self.recommendation)]}
			df_summary = pd.DataFrame(df_summary_dict)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
		return self.report, df_summary

	@tracelog
	def index(self, macd, price, timestamp):
		if macd != np.nan:
			self.price = price
			super().index(macd, timestamp)

	@property
	def strict(self):
		return self._strict

	@property
	def order_queue(self):
		return self._order_queue

	@property
	def ledger(self):
		return self._ledger

	@property
	def report(self):
		return pd.DataFrame(self.ledger)

	@property
	def price(self):
		return self._prc

	@price.setter
	def price(self, prc):
		self._prc = prc

	def update_direction(self):
		super().update_direction()

	@tracelog
	def v_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size <= 0:
		self.buy_signal()
	
	@tracelog
	def invertedv_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size > 0:
		self.sell_signal()

	@tracelog
	def possibleReversalUpward_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size <= 0:
		self.buy_signal()

	@tracelog
	def possibleReversalDownward_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size > 0:
		self.sell_signal()

	def possible_higherhigh_pattern(self, prev_pattern=Direction.Neutral):
		# holding_size = self.order_queue.holdings_size
		# if holding_size <= 0:
		self.buy_signal()

	def lowerlow_direction(self, prev_pattern=Direction.Neutral):
		# holding_size = self.order_queue.holdings_size
		# if holding_size > 0:
		self.sell_signal()

	@tracelog
	def buy_signal(self):
		holding_size = self.order_queue.holdings_size
		self.order_queue.buy(self.price)
		# Last request was honoured
		if holding_size != self.order_queue.holdings_size:
			self.update_ledger('BUY')
		default_logger().debug("\n{}".format(pd.DataFrame(self.ledger)))

	@tracelog
	def sell_signal(self):
		holding_size = self.order_queue.holdings_size
		self.order_queue.sell(self.price)
		if holding_size != self.order_queue.holdings_size:
			self.update_ledger('SELL')
		default_logger().debug("\n{}".format(pd.DataFrame(self.ledger)))

	@tracelog
	def update_ledger(self, signal):
		(self.ledger['DateTime']).append(self.timestamp)
		(self.ledger['Signal']).append(signal)
		(self.ledger['Price']).append(str(self.price))
		(self.ledger['Pattern']).append(str(self.pattern))
		(self.ledger['Direction']).append(str(self.direction))
		(self.ledger['Funds']).append(str(round(self.order_queue.funds,2)))
		(self.ledger['Order_Size']).append(str(round(self.order_queue.order_size,2)))
		(self.ledger['Holdings_Size']).append(str(round(self.order_queue.holdings_size,2)))
		(self.ledger['Portfolio_Value']).append(str(round(self.order_queue.portfolio_value,2)))
