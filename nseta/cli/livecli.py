import click
import pandas as pd
import threading, time

from nseta.live.live import get_quote, get_live_quote, get_data_list
from nseta.scanner.tiscanner import scanner, TECH_INDICATOR_KEYS
from nseta.archives.archiver import *
from nseta.cli.inputs import *
from nseta.common.tradingtime import *
from nseta.common.log import tracelog, default_logger
from datetime import datetime, date

__all__ = ['live_quote', 'scan', 'scan_live', 'scan_intraday']

NAME_LIST = ['Symbol', 'Name', 'ISIN']
QUOTE_LIST = ['Last Updated', 'Prev Close', 'Last Trade Price','Change','% Change', 'Avg. Price', 'Upper Band','Lower Band']
OHLC_LIST = ['Open', 'High', 'Low', 'Close']
WK52_LIST = ['52 Wk High', '52 Wk Low']
VOLUME_LIST = ['Quantity Traded', 'Total Traded Volume', 'Total Traded Value', 'Delivery Volume', '% Delivery']
PIPELINE_LIST = ['Bid Quantity', 'Bid Price', 'Offer_Quantity', 'Offer_Price']

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
	global RUN_IN_BACKGROUND
	try:
		orgdata, df = get_live_quote(symbol, general, ohlc, wk52, volume, orderbook)
		format_beautified(orgdata, general, ohlc, wk52, volume, orderbook)
		if background:
			b = threading.Thread(name='live_quote_background', target=live_quote_background, args=[symbol, general, ohlc, wk52, volume, orderbook])
			b.start()
	except Exception as e:
		RUN_IN_BACKGROUND = False
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to fetch live quote', fg='red', nl=True)
		return
	except SystemExit:
		RUN_IN_BACKGROUND = False
		return

@click.command(help='Scan live and intraday for prices and signals.')
@click.option('--stocks', '-S', default=[], help='Comma separated security codes(Optional. When skipped, all stocks configured in stocks.py will be scanned.)')
@click.option('--live', '-l', default=False, is_flag=True, help='Scans (every min.) the live-quote and lists those that meet the signal criteria. Works best with --background.')
@click.option('--intraday', '-i', default=False, is_flag=True, help='Scans (every 10 sec) the intraday price history and lists those that meet the signal criteria')
@click.option('--swing', '-s', default=False, is_flag=True, help='Scans (every 10 sec) the past 365 days price history and lists those that meet the signal criteria')
@click.option('--indicator', '-t', default='all', type=click.Choice(TECH_INDICATOR_KEYS),
	help=', '.join(TECH_INDICATOR_KEYS) + ". Choose one.")
@click.option('--clear', '-c', default=False, is_flag=True, help='Clears the cached data for the given options.')
@click.option('--background', '-r', default=False, is_flag=True, help='Keep running the process in the background (Optional)')
@tracelog
def scan(stocks, live, intraday, swing, indicator, clear, background):
	if (live and intraday) or ( live and swing) or (intraday and swing):
		click.secho('Choose only one of --live, --intraday or --swing options.', fg='red', nl=True)
		print_help_msg(scan)
		return
	elif not live and not intraday and not swing:
		click.secho('Choose at least one of the --live, --intraday (recommended) or --swing options.', fg='red', nl=True)
		print_help_msg(scan)
		return

	if stocks is not None and len(stocks) > 0:
		stocks = [x.strip() for x in stocks.split(',')]
	else:
		stocks = []
	global RUN_IN_BACKGROUND
	try:
		clear_cache(clear, background, indicator, intraday, live, swing)
		if live:
			scan_live(stocks, indicator, background)
		elif intraday:
			scan_intraday(stocks, indicator, background)
		elif swing:
			scan_swing(stocks, indicator, background)
	except Exception as e:
		RUN_IN_BACKGROUND = False
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to scan.', fg='red', nl=True)
		return
	except SystemExit:
		RUN_IN_BACKGROUND = False
		return

def scan_results_file_names(indicator):
	return 'df_Scan_Results.{}'.format(indicator), 'signaldf_Scan_Results.{}'.format(indicator)

def load_archived_scan_results(indicator, response_type):
	df_file_name , signaldf_file_name = scan_results_file_names(indicator)
	arch = archiver()
	df = arch.restore(df_file_name, response_type)
	signaldf = arch.restore(signaldf_file_name, response_type)
	return df, signaldf

def save_scan_results_archive(df, signaldf, response_type, indicator, should_cache=True):
	if should_cache or not current_datetime_in_ist_trading_time_range():
		df_file_name , signaldf_file_name = scan_results_file_names(indicator)
		arch = archiver()
		arch.archive(df, df_file_name, response_type)
		arch.archive(signaldf, signaldf_file_name, response_type)
		default_logger().debug('Saved to: {} and {}'.format(df_file_name, signaldf_file_name))

def scan_live(stocks, indicator, background):
	df, signaldf = load_archived_scan_results(indicator, ResponseType.Quote)
	s = scanner(indicator=indicator)
	if df is None or len(df) == 0:
		df, signaldf = s.scan_live(stocks=stocks)
	scan_live_results(df, signaldf, indicator)
	if background:
		b = threading.Thread(name='scan_live_background', target=scan_live_background, args=[s, stocks, indicator])
		b.start()

def scan_live_results(df, signaldf, indicator, should_cache=True):
	if df is not None and len(df) > 0:
		save_scan_results_archive(df, signaldf, ResponseType.Quote, indicator, should_cache)
		default_logger().debug("\nAll Stocks LTP and Signals:\n" + df.to_string(index=False))
	else:
		print('Nothing to show here.')
	if signaldf is not None and len(signaldf) > 0:
		print("\nLive Signals:\n" + signaldf.to_string(index=False))
	else:
		print('No signals to show here.')
	click.secho('Live scanning finished.', fg='green', nl=True)

def scan_intraday(stocks, indicator, background):
	df, signaldf = load_archived_scan_results(indicator, ResponseType.Intraday)
	s = scanner(indicator=indicator)
	if df is None or len(df) == 0:
		df, signaldf = s.scan_intraday(stocks=stocks)
	scan_intraday_results(df, signaldf, indicator)
	if background:
		b = threading.Thread(name='scan_intraday_background', target=scan_intraday_background, args=[s, stocks, indicator])
		b.start()

def scan_intraday_results(df, signaldf, indicator, should_cache=True):
	if df is not None and len(df) > 0:
		save_scan_results_archive(df, signaldf, ResponseType.Intraday, indicator, should_cache)
		default_logger().debug("\nAll Stocks LTP and Signals:\n" + df.to_string(index=False))
	else:
		print('Nothing to show here.')
	if signaldf is not None and len(signaldf) > 0:
		print("\nWe recommend taking the following BUY/SELL positions for day trading. Intraday Signals:\n" + signaldf.to_string(index=False))
	else:
		print('No signals to show here.')
	click.secho('Intraday scanning finished.', fg='green', nl=True)

def scan_swing(stocks, indicator, background):
	if background:
		default_logger().info('Background running not supported yet. Stay tuned. Executing just once...')
	df, signaldf = load_archived_scan_results(indicator, ResponseType.History)
	if df is None or len(df) == 0:
		s = scanner(indicator=indicator)
		df, signaldf = s.scan_swing(stocks=stocks)
	scan_swing_results(df, signaldf, indicator)
	# TODO: Include get-quote results for OHLC of today before market closing hours for better accuracy
	# if background:
	# 	b = threading.Thread(name='scan_intraday_background', target=scan_intraday_background, args=[s, stocks, indicator])
	# 	b.start()

def scan_swing_results(df, signaldf, indicator, should_cache=True):
	if df is not None and len(df) > 0:
		save_scan_results_archive(df, signaldf,ResponseType.History, indicator, should_cache)
		default_logger().debug("\nAll Stocks LTP and Signals:\n" + df.to_string(index=False))
	else:
		print('Nothing to show here.')
	if signaldf is not None and len(signaldf) > 0:
		print("\nWe recommend taking the following BUY/SELL positions for swingh trading. Swing Signals:\n" + signaldf.to_string(index=False))
	else:
		print('No signals to show here.')
	click.secho('Swing scanning finished.', fg='green', nl=True)

def format_beautified(orgdata, general, ohlc, wk52, volume, orderbook):
	primary, name_data, quote_data, ohlc_data, wk52_data, volume_data, pipeline_data = get_data_list(orgdata)
	frames = []
	if general:
		frames = add_frame(frames, name_data, NAME_LIST)
	frames = add_frame(frames, quote_data, QUOTE_LIST)
	if ohlc:
		frames = add_frame(frames, ohlc_data, OHLC_LIST)
	if wk52:
		frames = add_frame(frames, wk52_data, WK52_LIST)
	if volume:
		frames = add_frame(frames, volume_data, VOLUME_LIST)
	click.secho('------------------------------------------', fg='green', nl=True)
	click.echo(pd.concat(frames).to_string(index=True))
	if orderbook:
		dfpipeline = formatted_dataframe(pipeline_data, PIPELINE_LIST, indices=False)
		print('\n')
		click.echo(dfpipeline.to_string(index=False))
	click.secho('------------------------------------------', fg='red', nl=True)

def format_column(columnname, width):
	return columnname.ljust(width) + "|"

def add_frame(frames, list_data, column_names, should_transpose=True):
	df = formatted_dataframe(list_data, column_names)
	frames.append(df.transpose() if should_transpose else df)
	return frames

def formatted_dataframe(list_data, column_names, indices=True):
	columns =[]
	for column in column_names:
		columns.append(format_column(column,20))
	if indices:
		df = pd.DataFrame(list_data, columns = columns, index = [''])
	else:
		df = pd.DataFrame(list_data, columns = columns)
	return df

def clear_cache(clear, background, indicator, intraday = True, live = False, swing = False):
	response_type = ResponseType.Default
	response_type = ResponseType.Intraday if intraday else response_type
	response_type = ResponseType.Quote if live else response_type
	response_type = ResponseType.History if swing else response_type
	if clear or background:
		arch = archiver()
		df_file_name = 'df_Scan_Results.{}'.format(indicator)
		signaldf_file_name = 'signaldf_Scan_Results.{}'.format(indicator)
		arch.clearcache(df_file_name, response_type, force_clear=False)
		arch.clearcache(signaldf_file_name, response_type, force_clear=False)
		arch.clearcache(response_type=response_type, force_clear=False)

def live_quote_background(symbol, general, ohlc, wk52, volume, orderbook, terminate_after_iter=0, wait_time=60):
	global RUN_IN_BACKGROUND
	RUN_IN_BACKGROUND = True
	iteration = 0
	while RUN_IN_BACKGROUND:
		iteration = iteration + 1
		if terminate_after_iter > 0 and iteration >= terminate_after_iter:
			RUN_IN_BACKGROUND = False
			break
		result = get_quote(symbol)
		format_beautified(result, general, ohlc, wk52, volume, orderbook)
		time.sleep(wait_time)
	click.secho('Finished all iterations of scanning live quotes.', fg='green', nl=True)
	return iteration

def scan_live_background(scannerinstance, stocks, indicator, terminate_after_iter=0, wait_time=60):
	global RUN_IN_BACKGROUND
	RUN_IN_BACKGROUND = True
	iteration = 0
	while RUN_IN_BACKGROUND:
		iteration = iteration + 1
		if terminate_after_iter > 0 and iteration >= terminate_after_iter:
			RUN_IN_BACKGROUND = False
			break
		clear_cache(True, True, indicator, False, True, False)
		df, signaldf = scannerinstance.scan_live(stocks=stocks)
		scan_live_results(df, signaldf, indicator, should_cache=False)
		time.sleep(wait_time)
	click.secho('Finished all iterations of scanning live stocks.', fg='green', nl=True)
	return iteration

def scan_intraday_background(scannerinstance, stocks, indicator, terminate_after_iter=0, wait_time=10):
	global RUN_IN_BACKGROUND
	RUN_IN_BACKGROUND = True
	iteration = 0
	while RUN_IN_BACKGROUND:
		iteration = iteration + 1
		if terminate_after_iter > 0 and iteration >= terminate_after_iter:
			RUN_IN_BACKGROUND = False
			break
		clear_cache(True, True, indicator, True, False, False)
		df, signaldf = scannerinstance.scan_intraday(stocks=stocks)
		scan_intraday_results(df, signaldf, indicator, should_cache= False)
		time.sleep(wait_time)
	click.secho('Finished all iterations of scanning intraday.', fg='green', nl=True)
	return iteration
