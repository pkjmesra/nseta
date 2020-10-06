import click
import pandas as pd 

from nseta.live.live import get_quote
from nseta.cli.inputs import *
from datetime import datetime


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
    company_name = data['companyName']
    last_trade_price = data['lastPrice']
    price_change = data['pChange']
    o = data['open']
    h = data['dayHigh']
    l = data['dayLow']
    c = data['closePrice']
    prev_close = data['previousClose']
    wk52_high = data['high52']
    wk52_low = data['low52']
    quote_data = [[company_name, last_trade_price, price_change, o, h, l, c, prev_close, wk52_high, wk52_low]]

    traded_qty = data['quantityTraded']
    traded_volume = data['totalTradedVolume']
    traded_value = data['totalTradedValue']
    volume_data = [[traded_qty, traded_volume, traded_value]]

    sellQuantity5 = data['sellQuantity5']
    sellQuantity4 = data['sellQuantity4']
    sellQuantity3 = data['sellQuantity3']
    sellQuantity2 = data['sellQuantity2']
    sellQuantity1 = data['sellQuantity1']
    buyQuantity5 = data['buyQuantity5']
    buyQuantity4 = data['buyQuantity4']
    buyQuantity3 = data['buyQuantity3']
    buyQuantity2 = data['buyQuantity2']
    buyQuantity1 = data['buyQuantity1']
    
    buyPrice1 = data['buyPrice1']
    buyPrice2 = data['buyPrice2']
    buyPrice3 = data['buyPrice3']
    buyPrice4 = data['buyPrice4']
    buyPrice5 = data['buyPrice5']
    sellPrice1 = data['sellPrice1']
    sellPrice2 = data['sellPrice2']
    sellPrice3 = data['sellPrice3']
    sellPrice4 = data['sellPrice4']
    sellPrice5 = data['sellPrice5']
    pipeline_data = [[buyQuantity1, buyPrice1, sellQuantity1, sellPrice1],
                    [buyQuantity2, buyPrice2, sellQuantity2, sellPrice2],
                    [buyQuantity3, buyPrice3, sellQuantity3, sellPrice3],
                    [buyQuantity4, buyPrice4, sellQuantity4, sellPrice4],
                    [buyQuantity5, buyPrice5, sellQuantity5, sellPrice5]]

    dfquote = pd.DataFrame(quote_data, columns = ['Name', 'Last Trade Price', 'Price Change', 
        'Open', 'High', 'Low', 'Close', 'Prev Close', '52 wk High', '52 wk Low'])
    dfquote.set_index('Name', inplace=True)
    dfvolume = pd.DataFrame(volume_data, columns = ['Quantity Traded','Total Traded Volume', 'Total Traded Value'])
    dfvolume.set_index('Quantity Traded', inplace=True) 
    dfpipeline = pd.DataFrame(pipeline_data, columns = ['Bid Quantity','Bid Price', 'Offer Quantity', 'Offer Price'])
    dfpipeline.set_index('Bid Quantity', inplace=True) 
    print ('As of ' + time + '\n')
    print (dfquote.head())
    print ('\n')
    print (dfvolume.head())
    print ('\n')
    print (dfpipeline.head())
    print ('\n')
    