# -*- coding: utf-8 -*-
import logging
import pandas as pd

from nseta.common.log import tracelog, default_logger
from nseta.common.commons import Direction, Recommendation
from nseta.resources.resources import *
from nseta.strategy.simulatedorder import simulatedorder, OrderType
from nseta.strategy.basesignalstrategy import basesignalstrategy

__all__ = ['rsiSignalStrategy']

class rsiSignalStrategy(basesignalstrategy):
  def __init__(self, strict=False, intraday=False, requires_ledger=False):
    order_queue = simulatedorder(OrderType.MIS if intraday else OrderType.Delivery)
    self.lower = resources.rsi().lower
    self.upper = resources.rsi().upper
    super().__init__(requires_ledger=requires_ledger, order_queue=order_queue, 
      crossover_lower = self.lower, crossover_upper = self.upper)
    self.strict = strict
    self.prc = 0
    
    if default_logger().level == logging.DEBUG:
      self.ledger = {'DateTime':[],'Signal':[],'Price':[],'Pattern':[],'Direction':[], 'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[], 'Brokerage':[], 'P3':[], 'P2':[], 'P1':[], 'N1':[], 'N2':[], 'N3':[],'P-delta':[], 'N-delta':[], 'Base-delta':[]}
    else:
      self.ledger = {'DateTime':[],'Signal':[],'Price':[],'Pattern':[],'Direction':[], 'Funds':[], 'Order_Size':[], 'Holdings_Size':[], 'Portfolio_Value':[], 'Brokerage':[]}

  @tracelog
  def set_limits(self, lower, upper):
    self.lower = lower
    self.upper = upper
    super().set_limits(lower,upper)

  @tracelog
  def test_strategy(self, df):
    # TODO: What if keys are in lowercase or dt/datetime is used instead of date/Date
    self.target_met_status = False
    try:
      rowindex = 0
      for rsi in (df['RSI']).values:
        if rsi is not None:
          price =(df.iloc[rowindex])['Close']
          ts =(df.iloc[rowindex])['Date']
          self.index(rsi, price, ts)
          if self.target_met_status:
            break
        rowindex = rowindex + 1
      if self.order_queue.holdings_size < 0:
        buy_sell = 'BUY'
      elif self.order_queue.holdings_size > 0:
        buy_sell = 'SELL'
      else:
        buy_sell = 'SQR-OFF'
      self.order_queue.square_off(self.price)
      self.update_ledger(buy_sell)
      self.pnl = self.order_queue.pnl
      df_summary_dict = {'Symbol':[df['Symbol'].iloc[0]], 'Strategy':['RSI'], 'PnL':[self.pnl], 'Recommendation': [str(self.recommendation.name)]}
      df_summary = pd.DataFrame(df_summary_dict)
    except Exception as e:
      default_logger().debug(e, exc_info=True)
    return self.report, df_summary

  @tracelog
  def index(self, rsi, price, timestamp):
    if rsi > 0:
      self.price = price
      super().index(rsi, timestamp)

  @property
  def report(self):
    return pd.DataFrame(self.ledger)

  def crossedover_lower(self, prev_pattern=Direction.Neutral):
    if prev_pattern == Direction.Up:
      self.direction = Direction.Up
      self.pattern = Direction.OverSold
      self.buy_signal()

  def crossedover_upper(self, prev_pattern=Direction.Neutral):
    if prev_pattern == Direction.Down:
      self.direction = Direction.Down
      self.pattern = Direction.OverBought
      self.sell_signal()

  def target_met(self, prev_pattern=Direction.Neutral):
    self.target_met_status = True
    self.order_queue.square_off(self.price)

  def v_pattern(self, prev_pattern=Direction.Neutral):
    # if self.n3 >= 55:
    #   self.recommendation = Recommendation.Buy
    self.buy_signal()
    # else:
    #   self.recommendation = Recommendation.Hold
    self.check_squareoff(down=False);

  def invertedv_pattern(self, prev_pattern=Direction.Neutral):
    self.sell_signal()
    self.check_squareoff(down=True);

  def possible_higherhigh_pattern(self, prev_pattern=Direction.Neutral):
    if not self.strict and self.n1 <= self.lower:
      self.recommendation = Recommendation.Buy
      self.buy_signal()
    else:
      self.recommendation = Recommendation.Hold
    self.check_squareoff(down=False);

  def possible_lowerlow_direction(self, prev_pattern=Direction.Neutral):
    if not self.strict and self.n1 >= self.upper:
      self.sell_signal()
    self.check_squareoff(down=True);

  def check_squareoff(self, down=False):
    if down and self.order_queue.holdings_size >= 0:
      self.order_queue.square_off(self.price)
    if not down and self.order_queue.holdings_size <= 0:
      self.order_queue.square_off(self.price)

  @tracelog
  def update_ledger(self, signal):
    if not self.requires_ledger:
      return
    (self.ledger['DateTime']).append(self.timestamp)
    (self.ledger['Signal']).append(signal)
    (self.ledger['Price']).append(str(self.price))
    (self.ledger['Pattern']).append(str(self.pattern.name))
    (self.ledger['Direction']).append(str(self.direction.name))
    (self.ledger['Funds']).append(str(round(self.order_queue.funds,2)))
    (self.ledger['Order_Size']).append(str(round(self.order_queue.order_size,2)))
    (self.ledger['Holdings_Size']).append(str(round(self.order_queue.holdings_size,2)))
    (self.ledger['Portfolio_Value']).append(str(round(self.order_queue.portfolio_value,2)))
    (self.ledger['Brokerage']).append(str(round(self.order_queue.brokerage,2)))
    if default_logger().level == logging.DEBUG:
      (self.ledger['P3']).append(str(round(self.p3,2)))
      (self.ledger['P2']).append(str(round(self.p2,2)))
      (self.ledger['P1']).append(str(round(self.p1,2)))
      (self.ledger['N1']).append(str(round(self.n1,2)))
      (self.ledger['N2']).append(str(round(self.n2,2)))
      (self.ledger['N3']).append(str(round(self.n3,2)))
      (self.ledger['P-delta']).append(str(round(self.pdelta,2)))
      (self.ledger['N-delta']).append(str(round(self.ndelta,2)))
      (self.ledger['Base-delta']).append(str(round(self.basedelta,2)))
