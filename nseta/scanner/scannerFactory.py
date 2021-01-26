import enum
from nseta.scanner.intradayScanner import intradayScanner
from nseta.scanner.liveScanner import liveScanner
from nseta.scanner.quoteScanner import quoteScanner
from nseta.scanner.swingScanner import swingScanner
from nseta.scanner.volumeScanner import volumeScanner

__all__ = ['scannerFactory', 'ScannerType']

class ScannerType(enum.Enum):
	Intraday = 1
	Live = 2
	Quote = 3
	Swing = 4
	Volume = 5
	Unknown = 6

class scannerFactory:
	@staticmethod
	def scanner(scanner_type=ScannerType.Unknown, stocks=[], indicator=None, background=False):
		scanner_dict = {(ScannerType.Intraday).name:intradayScanner, 
			(ScannerType.Live).name:liveScanner,
			(ScannerType.Quote).name:quoteScanner,
			(ScannerType.Swing).name:swingScanner,
			(ScannerType.Volume).name:volumeScanner}
		return scanner_dict[scanner_type.name](scanner_type=scanner_type, 
			stocks=stocks, indicator=indicator, background=background)
