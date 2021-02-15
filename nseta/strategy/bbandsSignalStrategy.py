import logging
import pandas as pd

from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction
from nseta.strategy.simulatedorder import simulatedorder, OrderType
from nseta.strategy.basesignalstrategy import basesignalstrategy

__all__ = ['bbandsSignalStrategy']

class bbandsSignalStrategy(basesignalstrategy):
	def __init__(self, strict=False, intraday=False, requires_ledger=False):
		order_queue = simulatedorder(OrderType.MIS if intraday else OrderType.Delivery)
		super().__init__(requires_ledger=requires_ledger, order_queue=order_queue)
		self._strict = strict
		self._pat = Direction.Neutral
		self._dir = Direction.Neutral
		self._prc = 0
		self._ts = ''
		self._bbands_u = 0
		self._bbands_l = 0
		if default_logger().level == logging.DEBUG:
			self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[], 'Brokerage':[], 'BBands-U':[], 'BBands-L':[]}
		else:
			self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[], 'Brokerage':[]}

	@tracelog
	def test_strategy(self, df):
		# TODO: What if keys are in lowercase or dt/datetime is used instead of date/Date
		try:
			rowindex = 0
			self._target_met = False
			for lower_bband, upper_bband, price, ts in zip(df['BBands-L'], df['BBands-U'], df['Close'], df['Date']):
				self.index(lower_bband, upper_bband, price, ts)
				rowindex = rowindex + 1
				if self._target_met:
					break
			if self.order_queue.holdings_size < 0:
				buy_sell = 'BUY'
			elif self.order_queue.holdings_size > 0:
			 	buy_sell = 'SELL'
			else:
			 	buy_sell = 'SQR-OFF'
			self.order_queue.square_off(self.price)
			self.update_ledger(buy_sell)
			self.pnl = self.order_queue.pnl
			df_summary_dict = {'Symbol':[df['Symbol'].iloc[0]], 'Strategy':['BBands'], 'PnL':[self.pnl], 'Recommendation': [str(self.recommendation.name)]}
			df_summary = pd.DataFrame(df_summary_dict)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
		return self.report, df_summary

	@tracelog
	def index(self, lower_bband, upper_bband, price, timestamp):
		self.price = price
		if lower_bband is not None and lower_bband > 0:
			self.bbands_l = lower_bband
		if upper_bband is not None and upper_bband > 0:
			self.bbands_u = upper_bband
		if self.price >= upper_bband:
			self.sell_signal()
		if self.price <= lower_bband:
			self.buy_signal()
		super().index(price, timestamp)

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
	def bbands_u(self):
		return self._bbands_u

	@bbands_u.setter
	def bbands_u(self, upper_bband):
		self._bbands_u = upper_bband
		
	@property
	def bbands_l(self):
		return self._bbands_l

	@bbands_l.setter
	def bbands_l(self, lower_bband):
		self._bbands_l = lower_bband

	@property
	def price(self):
		return self._prc

	@price.setter
	def price(self, prc):
		self._prc = prc

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

	def v_pattern(self, prev_pattern=Direction.Neutral):
		if not self.strict:
			self.buy_signal()

	def invertedv_pattern(self, prev_pattern=Direction.Neutral):
		if not self.strict:
			self.sell_signal()

	def target_met(self, prev_pattern=Direction.Neutral):
		self._target_met = True
		self.order_queue.square_off(self.price)

	@tracelog
	def update_ledger(self, signal):
		if not self.requires_ledger:
			return
		(self.ledger['DateTime']).append(self.timestamp)
		(self.ledger['Signal']).append(signal)
		(self.ledger['Price']).append(str(self.price))
		(self.ledger['Funds']).append(str(round(self.order_queue.funds,2)))
		(self.ledger['Order_Size']).append(str(round(self.order_queue.order_size,2)))
		(self.ledger['Holdings_Size']).append(str(round(self.order_queue.holdings_size,2)))
		(self.ledger['Portfolio_Value']).append(str(round(self.order_queue.portfolio_value,2)))
		(self.ledger['Brokerage']).append(str(round(self.order_queue.brokerage,2)))
		if default_logger().level == logging.DEBUG:
			(self.ledger['BBands-U']).append(str(round(self.bbands_u,2)))
			(self.ledger['BBands-L']).append(str(round(self.bbands_l,2)))
