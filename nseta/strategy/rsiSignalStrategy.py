import logging
import pandas as pd

from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction, Recommendation
from nseta.resources.resources import *
from nseta.strategy.simulatedorder import simulatedorder, OrderType
from nseta.strategy.basesignalstrategy import basesignalstrategy

__all__ = ['rsiSignalStrategy']

class rsiSignalStrategy(basesignalstrategy):
	def __init__(self, strict=False, intraday=False, requires_ledger=False):
		super().__init__(requires_ledger=requires_ledger)
		self._strict = strict
		self._prc = 0
		self._lower = resources.rsi().lower
		self._upper = resources.rsi().upper
		self._order_queue = simulatedorder(OrderType.MIS if intraday else OrderType.Delivery)
		if default_logger().level == logging.DEBUG:
			self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Pattern':[],'Direction':[], 'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[], 'P3':[], 'P2':[], 'P1':[], 'N1':[], 'N2':[], 'N3':[],'P-delta':[], 'N-delta':[], 'Base-delta':[]}
		else:
			self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Pattern':[],'Direction':[], 'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[]}

	@tracelog
	def set_limits(self, lower, upper):
		self._lower = lower
		self._upper = upper

	@tracelog
	def test_strategy(self, df):
		# TODO: What if keys are in lowercase or dt/datetime is used instead of date/Date
		try:
			rowindex = 0
			for rsi in (df['RSI']).values:
				if rsi is not None:
					price =(df.iloc[rowindex])['Close']
					ts =(df.iloc[rowindex])['Date']
					self.index(rsi, price, ts)
				rowindex = rowindex + 1
			if self.order_queue.holdings_size < 0:
				buy_sell = 'BUY'
			elif self.order_queue.holdings_size > 0:
			 	buy_sell = 'SELL'
			else:
			 	buy_sell = 'SQR-OFF'
			self.order_queue.square_off(self.price)
			self.update_ledger(buy_sell)
			self.pnl = self.order_queue.pnl
			df_summary_dict = {'Symbol':[df['Symbol'].iloc[0]], 'Strategy':['RSI'], 'PnL':[self.pnl], 'Recommendation': [str(self.recommendation.name)]}
			df_summary = pd.DataFrame(df_summary_dict)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
		return self.report, df_summary

	@tracelog
	def index(self, rsi, price, timestamp):
		if rsi > 0:
			self.price = price
			super().index(rsi, timestamp)

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
	def lower(self):
		return self._lower

	@property
	def upper(self):
		return self._upper

	@property
	def price(self):
		return self._prc

	@price.setter
	def price(self, prc):
		self._prc = prc

	def update_direction(self):
		if self.n3 >= self.upper:
			self.direction = Direction.Up
			self.pattern = Direction.OverBought
			self.sell_signal()

		if self.n3 <= self.lower:
			self.direction = Direction.Down
			self.pattern = Direction.OverSold
			self.buy_signal()
		super().update_direction()

	def v_pattern(self, prev_pattern=Direction.Neutral):
		if self.n3 >= 55:
			self.recommendation = Recommendation.Buy
			self.buy_signal()
		else:
			self.recommendation = Recommendation.Hold

	def invertedv_pattern(self, prev_pattern=Direction.Neutral):
		self.sell_signal()

	def higherhigh_pattern(self, prev_pattern=Direction.Neutral):
		if not self.strict and self.n3 >= 55:
			self.recommendation = Recommendation.Buy
			self.buy_signal()
		else:
			self.recommendation = Recommendation.Hold

	def lowerlow_direction(self, prev_pattern=Direction.Neutral):
		if not self.strict:
			self.sell_signal()

	def buy_signal(self):
		holding_size = self.order_queue.holdings_size
		self.order_queue.buy(self.price)
		# Last request was honoured
		if holding_size != self.order_queue.holdings_size:
			self.update_ledger('BUY')
		default_logger().debug("\n{}".format(pd.DataFrame(self.ledger)))

	def sell_signal(self):
		holding_size = self.order_queue.holdings_size
		self.order_queue.sell(self.price)
		if holding_size != self.order_queue.holdings_size:
			self.update_ledger('SELL')
		default_logger().debug("\n{}".format(pd.DataFrame(self.ledger)))

	@tracelog
	def update_ledger(self, signal):
		if not self.requires_ledger:
			return
		(self.ledger['DateTime']).append(self.timestamp)
		(self.ledger['Signal']).append(signal)
		(self.ledger['Price']).append(str(self.price))
		(self.ledger['Pattern']).append(str(self.pattern))
		(self.ledger['Direction']).append(str(self.direction))
		(self.ledger['Funds']).append(str(round(self.order_queue.funds,2)))
		(self.ledger['Order_Size']).append(str(round(self.order_queue.order_size,2)))
		(self.ledger['Holdings_Size']).append(str(round(self.order_queue.holdings_size,2)))
		(self.ledger['Portfolio_Value']).append(str(round(self.order_queue.portfolio_value,2)))
		if default_logger().level == logging.DEBUG:
			(self.ledger['P3']).append(str(round(self.p3,2)))
			(self.ledger['P2']).append(str(round(self.p2,2)))
			(self.ledger['P1']).append(str(round(self.p1,2)))
			(self.ledger['N1']).append(str(round(self.n1,2)))
			(self.ledger['N2']).append(str(round(self.n2,2)))
			(self.ledger['N3']).append(str(round(self.n3,2)))
			(self.ledger['P-delta']).append(str(round(self.pdelta,2)))
			(self.ledger['N-delta']).append(str(round(self.ndelta,2)))
			(self.ledger['Base-delta']).append(str(round(self.basedelta,2)))
