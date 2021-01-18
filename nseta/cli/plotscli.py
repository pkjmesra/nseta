
from nseta.common.history import historicaldata
from nseta.common.log import tracelog, default_logger
from nseta.plots.plots import *
from nseta.cli.inputs import *
from nseta.archives.archiver import *

import click
from datetime import datetime

__all__ = ['plot_ta']

PLOT_KEY_TO_FUNC = {"ALL": plot_technical_indicators,
			   "PRICE": plot_history,
			   "RSI": plot_rsi,
			   "EMA": plot_ema,
			   "SMA": plot_sma,
			   "SSTO": plot_sstochastic,
			   "FSTO": plot_fstochastic,
			   "ADX": plot_adx,
			   "MACD": plot_macd,
			   "MOM": plot_mom,
			   "DMI": plot_dmi,
			   "BBANDS": plot_bbands}
PLOT_TI_KEYS = list(PLOT_KEY_TO_FUNC.keys())

@click.command(help='Plot various technical analysis indicators')
@click.option('--symbol', '-S',  help='Security code')
@click.option('--start', '-s', help='Start date in yyyy-mm-dd format')
@click.option('--end', '-e', help='End date in yyyy-mm-dd format')
@click.option('--clear', '-c', default=False, is_flag=True, help='Clears the cached data for the given options.')
@click.option('--plot-type', '-p','plot_type', default='ALL', help=', '.join(PLOT_TI_KEYS) + ". Choose one.")
@tracelog
def plot_ta(symbol, start, end, clear, plot_type="ALL"):
	if not validate_inputs(start, end, symbol):
		print_help_msg(plot_ta)
		return
	sd = datetime.strptime(start, "%Y-%m-%d").date()
	ed = datetime.strptime(end, "%Y-%m-%d").date()

	try:
		if clear:
			arch = archiver()
			arch.clearcache(response_type=ResponseType.History, force_clear=False)
		historyinstance = historicaldata()
		df = historyinstance.daily_ohlc_history(symbol, sd, ed, type=ResponseType.History)
		df['dt'] = df['Date']
		df.set_index('Date', inplace=True)
		plot_type = plot_type.upper()
		if plot_type in PLOT_KEY_TO_FUNC:
			PLOT_KEY_TO_FUNC[plot_type](df).show()
		else:
			PLOT_KEY_TO_FUNC['ALL'](df).show()
		click.secho('Technical indicator(s): {}, plotted.'.format(plot_type), fg='green', nl=True)
	except Exception as e:
		default_logger().debug(e, exc_info=True)
		click.secho('Failed to plot technical indicators', fg='red', nl=True)
		return
	except SystemExit:
		pass
