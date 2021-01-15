
from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction

__all__ = ['basesignalstrategy']

class basesignalstrategy:
	def __init__(self):
		self._pat = Direction.Neutral
		self._dir = Direction.Neutral
		self._p1 = 0
		self._p2 = 0
		self._p3 = 0
		self._n1 = 0
		self._n2 = 0
		self._n3 = 0
		self._ts = ''

	@tracelog
	def index(self, index, timestamp):
		self.n3 = index
		self.timestamp = timestamp
		if self.p3 > 0:
			self.update_direction()
	
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
				self.invertedv_pattern()
			elif (self.p1 < self.p2) and (self.p2 < self.p3): # All last 6 values fell
				self.pattern = Direction.LowerLow
				self.lowerlow_direction()

		if (self.n1 < self.n2) and (self.n2 < self.n3):
			self.direction = Direction.Up
			if (self.p1 < self.p2) and (self.p2 < self.p3):
				self.pattern = Direction.V
				self.v_pattern()
			elif (self.p1 > self.p2) and (self.p2 > self.p3):
				self.pattern = Direction.HigherHigh
				self.higherhigh_pattern()

	def v_pattern(self):
		default_logger().debug("\n{}".format(self.pattern))

	def invertedv_pattern(self):
		default_logger().debug("\n{}".format(self.pattern))

	def higherhigh_pattern(self):
		default_logger().debug("\n{}".format(self.pattern))

	def lowerlow_direction(self):
		default_logger().debug("\n{}".format(self.pattern))
