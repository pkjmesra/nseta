import click
import pandas as pd 

from nseta.live.live import get_quote
from nseta.cli.inputs import *
from datetime import datetime

QUOTE_KEYS = ['companyName', 'lastPrice', 'pChange', 'open', 'dayHigh', 'dayLow', 'closePrice', 'previousClose', 'high52', 'low52']
VOLUME_KEYS = ['quantityTraded', 'totalTradedVolume', 'totalTradedValue']

@click.command(help='Get live price quote of a security')
@click.option('--symbol', '-S',  help='Security code')
@click.option('--series', default='EQ', help='Default series - EQ (Equity)')
def live_quote(symbol, series):
    if not validate_symbol(symbol):
        print_help_msg(live_quote)
        return
    result = get_quote(symbol)
    if len(result['data']) == 0:
        click.secho("Please check the inputs. Could not fetch the data.", fg='red', nl=True)
        return
    data = result['data'][0]
    time = result['lastUpdateTime']
    quote_data = []
    for key in QUOTE_KEYS:
        quote_data.append(data[key])
    quote_data = [quote_data]

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
            row.append(data[column])
        pipeline_data.append(row)

    dfquote = pd.DataFrame(quote_data, columns = ['Name', 'Last_Trade_Price', 'Price_Change', 
        'Open', 'High', 'Low', 'Close', 'Prev_Close', '52wk_High', '52wk_Low'])
    dfquote.set_index('Name', inplace=True)
    dfvolume = pd.DataFrame(volume_data, columns = ['Quantity_Traded','Total_Traded_Volume', 'Total_Traded_Value'])
    dfvolume.set_index('Quantity_Traded', inplace=True) 
    dfpipeline = pd.DataFrame(pipeline_data, columns = ['Bid_Quantity','Bid_Price', 'Offer_Quantity', 'Offer_Price'])
    dfpipeline.set_index('Bid_Quantity', inplace=True) 
    print ('As of ' + time + '\n')
    print (dfquote.head())
    print ('\n')
    print (dfvolume.head())
    print ('\n')
    print (dfpipeline.head())
    print ('\n')
    