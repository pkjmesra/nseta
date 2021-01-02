import click
import pandas as pd
import threading, time

from nseta.live.live import get_quote, get_live_quote, get_data_list
from nseta.scanner.tiscanner import scanner
from nseta.cli.inputs import *
from nseta.plots.plots import plot_technical_indicators
from nseta.common.log import tracelog, default_logger
from datetime import datetime, date

__all__ = ['live_quote', 'live_intraday']

NAME_LIST = ['Symbol', 'Name', 'ISIN']
QUOTE_LIST = ['Last Updated', 'Prev Close', 'Last Trade Price','Change','% Change', 'Avg. Price', 'Upper Band','Lower Band']
OHLC_LIST = ['Open', 'High', 'Low', 'Close']
WK52_LIST = ['52 Wk High', '52 Wk Low']
VOLUME_LIST = ['Quantity Traded', 'Total Traded Volume', 'Total Traded Value', 'Delivery Volume', '% Delivery']
PIPELINE_LIST = ['Bid Quantity', 'Bid Price', 'Offer_Quantity', 'Offer_Price']
RUN_IN_BACKGROUND = True

@click.command(help='Get live price quote of a security')
@click.option('--symbol', '-S',  help='Security code. Pass [] with --intraday for scanning.')
@click.option('--general', '-g', default=False, is_flag=True, help='Get the general (Name, ISIN) details also (Optional)')
@click.option('--ohlc', '-o', default=False, is_flag=True, help='Get the OHLC values also (Optional)')
@click.option('--wk52', '-w' ,default=False, is_flag=True, help='Get the 52 week high/low values also (Optional)')
@click.option('--volume', '-v', default=False, is_flag=True, help='Get the traded volume details also (Optional)')
@click.option('--orderbook', '-b', default=False, is_flag=True, help='Get the current bid/offer details also (Optional)')
@click.option('--plot', '-p', default=False, is_flag=True, help='Plot the "Close" values (Optional)')
@click.option('--background', '-r', default=False, is_flag=True, help='Keep running the process in the background (Optional)')
@tracelog
def live_quote(symbol, general, ohlc, wk52, volume, orderbook, plot, background):
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
	except KeyboardInterrupt as e:
		RUN_IN_BACKGROUND = False
		default_logger().error(e, exc_info=True)
		click.secho('[live_quote] Keyboard Interrupt received. Exiting.', fg='red', nl=True)
		try:
			sys.exit(e.args[0][0]["code"])
		except SystemExit as se:
			os._exit(se.args[0][0]["code"])
		return
	except Exception as e:
		RUN_IN_BACKGROUND = False
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to fetch live quote', fg='red', nl=True)
		return
	except SystemExit:
		RUN_IN_BACKGROUND = False
		return

@click.command(help='Scan live price quotes and calculate RSI for stocks.')
@click.option('--stocks', '-S', default=[], help='Comma separated security codes(Optional. Configure the tickers in stocks.py)')
@click.option('--live', '-l', default=False, is_flag=True, help='Scans the live-quote and lists those that meet the signal criteria. Works best with --background.')
@click.option('--intraday', '-i', default=False, is_flag=True, help='Scans the intraday price history and lists those that meet the signal criteria')
@click.option('--background', '-r', default=False, is_flag=True, help='Keep running the process in the background (Optional)')
@tracelog
def scan(stocks, live, intraday, background):
	if live and intraday:
		click.secho('Choose only one of --live or --intraday options.', fg='red', nl=True)
		return
	elif not live and not intraday:
		click.secho('Choose at least one of the --live or --intraday (recommended) options.', fg='red', nl=True)
		return

	if stocks is not None and len(stocks) > 0:
		stocks = [x.strip() for x in stocks.split(',')]
	else:
		stocks = []
	global RUN_IN_BACKGROUND
	try:
		if live:
			scan_live(stocks, background)
		elif intraday:
			scan_intraday(stocks, background)
	except KeyboardInterrupt as e:
		RUN_IN_BACKGROUND = False
		default_logger().error(e, exc_info=True)
		click.secho('[scan] Keyboard Interrupt received. Exiting.', fg='red', nl=True)
		try:
			sys.exit(e.args[0][0]["code"])
		except SystemExit as se:
			os._exit(se.args[0][0]["code"])
		return
	except Exception as e:
		RUN_IN_BACKGROUND = False
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to scan.', fg='red', nl=True)
		return
	except SystemExit:
		RUN_IN_BACKGROUND = False
		return

def scan_live(stocks, background):
	s = scanner()
	s.scan(stocks=stocks)
	if background:
		b = threading.Thread(name='scan_live_background', target=scan_live_background, args=[s, stocks])
		b.start()

def scan_intraday(stocks, background):
	file_name = 'Scan_Results.csv'
	s = scanner()
	df, signaldf = s.scan_intraday(stocks=stocks)
	if df is not None and len(df) > 0:
		default_logger().info(df.to_string(index=False))
		df.to_csv(file_name)
		default_logger().info('Saved to: {}'.format(file_name))
		click.secho('Saved to: {}'.format(file_name), fg='green', nl=True)
		if plot:
			df.set_index('Date', inplace=True)
			plot_technical_indicators(df).show()
	if signaldf is not None and len(signaldf) > 0:
		click.echo(signaldf.to_string(index=False))
	if background:
		b = threading.Thread(name='scan_intraday_background', target=scan_intraday_background, args=[s, stocks])
		b.start()

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

def live_quote_background(symbol, general, ohlc, wk52, volume, orderbook):
	global RUN_IN_BACKGROUND
	RUN_IN_BACKGROUND = True
	while RUN_IN_BACKGROUND:
		result = get_quote(symbol)
		format_beautified(result, general, ohlc, wk52, volume, orderbook)
		time.sleep(1)

def scan_live_background(scannerinstance, stocks):
	global RUN_IN_BACKGROUND
	RUN_IN_BACKGROUND = True
	while RUN_IN_BACKGROUND:
		scannerinstance.scan(stocks)
		time.sleep(60)

def scan_intraday_background(scannerinstance, stocks):
	global RUN_IN_BACKGROUND
	RUN_IN_BACKGROUND = True
	while RUN_IN_BACKGROUND:
		df, signaldf = scannerinstance.scan_intraday(stocks=stocks)
		if signaldf is not None and len(signaldf) > 0:
			click.echo(signaldf.to_string(index=False))
		time.sleep(15)
