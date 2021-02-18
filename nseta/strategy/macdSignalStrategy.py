import pandas as pd
import numpy as np

from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction
from nseta.strategy.simulatedorder import simulatedorder, OrderType
from nseta.strategy.basesignalstrategy import basesignalstrategy

__all__ = ['macdSignalStrategy']

class macdSignalStrategy(basesignalstrategy):
	def __init__(self, strict=False, intraday=False, requires_ledger=False):
		order_queue = simulatedorder(OrderType.MIS if intraday else OrderType.Delivery)
		super().__init__(requires_ledger=requires_ledger, order_queue=order_queue)
		# Cross over above zero line for buy or below zero line for sell
		self._strict = strict
		self._prc = 0
		self._macd9 = 0
		self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Pattern':[],'Direction':[], 'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[], 'Brokerage':[]}

	@tracelog
	def test_strategy(self, df):
		# TODO: What if keys are in lowercase or dt/datetime is used instead of date/Date
		try:
			rowindex = 0
			df_summary = None
			df = df.dropna()
			if df is None or len(df) ==0:
				return self.report, None
			self._target_met = False
			for macd, macd9 in zip((df['macd(12)']).values, (df['macdsignal(9)']).values):
				if macd is not None:
					price =(df.iloc[rowindex])['Close']
					ts =(df.iloc[rowindex])['Date']
					self.macd9 = macd9
					self.index(macd, price, ts)
					if self._target_met:
						break
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
			df_summary_dict = {'Symbol':[df['Symbol'].iloc[0]], 'Strategy':['MACD'], 'PnL':[self.pnl], 'Recommendation': [str(self.recommendation.name)]}
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
	def macd9(self):
		return self._macd9

	@macd9.setter
	def macd9(self, macd9):
		self._macd9 = macd9

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

	def target_met(self, prev_pattern=Direction.Neutral):
		self._target_met = True
		self.order_queue.square_off(self.price)

	@tracelog
	def v_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size <= 0:
		if self.n3 > self.macd9:
			self.buy_signal()
	
	@tracelog
	def invertedv_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size > 0:
		if self.n3 < self.macd9:
			self.sell_signal()

	@tracelog
	def possibleReversalUpward_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size <= 0:
		if not self.strict:
			self.buy_signal()

	@tracelog
	def possibleReversalDownward_pattern(self, prev_pattern=Direction.Neutral):
		# if self.order_queue.holdings_size > 0:
		if not self.strict:
			self.sell_signal()

	def possible_higherhigh_pattern(self, prev_pattern=Direction.Neutral):
		# holding_size = self.order_queue.holdings_size
		# if holding_size <= 0:
		if not self.strict:
			self.buy_signal()

	def lowerlow_direction(self, prev_pattern=Direction.Neutral):
		# holding_size = self.order_queue.holdings_size
		# if holding_size > 0:
		if not self.strict:
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
		if not self.requires_ledger:
			return
		(self.ledger['DateTime']).append(self.timestamp)
		(self.ledger['Signal']).append(signal)
		(self.ledger['Price']).append(str(self.price))
		(self.ledger['Pattern']).append(str(self.pattern.name))
		(self.ledger['Direction']).append(str(self.direction.name))
		(self.ledger['Funds']).append(str(round(self.order_queue.funds,2)))
		(self.ledger['Order_Size']).append(str(round(self.order_queue.order_size,2)))
		(self.ledger['Holdings_Size']).append(str(round(self.order_queue.holdings_size,2)))
		(self.ledger['Portfolio_Value']).append(str(round(self.order_queue.portfolio_value,2)))
		(self.ledger['Brokerage']).append(str(round(self.order_queue.brokerage,2)))
