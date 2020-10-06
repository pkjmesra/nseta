
from nseta.common.history import get_history
from nseta.plots.plots import *
from nseta.cli.inputs import *

import click
from datetime import datetime

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
@click.option('--plot-type', '-p','plot_type', default='ALL', help=', '.join(PLOT_TI_KEYS) + ". Choose one.")
def plot_ta(symbol, start, end, plot_type="ALL"):
	if not validate_inputs(start, end, symbol):
		print_help_msg(plot_ta)
		return
	sd = datetime.strptime(start, "%Y-%m-%d").date()
	ed = datetime.strptime(end, "%Y-%m-%d").date()

	df = get_history(symbol, sd, ed)
	df.set_index('Date', inplace=True)
	plot_type = plot_type.upper()
	if plot_type in PLOT_KEY_TO_FUNC:
		PLOT_KEY_TO_FUNC[plot_type](df).show()
	else:
		PLOT_KEY_TO_FUNC['ALL'](df).show()
