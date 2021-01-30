
from nseta.scanner.baseStockScanner import baseStockScanner, TECH_INDICATOR_KEYS, ScannerType
from nseta.scanner.intradayStockScanner import intradayStockScanner
from nseta.scanner.liveStockScanner import liveStockScanner
from nseta.scanner.swingStockScanner import swingStockScanner
from nseta.scanner.volumeStockScanner import volumeStockScanner

__all__ = ['scanner', 'TECH_INDICATOR_KEYS', 'ScannerType']

# PIVOT_KEYS =['PP', 'R1','S1','R2','S2','R3','S3']

class scanner(baseStockScanner):
	def __init__(self, indicator='all'):
		super().__init__(indicator=indicator)

	def get_func_name(self, scanner_type=ScannerType.Unknown):
		scn = scanner.stockScanner(scanner_type=scanner_type, indicator=self.indicator)
		return scn.get_func_name()

	@staticmethod
	def stockScanner(scanner_type=ScannerType.Unknown, indicator=None):
		scanner_dict = {(ScannerType.Intraday).name:intradayStockScanner,
			(ScannerType.Live).name:liveStockScanner,
			(ScannerType.Swing).name:swingStockScanner,
			(ScannerType.Volume).name:volumeStockScanner}
		return scanner_dict[scanner_type.name](indicator=indicator)

	# def buy_solid():
		# OBV trending upwards
		# RSI trending upwards. If not, then if it's closer to lower limit, strong buy
		# MACD trending upwards and +ve. MACD > MACD 12
		# LTP line > EMA9 and LTP > MA50
		# MOM +ve and trending upwards
