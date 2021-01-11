__all__ = ['simulatedorder']

class simulatedorder:
	def __init__(self):
		self._buy_prop = 1
		self._sell_prop = 1
		self._commission = 0
		self._funds = 100000
		self._stock_price = 0
		self._holdings_size = 0
		self._order_size = 0

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
		return self.funds + self.stock_value

	def buy(self, price, allow_square_off_at_EOD=False, square_off=False):
		self.stock_price = price
		if self.funds >= price:
			afforded_size = int(
				self.funds
				/ (self.stock_price * (1 + self.commission))
			)
			buy_prop_size = int(afforded_size * self.buy_prop)
			final_size = min(buy_prop_size, afforded_size)
			self.order_size = final_size
			self.holdings_size = self.holdings_size + self.order_size
			self.funds = self.funds - final_size * (self.stock_price * (1 + self.commission))
		elif allow_square_off_at_EOD:
			if square_off:
				self.order_size = self.holdings_size
				self.holdings_size = 0
				self.funds = self.funds + self.order_size * (self.stock_price * (1 + self.commission))
			else:
				self.order_size = self.buy_prop
				self.holdings_size = self.holdings_size + self.order_size
				self.funds = self.funds + self.holdings_size * (self.stock_price * (1 + self.commission))
		else:
			self.order_size = 0

	def sell(self, price, allow_square_off_at_EOD=False, square_off=False):
		self.stock_price = price
		if self.holdings_size > 0:
			self.order_size = self.holdings_size
			self.funds = self.funds + self.order_size * (self.stock_price * (1 + self.commission))
			self.holdings_size = self.holdings_size - self.order_size
		elif allow_square_off_at_EOD:
			if square_off:
				self.order_size = self.holdings_size
				self.holdings_size = 0
				self.funds = self.funds + self.order_size * (self.stock_price * (1 + self.commission))
			else:
				self.order_size = self.sell_prop
				self.holdings_size = self.holdings_size - self.order_size
				self.funds = self.funds + self.order_size * (self.stock_price * (1 + self.commission))
		else:
			self.order_size = 0

	def square_off(self, price):
		if self.holdings_size == 0:
			self.order_size = 0
			return
		elif self.holdings_size > 0:
			self.sell(price, allow_square_off_at_EOD= True, square_off = True)
		elif self.holdings_size < 0:
			self.buy(price, allow_square_off_at_EOD= True, square_off = True)
