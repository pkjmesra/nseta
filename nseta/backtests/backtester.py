# -*- coding: utf-8 -*-
from nseta.common.log import tracelog, default_logger

__all__ = ['Backtester']

class Backtester:
  def __init__(self):
      default_logger().debug('Backtester Initialized with params {}'.format(''))

  def backtest(self):
      default_logger().debug('Backtesting with params {}'.format(''))
