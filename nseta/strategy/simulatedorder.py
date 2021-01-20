import enum

__all__ = ['simulatedorder', 'OrderType', 'INITIAL_FUNDS']

INITIAL_FUNDS = 100000

class OrderType(enum.Enum):
	MIS = 1
	Delivery = 2

class simulatedorder:
	def __init__(self, order_type=OrderType.Delivery):
		self._buy_prop = 1
		self._sell_prop = 1
		self._single_tran_multiplier = 0.5
		self._commission = 0
		self._funds = INITIAL_FUNDS
		self._stock_price = 0
		self._holdings_size = 0
		self._order_size = 0
		self._order_type = order_type
		self._margin = 0.2 if self.order_type == OrderType.MIS else 1 # Only 20% margin is assumed to be required

	@property
	def single_tran_multiplier(self):
		return self._single_tran_multiplier

	@property
	def pnl(self):
		return round(self.portfolio_value - INITIAL_FUNDS, 2)

	@property
	def order_type(self):
		return self._order_type

	@property
	def margin(self):
		return self._margin

	@property
	def buy_prop(self):
		return self._buy_prop

	@property
	def sell_prop(self):
		return self._sell_prop

	@property
	def commission(self):
		return self._commission

	@property
	def funds(self):
		return self._funds

	@funds.setter
	def funds(self, value):
		self._funds = value

	@property
	def stock_price(self):
		return self._stock_price

	@stock_price.setter
	def stock_price(self, value):
		self._stock_price = value

	@property
	def stock_value(self):
		return self.holdings_size * self.stock_price

	@property
	def holdings_size(self):
		return self._holdings_size

	@holdings_size.setter
	def holdings_size(self, value):
		self._holdings_size = value

	@property
	def order_size(self):
		return self._order_size

	@order_size.setter
	def order_size(self, value):
		self._order_size = value

	@property
	def portfolio_value(self):
		return self.funds + self.stock_value * self.margin

	def buy(self, price):
		self.stock_price = price
		available_funds = self.funds * self.single_tran_multiplier / self.margin
		if self.holdings_size >= 0:
			# This is a normal delivery order.
			if available_funds > price:
				afforded_size = int(
					available_funds
					/ (self.stock_price * (1 + self.commission))
				)
				buy_prop_size = int(afforded_size * self.buy_prop)
				final_size = min(buy_prop_size, afforded_size)
				self.order_size = final_size
				self.holdings_size = self.holdings_size + self.order_size
				used_funds = final_size * (self.stock_price * (1 + self.commission))
				self.funds = self.funds - used_funds * self.margin
		elif self.holdings_size < 0 and self.order_type == OrderType.MIS:
			# This is an MIS order and we have to square off
			self.order_size = self.holdings_size
			self.holdings_size = 0
			money_made = 0 - self.order_size * (self.stock_price * (1 - self.commission))
			self.funds = self.funds + money_made * self.margin
	
	def sell(self, price):
		self.stock_price = price
		if self.holdings_size > 0:
			# Assuming a buy order preceded this sell order, so holdings are +ve
			self.order_size = self.holdings_size
			money_made = self.order_size * (self.stock_price * (1 - self.commission))
			self.holdings_size = self.holdings_size - self.order_size
			self.funds = self.funds + money_made * self.margin
		elif self.holdings_size <= 0 and self.order_type == OrderType.MIS:
			# Must square off later in the day. This is an MIS order
			available_funds = self.funds / self.margin
			afforded_size = int(
					available_funds
					/ (self.stock_price * (1 + self.commission))
				)
			sell_prop_size = int(afforded_size * self.sell_prop)
			final_size = min(sell_prop_size, afforded_size)
			self.order_size = final_size
			used_funds = self.order_size * (self.stock_price * (1 + self.commission))
			self.holdings_size = self.holdings_size - self.order_size
			self.funds = self.funds - (used_funds) * self.margin

	def square_off(self, price):
		if self.holdings_size == 0:
			self.order_size = 0
			return
		elif self.holdings_size > 0:
			self.sell(price)
		elif self.holdings_size < 0:
			self.buy(price)
