import enum
from nseta.common.log import logdebug, default_logger
import click

__all__ = ['rsisignal','Direction']

class Direction(enum.Enum):
	Down = 1
	Neutral = 2
	Up = 3
	V = 4
	InvertedV = 5
	LowerLow = 6
	HigherHigh = 7

class rsisignal:
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
		self._buytriggerred = False
		self._lower = 30
		self._upper = 70

	@logdebug
	def set_limits(self, lower, upper):
		self._lower = lower
		self._upper = upper

	@logdebug
	def index(self, rsi, price):
		if rsi > 0:
			self.n3 = rsi
			self.price = price
			if self.p3 > 0:
				self.update_direction()

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

	@logdebug
	def update_direction(self):
		self.direction = Direction.Neutral
		self.pattern = Direction.Neutral
		selllog = "Sell Signal at " + self.to_string() + ", Profit:, " + str(self._profit) + "\n"
		if (self.n1 > self.n2) and (self.n2 > self.n3):
			self.direction = Direction.Down
			default_logger().debug("Down direction detected." + self.to_string())
			if (self.p1 > self.p2) and (self.p2 > self.p3):
				self.pattern = Direction.InvertedV
				if (self.n1 >= self.upper) and self.basedelta >= 5:
					self.sell_signal(selllog)
		if self.ndelta >= 20 and self.n3 >= self.upper:
			self.direction = Direction.Up
			if self.basedelta <= -25:
				self.pattern = Direction.HigherHigh
				self.sell_signal(selllog)

		buylog = "Buy Signal at " + self.to_string() + ", Profit:, " + str(self._profit) + "\n"
		if (self.n1 < self.n2) and (self.n2 < self.n3):
			self.direction = Direction.Up
			default_logger().debug("Up direction detected." + self.to_string())
			if (self.p1 < self.p2) and (self.p2 < self.p3):
				self.pattern = Direction.V
				if (self.n1 <= self.lower) and self.basedelta >=20:
					self.buy_signal(buylog)
		if self.ndelta <= -15 and self.n3 <= self.lower:
			if self.basedelta >=20:
				self.pattern = Direction.LowerLow
				self.buy_signal(buylog)


	@logdebug
	def buy_signal(self, log):
		self.buytriggerred = True
		self._profit = self._profit - self.price
		click.secho(log, fg='green', nl=True)

	@logdebug
	def sell_signal(self, log):
		self._profit = self._profit + self.price
		click.secho(log, fg='red', nl=True)

	def to_string(self):
		s1 = "Pattern:" + str(self.pattern) + ",Price:" + str(self.price) + "," + " Direction:" + str(self.direction) + ",\n" 
		s2 = "p3:"+ str(self.p3) + "," + "p2:"+ str(self.p2) + "," + "p1:"+ str(self.p1) + ",\n"
		s3 = "n1:"+ str(self.n1) + "," + "n2:"+ str(self.n2) + "," + "n3:"+ str(self.n3) + ",\n"
		s4 = "p-delta:"+ str(self.pdelta) + "," + "n-delta:"+ str(self.ndelta) + "," + "base-delta:"+ str(self.basedelta) + ",\n"
		return s1 + s2 + s3 + s4
