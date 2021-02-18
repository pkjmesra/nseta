from nseta.scanner.intradayStockScanner import intradayStockScanner
from nseta.common.log import tracelog, default_logger

__all__ = ['topPickStockScanner']

class topPickStockScanner(intradayStockScanner):
	def __init__(self, indicator='all'):
		super().__init__(indicator=indicator)
