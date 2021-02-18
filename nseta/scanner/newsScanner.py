from nseta.scanner.baseScanner import baseScanner
from nseta.resources.resources import resources
from nseta.common.log import tracelog

__all__ = ['topPickScanner']

class newsScanner(baseScanner):

	def __init__(self, scanner_type, stocks=[], indicator=None, background=False):
		super().__init__(scanner_type,stocks,indicator=indicator, background=background)

	@tracelog
	def scan(self, option=None, analyse=False):
		super().scan(option= 'Cnt_Cdl' if option is None else option, analyse=analyse)
