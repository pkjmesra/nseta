import pandas as pd
from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction
from nseta.strategy.simulatedorder import simulatedorder, OrderType
from nseta.strategy.basesignalstrategy import basesignalstrategy

__all__ = ['rsiSignalStrategy']

class rsiSignalStrategy(basesignalstrategy):
	def __init__(self, strict=False):
		super().__init__()
		self._strict = strict
		self._prc = 0
		self._profit = 0
		self._buytriggerred = False
		self._lower = 25
		self._upper = 75
		self._order_queue = simulatedorder(OrderType.MIS)
		self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Pattern':[],'Direction':[], 'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[], 'P3':[], 'P2':[], 'P1':[], 'N1':[], 'N2':[], 'N3':[],'P-delta':[], 'N-delta':[], 'Base-delta':[]}

	@tracelog
	def set_limits(self, lower, upper):
		self._lower = lower
		self._upper = upper

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
			buy_sell = 'BUY' if self.order_queue.holdings_size < 0 else 'SELL'
			self.order_queue.square_off(self.price)
			self.update_ledger(buy_sell)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
		return self.report

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
	def buytriggerred(self):
		return self._buytriggerred

	@buytriggerred.setter
	def buytriggerred(self, buyt):
		self._buytriggerred = buyt

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

	def v_pattern(self):
		self.buy_signal()

	def invertedv_pattern(self):
		self.sell_signal()

	def higherhigh_pattern(self):
		if not self.strict:
			self.buy_signal()

	def lowerlow_direction(self):
		if not self.strict:
			self.sell_signal()

	def buy_signal(self):
		self.buytriggerred = True
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
		(self.ledger['DateTime']).append(self.timestamp)
		(self.ledger['Signal']).append(signal)
		(self.ledger['Price']).append(str(self.price))
		(self.ledger['Pattern']).append(str(self.pattern))
		(self.ledger['Direction']).append(str(self.direction))
		(self.ledger['Funds']).append(str(round(self.order_queue.funds,2)))
		(self.ledger['Order_Size']).append(str(round(self.order_queue.order_size,2)))
		(self.ledger['Holdings_Size']).append(str(round(self.order_queue.holdings_size,2)))
		(self.ledger['Portfolio_Value']).append(str(round(self.order_queue.portfolio_value,2)))
		(self.ledger['P3']).append(str(round(self.p3,2)))
		(self.ledger['P2']).append(str(round(self.p2,2)))
		(self.ledger['P1']).append(str(round(self.p1,2)))
		(self.ledger['N1']).append(str(round(self.n1,2)))
		(self.ledger['N2']).append(str(round(self.n2,2)))
		(self.ledger['N3']).append(str(round(self.n3,2)))
		(self.ledger['P-delta']).append(str(round(self.pdelta,2)))
		(self.ledger['N-delta']).append(str(round(self.ndelta,2)))
		(self.ledger['Base-delta']).append(str(round(self.basedelta,2)))
