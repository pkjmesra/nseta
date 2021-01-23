from nseta.analytics.model import *
from nseta.common.history import historicaldata
from nseta.common.log import tracelog, default_logger
from nseta.plots.plots import *
from nseta.cli.inputs import *
from nseta.archives.archiver import *

import click
from datetime import datetime

__all__ = ['create_cdl_model']

@click.command(help='Create candlestick model.Plot uncovered patterns')
@click.option('--symbol', '-S',  help='Security code')
@click.option('--start', '-s', help='Start date in yyyy-mm-dd format')
@click.option('--end', '-e', help='End date in yyyy-mm-dd format')
@click.option('--file', '-o', 'file_name',  help='Output file name. Default is {symbol}.csv')
@click.option('--steps/--no-steps', default=False, help='--steps for saving intermediate steps in output file')
@click.option('--clear', '-c', default=False, is_flag=True, help='Clears the cached data for the given options.')
@click.option('--format', '-f', default='csv',  type=click.Choice(['csv', 'pkl']),
				help='Output format, pkl - to save as Pickel and csv - to save as csv')
@tracelog
def create_cdl_model(symbol, start, end, file_name, steps, clear, format):
	if not validate_inputs(start, end, symbol):
		print_help_msg(create_cdl_model)
		return
	sd = datetime.strptime(start, "%Y-%m-%d").date()
	ed = datetime.strptime(end, "%Y-%m-%d").date()

	try:
		if clear:
			arch = archiver()
			arch.clearcache(response_type=ResponseType.History, force_clear=False)
		historyinstance = historicaldata()
		df = historyinstance.daily_ohlc_history(symbol, sd, ed, type=ResponseType.History)
		df = df.sort_values(by='Date',ascending=True)
		df.set_index('Date', inplace=True)
		df = model_candlestick(df, steps)
		click.echo(df.to_string(index=False))
	except Exception as e:
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to create candlestick model', fg='red', nl=True)
		return
	except SystemExit:
		pass

	if not file_name:
		file_name = symbol + '.' + format
	if format == 'csv':
		df.to_csv(file_name)
	else:
		df.to_pickle(file_name)
	default_logger().debug('Model saved to: {}'.format(file_name))
	default_logger().debug('Candlestick pattern model plot saved to: {}'.format(symbol +'_candles.html'))
	click.secho('Model saved to: {}'.format(file_name), fg='green', nl=True)
	try:
		plot_candlestick(df, symbol, 'Candlestick Pattern Model Recognition for ' + symbol)
		click.secho('Candlestick pattern model plot saved to: {}'.format(symbol +'_candles.html'), fg='green', nl=True)	
	except Exception as e:
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to plot candlestick pattern for the model', fg='red', nl=True)
		return
	except SystemExit:
		pass
