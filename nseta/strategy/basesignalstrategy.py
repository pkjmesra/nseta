import numpy as np
import pandas as pd

from nseta.resources.resources import *
from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction, Recommendation

__all__ = ['basesignalstrategy']

class basesignalstrategy:
	def __init__(self, requires_ledger=False, order_queue=None, crossover_lower=0, crossover_upper=0):
		self._pat = Direction.Neutral
		self._dir = Direction.Neutral
		self._p1 = np.nan
		self._p2 = np.nan
		self._p3 = np.nan
		self._n1 = np.nan
		self._n2 = np.nan
		self._n3 = np.nan
		self._ts = ''
		self._pnl = 0
		self._requires_ledger = requires_ledger
		self._baseledger = {'DateTime':[],'P3':[], 'P2':[], 'P1':[], 'N1':[], 'N2':[], 'N3':[]}
		self._reco = Recommendation.Unknown
		self._p_percent = resources.backtest().profit_threshhold_percent
		self._l_percent = 0 - resources.backtest().loss_threshhold_percent
		self._order_queue = order_queue
		self._crossover_lower = crossover_lower
		self._crossover_upper = crossover_upper


	@property
	def requires_ledger(self):
		return self._requires_ledger

	@property
	def crossover_lower(self):
		return self._crossover_lower

	@property
	def crossover_upper(self):
		return self._crossover_upper

	@property
	def profit_threshhold(self):
		return self._p_percent

	@property
	def loss_threshhold(self):
		return self._l_percent

	@property
	def baseledger(self):
		return self._baseledger

	@property
	def basereport(self):
		return pd.DataFrame(self.baseledger)

	@tracelog
	def index(self, index, timestamp):
		self.n3 = index
		self.timestamp = timestamp
		if self.p3 != np.nan:
			self.recommendation = Recommendation.Unknown
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
	def order_queue(self):
		return self._order_queue

	@order_queue.setter
	def order_queue(self, oq):
		self._order_queue = oq

	@property
	def pnl(self):
		return self._pnl

	@pnl.setter
	def pnl(self, pnl):
		self._pnl = pnl

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
	def direction(self, direction):
		self._dir = direction

	@property
	def p3(self):
		return self._p3

	@p3.setter
	def p3(self, p2):
		self._p3 = p2

	@property
	def p2(self):
		 return self._p2

	@p2.setter
	def p2(self, p1):
		if self._p2 != np.nan:
			self.p3 = self._p2
		self._p2 = p1

	@property
	def p1(self):
		return self._p1

	@p1.setter
	def p1(self, n1):
		if self._p1 != np.nan:
			self.p2 = self._p1
		self._p1 = n1

	@property
	def n1(self):
		return self._n1

	@n1.setter
	def n1(self, n2):
		if self._n1 != np.nan:
			self.p1 = self._n1
		self._n1 = n2

	@property
	def n2(self):
		return self._n2

	@n2.setter
	def n2(self, n3):
		if self._n2 != np.nan:
			self.n1 = self._n2
		self._n2 = n3

	@property
	def n3(self):
		return self._n3

	@n3.setter
	def n3(self, current):
		if self._n3 != np.nan:
			self.n2 = self._n3
		self._n3 = current

	@property
	def recommendation(self):
		return self._reco

	@recommendation.setter
	def recommendation(self, reco):
		self._reco = reco

	@tracelog
	def update_direction(self):
		if self.requires_ledger:
			(self.baseledger['DateTime']).append(self.timestamp)
			(self.baseledger['P3']).append(str(round(self.p3,2)))
			(self.baseledger['P2']).append(str(round(self.p2,2)))
			(self.baseledger['P1']).append(str(round(self.p1,2)))
			(self.baseledger['N1']).append(str(round(self.n1,2)))
			(self.baseledger['N2']).append(str(round(self.n2,2)))
			(self.baseledger['N3']).append(str(round(self.n3,2)))
		n1gtn2 = True if self.n1 > self.n2 else False
		n2ltn3 = True if self.n2 < self.n3 else False
		n1ltn3 = True if self.n1 < self.n3 else False
		n1ltn2 = True if self.n1 < self.n2 else False
		n2gtn3 = True if self.n2 > self.n3 else False
		n1gtn3 = True if self.n1 > self.n3 else False
		n3ltn2 = True if self.n3 < self.n2 else False
		prev_pattern = self.pattern
		self.recommendation = Recommendation.Hold if n2ltn3 else Recommendation.Sell
		if n1gtn2 and n2ltn3: # The last 3rd and 2nd values fell and last one reversed in direction
			if (self.p1 < self.p2) and (self.p2 < self.p3): # All previous values were falling.
				self.pattern = Direction.PossibleReversalUpward
				self.recommendation = Recommendation.Buy
				self.possibleReversalUpward_pattern(prev_pattern=prev_pattern)
		if n1ltn2 and n3ltn2: # The last 3rd and 2nd values fell and last one reversed in direction
			if (self.p1 > self.p2) and (self.p2 > self.p3): # All previous values were falling.
				self.pattern = Direction.PossibleReversalDownward
				self.recommendation = Recommendation.Sell
				self.possibleReversalDownward_pattern(prev_pattern=prev_pattern)

		if n1gtn2 and n2gtn3: # The last 3 values fell
			self.direction = Direction.Down
			self.recommendation = Recommendation.Sell
			self.possible_lowerlow_direction(prev_pattern=prev_pattern)
			if ((self.p1 > self.p2) and (self.p2 > self.p3)) or ((self.p1 > self.p2) and (self.p1 > self.p3)): # The last 6th, 5th and 4th values were rising
				self.pattern = Direction.InvertedV
				self.recommendation = Recommendation.Sell
				self.invertedv_pattern(prev_pattern=prev_pattern)
			elif (self.p1 < self.p2) or (self.p1 < self.p3): # All last 5/6 values fell
				self.pattern = Direction.LowerLow
				self.recommendation = Recommendation.Sell
				self.lowerlow_direction(prev_pattern=prev_pattern)

		if n1ltn2 and n2ltn3: # The last 3 values rose
			self.direction = Direction.Up
			self.possible_higherhigh_pattern(prev_pattern=prev_pattern)
			self.recommendation = Recommendation.Hold
			if ((self.p1 < self.p2) and (self.p2 < self.p3)) or ((self.p1 < self.p2) and (self.p1 < self.p3)):
				self.pattern = Direction.V
				self.recommendation = Recommendation.Buy
				self.v_pattern(prev_pattern=prev_pattern)
			elif (self.p1 > self.p2) or (self.p1 > self.p3):
				self.pattern = Direction.HigherHigh
				self.recommendation = Recommendation.Buy
				self.higherhigh_pattern(prev_pattern=prev_pattern)
		
		if (n2ltn3 or n1ltn3) and self.n3 >= self.crossover_lower:
			self.crossedover_lower(prev_pattern=Direction.Up)
		if (n2gtn3 or n1gtn3) and self.n3 <= self.crossover_lower:
			self.crossedover_lower(prev_pattern=Direction.Down)

		if (n2ltn3 or n1ltn3) and self.n3 >= self.crossover_upper:
			self.crossedover_upper(prev_pattern=Direction.Up)
		if (n2gtn3 or n1gtn3) and self.n3 <= self.crossover_upper:
			self.crossedover_upper(prev_pattern=Direction.Down)

		if (self.order_queue.pnl_percent >= self.profit_threshhold) or (self.order_queue.pnl_percent <= self.loss_threshhold):
			self.target_met(prev_pattern=prev_pattern)

	def target_met(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def crossedover_lower(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def crossedover_upper(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def possible_higherhigh_pattern(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def possible_lowerlow_direction(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def possibleReversalUpward_pattern(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def possibleReversalDownward_pattern(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def v_pattern(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def invertedv_pattern(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def higherhigh_pattern(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))

	def lowerlow_direction(self, prev_pattern=Direction.Neutral):
		default_logger().debug("\n{}".format(self.pattern))
