from nseta.analytics.model import *
from nseta.common.history import get_history
from nseta.plots.plots import *
from nseta.cli.inputs import *

import click
from datetime import datetime

@click.command(help='Create candlestick model.Plot uncovered patterns')
@click.option('--symbol', '-S',  help='Security code')
@click.option('--start', '-s', help='Start date in yyyy-mm-dd format')
@click.option('--end', '-e', help='End date in yyyy-mm-dd format')
@click.option('--file', '-o', 'file_name',  help='Output file name. Default is {symbol}.csv')
@click.option('--steps/--no-steps', default=False, help='--steps for saving intermediate steps in output file')
@click.option('--format', '-f', default='csv',  type=click.Choice(['csv', 'pkl']),
                help='Output format, pkl - to save as Pickel and csv - to save as csv')
def create_cdl_model(symbol, start, end, file_name, steps, format):
	if not validate_inputs(start, end, symbol):
		print_help_msg(create_cdl_model)
		return
	sd = datetime.strptime(start, "%Y-%m-%d").date()
	ed = datetime.strptime(end, "%Y-%m-%d").date()

	df = get_history(symbol, sd, ed)
	df.set_index('Date', inplace=True)
	df = model_candlestick(df, steps)
	click.echo(df.head())
	if not file_name:
		file_name = symbol + '.' + format
	if format == 'csv':
		df.to_csv(file_name)
	else:
		df.to_pickle(file_name)
	click.secho('Model saved to: {}'.format(file_name), fg='green', nl=True)
	click.secho('Candlestick pattern model plot saved to: {}'.format(symbol +'_candles.html'), fg='green', nl=True)	
	plot_candlestick(df, symbol, 'Candlestick Pattern Model Recognition for ' + symbol)
