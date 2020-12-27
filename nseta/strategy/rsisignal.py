import enum

__all__ = ['rsisignal','Direction']

class Direction(enum.Enum):
	Down = 1
	Neutral = 2
	Up = 3
	V = 4
	InvertedV = 5

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

	def index(self, rsi, price):
		if rsi > 0:
			self.n3 = rsi
			self.price = price
			if self.p3 > 0:
				self.update_direction()

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

	def update_direction(self):
		self.direction = Direction.Neutral
		self.pattern = Direction.Neutral
		if (self.n1 > self.n2) and (self.n2 > self.n3):
			self.direction = Direction.Down
			if (self.p1 > self.p2) and (self.p2 > self.p3):
				self.pattern = Direction.InvertedV
				if self.n3 > 60 and self.buytriggerred:
					self.sell_signal()
		if (self.n1 < self.n2) and (self.n2 < self.n3):
			self.direction = Direction.Up
			if (self.p1 < self.p2) and (self.p2 < self.p3):
				self.pattern = Direction.V
				if self.n3 < 40:
					self.buy_signal()

	def buy_signal(self):
		self.buytriggerred = True
		self._profit = self._profit - self.price
		print("Buy Signal at Price," + str(self.price) + ", and RSI, " + str([self.n3, self.n2, self.n1, self.p1, self.p2, self.p3]) + ", Profit:, " + str(self._profit))

	def sell_signal(self):
		self._profit = self._profit + self.price
		print("Sell Signal at Price," + str(self.price) + ", and RSI," + str([self.n3, self.n2, self.n1, self.p1, self.p2, self.p3]) + ", Profit:, " + str(self._profit))
