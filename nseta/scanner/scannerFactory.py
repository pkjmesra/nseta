from nseta.scanner.intradayScanner import intradayScanner
from nseta.scanner.liveScanner import liveScanner
from nseta.scanner.quoteScanner import quoteScanner
from nseta.scanner.swingScanner import swingScanner
from nseta.scanner.volumeScanner import volumeScanner
from nseta.scanner.topPickScanner import topPickScanner
from nseta.scanner.newsScanner import newsScanner
from nseta.scanner.stockscanner import ScannerType

__all__ = ['scannerFactory']

class scannerFactory:
	@staticmethod
	def scanner(scanner_type=ScannerType.Unknown, stocks=[], indicator=None, background=False):
		scanner_dict = {(ScannerType.Intraday).name:intradayScanner,
			(ScannerType.Live).name:liveScanner,
			(ScannerType.Quote).name:quoteScanner,
			(ScannerType.Swing).name:swingScanner,
			(ScannerType.Volume).name:volumeScanner,
			(ScannerType.TopPick).name:topPickScanner,
			(ScannerType.News).name:newsScanner}
		return scanner_dict[scanner_type.name](scanner_type=scanner_type,
			stocks=stocks, indicator=indicator, background=background)
