import click
import pandas as pd
import threading, time

from nseta.live.live import get_quote, get_live_quote, get_data_list
from nseta.scanner.tiscanner import scanner
from nseta.cli.inputs import *
from nseta.plots.plots import plot_technical_indicators
from nseta.common.log import logdebug, default_logger
from datetime import datetime, date

__all__ = ['live_quote', 'live_intraday']

RUN_IN_BACKGROUND = True

@click.command(help='Get live price quote of a security')
@click.option('--symbol', '-S',  help='Security code. Pass [] with --intraday for scanning.')
@click.option('--series', default='EQ', help='Default series - EQ (Equity) (Optional)')
@click.option('--general', '-g', default=False, is_flag=True, help='Get the general (Name, ISIN) details also (Optional)')
@click.option('--ohlc', '-o', default=False, is_flag=True, help='Get the OHLC values also (Optional)')
@click.option('--wk52', '-w' ,default=False, is_flag=True, help='Get the 52 week high/low values also (Optional)')
@click.option('--volume', '-v', default=False, is_flag=True, help='Get the traded volume details also (Optional)')
@click.option('--orderbook', '-b', default=False, is_flag=True, help='Get the current bid/offer details also (Optional)')
@click.option('--intraday', '-i', default=False, is_flag=True, help='Get the current intraday price history (Optional)')
@click.option('--plot', '-p', default=False, is_flag=True, help='Plot the "Close" values (Optional)')
@click.option('--background', '-r', default=False, is_flag=True, help='Keep running the process in the background (Optional)')
@logdebug
def live_quote(symbol, series, general, ohlc, wk52, volume, orderbook, intraday, plot, background):
	if not validate_symbol(symbol):
		print_help_msg(live_quote)
		return
	global RUN_IN_BACKGROUND
	try:
		if (not intraday):
			orgdata, df = get_live_quote(symbol, general, ohlc, wk52, volume, orderbook)
			format_beautified(orgdata, general, ohlc, wk52, volume, orderbook)
			if background:
				b = threading.Thread(name='live_quote_background', target=live_quote_background, args=[symbol, general, ohlc, wk52, volume, orderbook])
				b.start()
		else:
			if symbol == '[]':
				stocks = []
				file_name = 'Scan_Results.csv'
			else:
				stocks = [symbol]
				file_name = symbol + '.csv'
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
				b = threading.Thread(name='live_quote_scan_background', target=live_quote_scan_background, args=[s, stocks])
				b.start()
	except KeyboardInterrupt:
		RUN_IN_BACKGROUND = False
	except Exception as e:
		default_logger().error(e, exc_info=True)
		click.secho('Failed to fetch live quote', fg='red', nl=True)
		return
	except SystemExit:
		pass

@click.command(help='Scan live price quotes and calculate RSI for stocks.')
@click.option('--stocks', '-S', help='Comma separated security codes(Optional. Configure the tickers in stocks.py)')
@click.option('--background', '-r', default=False, is_flag=True, help='Keep running the process in the background (Optional)')
@logdebug
def scan(stocks, background):
	if stocks is not None:
		stocks = [x.strip() for x in stocks.split(',')]
	else:
		stocks = []
	s = scanner()
	s.scan(stocks=stocks)
	if background:
		b = threading.Thread(name='scan_background', target=scan_background, args=[s, stocks])
		b.start()

def format_beautified(orgdata, general, ohlc, wk52, volume, orderbook):
	primary, name_data, quote_data, ohlc_data, wk52_data, volume_data, pipeline_data = get_data_list(orgdata)
	frames = []
	if general:
		dfname = pd.DataFrame(name_data, columns = ['Symbol              |','Name                |', 'ISIN                |'], index = ['']).transpose()
		frames.append(dfname)
	dfquote = pd.DataFrame(quote_data, columns = ['Last Updated        |', 'Prev Close          |', 'Last Trade Price    |', 'Change              |', '% Change            |', 'Avg. Price          |', 'Upper Band          |', 'Lower Band          |'], index = ['']).transpose()
	frames.append(dfquote)
	if ohlc:
		dfohlc = pd.DataFrame(ohlc_data, columns = ['Open                |', 'High                |', 'Low                 |', 'Close               |'], index = ['']).transpose()
		frames.append(dfohlc)
	if wk52:
		dfwk52 = pd.DataFrame(wk52_data, columns = ['52 Wk High          |', '52 Wk Low           |'], index = ['']).transpose()
		frames.append(dfwk52)
	if volume:
		dfvolume = pd.DataFrame(volume_data, columns = ['Quantity Traded     |','Total Traded Volume |', 'Total Traded Value  |', 'Delivery Volume     |', '% Delivery          |'], index = ['']).transpose()
		frames.append(dfvolume)
	click.secho('------------------------------------------', fg='green', nl=True)
	click.echo(pd.concat(frames).to_string(index=True))
	if orderbook:
		dfpipeline = pd.DataFrame(pipeline_data, columns = ['Bid Quantity    |','Bid Price       |', 'Offer_Quantity  |', 'Offer_Price'])
		print('\n')
		click.echo(dfpipeline.to_string(index=False))
	click.secho('------------------------------------------', fg='red', nl=True)

def live_quote_background(symbol, general, ohlc, wk52, volume, orderbook):
	global RUN_IN_BACKGROUND
	while RUN_IN_BACKGROUND:
		result = get_quote(symbol)
		format_beautified(result, general, ohlc, wk52, volume, orderbook)
		time.sleep(1)

def scan_background(scannerinstance, stocks):
	global RUN_IN_BACKGROUND
	while RUN_IN_BACKGROUND:
		scannerinstance.scan(stocks)
		time.sleep(60)

def live_quote_scan_background(scannerinstance, stocks):
	global RUN_IN_BACKGROUND
	while RUN_IN_BACKGROUND:
		df, signaldf = scannerinstance.scan_intraday(stocks=stocks)
		if signaldf is not None and len(signaldf) > 0:
			click.echo(signaldf.to_string(index=False))
		time.sleep(15)
