import click

from nseta.scanner.stockscanner import TECH_INDICATOR_KEYS
from nseta.cli.inputs import *
from nseta.common.tradingtime import current_datetime_in_ist_trading_time_range
from nseta.common.log import tracelog, default_logger
from nseta.scanner.scannerFactory import *
from nseta.scanner.stockscanner import ScannerType

__all__ = ['live_quote', 'scan']

ORDER_BY_KEYS = ['intraday', 'momentum']
RUN_IN_BACKGROUND = True

@click.command(help='Get live price quote of a security')
@click.option('--symbol', '-S',  help='Security code.')
@click.option('--general', '-g', default=False, is_flag=True, help='Get the general (Name, ISIN) details also (Optional)')
@click.option('--ohlc', '-o', default=False, is_flag=True, help='Get the OHLC values also (Optional)')
@click.option('--wk52', '-w' ,default=False, is_flag=True, help='Get the 52 week high/low values also (Optional)')
@click.option('--volume', '-v', default=False, is_flag=True, help='Get the traded volume details also (Optional)')
@click.option('--orderbook', '-b', default=False, is_flag=True, help='Get the current bid/offer details also (Optional)')
@click.option('--background', '-r', default=False, is_flag=True, help='Keep running the process in the background (Optional)')
@tracelog
def live_quote(symbol, general, ohlc, wk52, volume, orderbook, background):
	if not validate_symbol(symbol):
		print_help_msg(live_quote)
		return
	scanner = scannerFactory.scanner(ScannerType.Quote)
	scanner.scan(symbol, general, ohlc, wk52, volume, orderbook, background)

@click.command(help='Scan live and intraday for prices and signals.')
@click.option('--stocks', '-S', default=[], help='Comma separated security codes(Optional). When skipped, all stocks configured in stocks.txt will be scanned.)')
@click.option('--live', '-l', default=False, is_flag=True, help='Scans (every min. when in background) the live-quote and lists those that meet the signal criteria. Works best with --background.')
@click.option('--intraday', '-i', default=False, is_flag=True, help='Scans (every 10 sec when in background) the intraday price history and lists those that meet the signal criteria')
@click.option('--swing', '-s', default=False, is_flag=True, help='Scans (every 10 sec when in background) the past 90 days price history and lists those that meet the signal criteria')
@click.option('--volume', '-v', default=False, is_flag=True, help='Scans (every 10 sec when in background) the past 7 days price history and lists those that meet the signal criteria')
@click.option('--indicator', '-t', default='all', type=click.Choice(TECH_INDICATOR_KEYS),
	help=', '.join(TECH_INDICATOR_KEYS) + ". Choose one.")
@click.option('--orderby', '-o', default='intraday', type=click.Choice(ORDER_BY_KEYS),
	help=', '.join(ORDER_BY_KEYS) + ". Choose one.")
@click.option('--clear', '-c', default=False, is_flag=True, help='Clears the cached data for the given options.')
@click.option('--background', '-r', default=False, is_flag=True, help='Keep running the process in the background (Optional)')
@tracelog
def scan(stocks, live, intraday, swing, volume, indicator, orderby, clear, background):
	if (live and intraday) or ( live and swing) or (intraday and swing) or (live and volume) or (intraday and volume) or (swing and volume):
		click.secho('Choose only one of --live, --intraday, --swing or --volume options.', fg='red', nl=True)
		print_help_msg(scan)
		return
	elif not live and not intraday and not swing and not volume:
		click.secho('Choose at least one of the --live, --intraday (recommended) , --volume or --swing options.', fg='red', nl=True)
		print_help_msg(scan)
		return

	if stocks is not None and len(stocks) > 0:
		stocks = [x.strip() for x in stocks.split(',')]
	else:
		stocks = []
	global RUN_IN_BACKGROUND
	try:
		scanner_type = ScannerType.Volume if volume else (ScannerType.Intraday if intraday else (ScannerType.Swing if swing else ScannerType.Live))
		scanner = scannerFactory.scanner(scanner_type, stocks, indicator, background)
		scanner.clear_cache(clear, force_clear = current_datetime_in_ist_trading_time_range())
		scanner.scan(option=orderby)
	except Exception as e:
		RUN_IN_BACKGROUND = False
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to scan.\n', fg='red', nl=True)
		return
	except SystemExit:
		RUN_IN_BACKGROUND = False
		return

'''
TODO:
1. Scan for stocks that have 
	higher highs or V patterns of MOM, OBV, MACD, Price, RSI 
	and RSI is bullish (50+). 
	and Price is above EMA(9), SMA(10) and SMA(50)
	and MOM is +ve
	and OBV is +ve
	and MACD is > signal by a margin of x
	and volume is rising compared to 7day or yesterday's volume
'''