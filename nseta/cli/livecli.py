import click
import pandas as pd
import threading, time

from nseta.live.live import get_quote
from nseta.cli.inputs import *
from nseta.common.log import logdebug, default_logger
from datetime import datetime

__all__ = ['live_quote']

NAME_KEYS = ['companyName', 'isinCode']
QUOTE_KEYS = ['previousClose', 'lastPrice', 'change', 'pChange', 'averagePrice', 'pricebandupper', 'pricebandlower']
OHLC_KEYS = ['open', 'dayHigh', 'dayLow', 'closePrice']
WK52_KEYS = ['high52', 'low52']
VOLUME_KEYS = ['quantityTraded', 'totalTradedVolume', 'totalTradedValue', 'deliveryQuantity', 'deliveryToTradedQuantity']
RUN_IN_BACKGROUND = True

@click.command(help='Get live price quote of a security along with other (Optional) parameters')
@click.option('--symbol', '-S',  help='Security code')
@click.option('--series', default='EQ', help='Default series - EQ (Equity) (Optional)')
@click.option('--general', '-G', is_flag=True, help='Get the general (Name, ISIN) details also (Optional)')
@click.option('--ohlc', '-O', is_flag=True, help='Get the OHLC values also (Optional)')
@click.option('--wk52', '-W' ,is_flag=True, help='Get the 52 week high/low values also (Optional)')
@click.option('--volume', '-V', is_flag=True, help='Get the traded volume details also (Optional)')
@click.option('--orderbook', '-B', is_flag=True, help='Get the current bid/offer details also (Optional)')
@click.option('--background', '-R', is_flag=True, help='Keep running the process in the background (Optional)')
@logdebug
def live_quote(symbol, series, general, ohlc, wk52, volume, orderbook, background):
	if not validate_symbol(symbol):
		print_help_msg(live_quote)
		return

	try:
		result = get_quote(symbol)
		# print(result)
		if len(result['data']) == 0:
			default_logger().warn('Wrong or invalid inputs.')
			click.secho("Please check the inputs. Could not fetch the data.", fg='red', nl=True)
			return
		data = result['data'][0]
		time = result['lastUpdateTime']
		format_data(data, time, general, ohlc, wk52, volume, orderbook)
		if background:
			b = threading.Thread(name='live_quote_background', target=live_quote_background, args=[symbol, general, ohlc, wk52, volume, orderbook])
			b.start()
	except KeyboardInterrupt:
		RUN_IN_BACKGROUND = False
	except Exception as e:
		default_logger().error(e, exc_info=True)
		click.secho('Failed to fetch live quote', fg='red', nl=True)
		return
	except SystemExit:
		pass
	
def format_data(data, time, general, ohlc, wk52, volume, orderbook):
	name_data = []
	for key in NAME_KEYS:
		name_data.append(data[key])
	name_data = [name_data]

	quote_data = [time]
	for key in QUOTE_KEYS:
		quote_data.append(data[key])
	quote_data = [quote_data]

	ohlc_data = []
	for key in OHLC_KEYS:
		ohlc_data.append(data[key])
	ohlc_data = [ohlc_data]

	wk52_data = []
	for key in WK52_KEYS:
		wk52_data.append(data[key])
	wk52_data = [wk52_data]

	volume_data = []
	for key in VOLUME_KEYS:
		volume_data.append(data[key])
	volume_data = [volume_data]

	pipeline_data = []
	for x in range(1,5):
		buy_qty_key = 'buyQuantity' + str(x)
		buy_prc_key = 'buyPrice' + str(x)
		sell_qty_key = 'sellQuantity' + str(x)
		sell_prc_key = 'sellPrice' + str(x)
		columns = [buy_qty_key, buy_prc_key, sell_qty_key, sell_prc_key]
		row = []
		for column in columns:
			row.append(data[column] + "  ")
		pipeline_data.append(row)

	frames = []
	if general:
		dfname = pd.DataFrame(name_data, columns = ['Name                |', 'ISIN                |'], index = ['']).transpose()
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
	while RUN_IN_BACKGROUND:
		result = get_quote(symbol)
		data = result['data'][0]
		t = result['lastUpdateTime']
		format_data(data, t, general, ohlc, wk52, volume, orderbook)
		time.sleep(1)
