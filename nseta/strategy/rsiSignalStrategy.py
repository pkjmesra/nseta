import pandas as pd
from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction
from nseta.strategy.simulatedorder import simulatedorder

__all__ = ['rsiSignalStrategy']

class rsiSignalStrategy:
	def __init__(self):
		self._pat = Direction.Neutral
		self._dir = Direction.Neutral
		self._p1 = 0
		self._p2 = 0
		self._p3 = 0
		self._n1 = 0
		self._n2 = 0
		self._n3 = 0
		self._prc = 0
		self._profit = 0
		self._ts = ''
		self._buytriggerred = False
		self._lower = 25
		self._upper = 75
		self._order_queue = simulatedorder()
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
			self.n3 = rsi
			self.price = price
			self.timestamp = timestamp
			if self.p3 > 0:
				self.update_direction()

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
	def pdelta(self):
		if self.pattern == Direction.InvertedV:
			return 100 *(self.p1 - self.p3)/self.p3
		else:
			return 100 *(self.p3 - self.p1)/self.p3

	@property
	def ndelta(self):
		if self.pattern == Direction.InvertedV:
			return 100 *(self.n1 - self.n3)/self.n1
		else:
			return 100 *(self.n3 - self.n1)/self.n1

	@property
	def basedelta(self):
		return 100 * (self.p3 - self.n3)/self.p3

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

	@property
	def timestamp(self):
		return self._ts

	@timestamp.setter
	def timestamp(self, ts):
		self._ts = ts

	@property
	def pattern(self):
		return self._pat

	@pattern.setter
	def pattern(self, pat):
		self._pat = pat

	@property
	def direction(self):
		return self._dir

	@direction.setter
	def direction(self, dir):
		self._dir = dir

	@property
	def p1(self):
		return self._p1

	@p1.setter
	def p1(self, previous1):
		self.p2 = self._p1
		self._p1 = previous1

	@property
	def p2(self):
		 return self._p2

	@p2.setter
	def p2(self, previous2):
		self.p3 = self._p2
		self._p2 = previous2

	@property
	def p3(self):
		return self._p3

	@p3.setter
	def p3(self, previous3):
		self._p3 = previous3

	@property
	def n1(self):
		return self._n1

	@n1.setter
	def n1(self, next1):
		self.p1 = self._n1
		self._n1 = next1

	@property
	def n2(self):
		return self._n2

	@n2.setter
	def n2(self, next2):
		self.n1 = self._n2
		self._n2 = next2

	@property
	def n3(self):
		return self._n3

	@n3.setter
	def n3(self, next3):
		self.n2 = self._n3
		self._n3 = next3

	def update_direction(self):
		if (self.n1 > self.n2) and (self.n2 > self.n3): # The last 3 values fell
			self.direction = Direction.Down
			if (self.p1 > self.p2) and (self.p2 > self.p3): # The last 6th, 5th and 4th values were rising
				self.pattern = Direction.InvertedV
				# if self.ndelta >= 15: # RSI fell > 15%
				self.sell_signal()
			elif (self.p1 < self.p2) and (self.p2 < self.p3): # All last 6 values fell
				self.pattern = Direction.LowerLow
				self.sell_signal()
		if self.n3 >= self.upper:
			self.direction = Direction.Up
			self.pattern = Direction.OverBought
			self.sell_signal()

		if (self.n1 < self.n2) and (self.n2 < self.n3):
			self.direction = Direction.Up
			if (self.p1 < self.p2) and (self.p2 < self.p3):
				self.pattern = Direction.V
				# if self.ndelta >= 15: # RSI rose > 15%
				self.buy_signal()
			elif (self.p1 > self.p2) and (self.p2 > self.p3):
				self.pattern = Direction.HigherHigh
				self.buy_signal()
		if self.n3 <= self.lower:
			self.direction = Direction.Down
			self.pattern = Direction.OverSold
			self.buy_signal()


	def buy_signal(self):
		self.buytriggerred = True
		self.order_queue.buy(self.price, allow_square_off_at_EOD=True)
		self.update_ledger('BUY')
		default_logger().debug("\n{}".format(pd.DataFrame(self.ledger)))

	def sell_signal(self):
		self.order_queue.sell(self.price, allow_square_off_at_EOD=True)
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
