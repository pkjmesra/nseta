import pandas as pd
from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction

__all__ = ['bbandsSignalStrategy']

class bbandsSignalStrategy:
	def __init__(self):
		self._pat = Direction.Neutral
		self._dir = Direction.Neutral
		self._prc = 0
		self._profit = 0
		self._ts = ''
		self._buytriggerred = False
		self._bbands_u = 0
		self._bbands_l = 0
		self._ledger = {'DateTime':[],'Signal':[],'Price':[],'Profit':[], 'BBands-U':[], 'BBands-L':[]}

	def test_strategy(self, df):
		# TODO: What if keys are in lowercase or dt/datetime is used instead of date/Date
		try:
			rowindex = 0
			for lower_bband, upper_bband, price, ts in zip(df['BBands-L'], df['BBands-U'], df['Close'], df['Date']): 
				self.index(lower_bband, upper_bband, price, ts)
				rowindex = rowindex + 1
		except Exception as e:
			default_logger().debug(e, exc_info=True)
			pass
		return self.report

	def index(self, lower_bband, upper_bband, price, timestamp):
		self.price = price
		self.timestamp = timestamp
		if lower_bband is not None and lower_bband > 0:
			self.bbands_l = lower_bband
		if upper_bband is not None and upper_bband > 0:
			self.bbands_u = upper_bband
		if self.price >= upper_bband:
			self.sell_signal()
		if self.price <= lower_bband:
			self.buy_signal()

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

	def buy_signal(self):
		self.buytriggerred = True
		self._profit = self._profit - self.price
		self.update_ledger('BUY')
		default_logger().debug("\n{}".format(pd.DataFrame(self.ledger)))

	def sell_signal(self):
		self._profit = self._profit + self.price
		self.update_ledger('SELL')
		default_logger().debug("\n{}".format(pd.DataFrame(self.ledger)))

	def update_ledger(self, signal):
		(self.ledger['DateTime']).append(self.timestamp)
		(self.ledger['Signal']).append(signal)
		(self.ledger['Price']).append(str(self.price))
		(self.ledger['Profit']).append(str(round(self._profit,2)))
		(self.ledger['BBands-U']).append(str(round(self.bbands_u,2)))
		(self.ledger['BBands-L']).append(str(round(self.bbands_l,2)))