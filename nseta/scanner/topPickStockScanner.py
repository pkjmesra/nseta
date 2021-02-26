# -*- coding: utf-8 -*-
from nseta.scanner.intradayStockScanner import intradayStockScanner

__all__ = ['topPickStockScanner']

class topPickStockScanner(intradayStockScanner):
  def __init__(self, indicator='all'):
    super().__init__(indicator=indicator)
