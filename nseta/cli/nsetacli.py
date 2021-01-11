import signal
import os
import warnings

import click, logging
import nseta
from nseta.cli.historycli import history, pe_history
from nseta.cli.modelcli import create_cdl_model
from nseta.cli.plotscli import plot_ta
from nseta.cli.strategycli import test_trading_strategy, forecast_strategy
from nseta.cli.livecli import live_quote, scan
from nseta.common import log

__all__ = ['nsetacli']

@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option('--debug/--no-debug', default=False, help='--debug to turn debugging on. Default is off')
@click.option('--version', is_flag=True, help='Shows the version of this library')
@click.option('--trace/--no-trace', default=False, help='--trace to turn tracing on (works only with --debug). Default is off.')
def nsetacli(debug, version, trace):
	signal.signal(signal.SIGINT, sigint_handler)
	if debug:
		click.echo('Debug mode is %s' % ('on' if debug else 'off'))
		if trace:
			click.echo('Tracing mode is %s' % ('on' if trace else 'off'))
		log.setup_custom_logger('nseta', logging.DEBUG, trace)
	else:
		log.setup_custom_logger('nseta', logging.INFO)
	if version:
		click.echo('nseta ' + nseta.__version__)

nsetacli.add_command(create_cdl_model)
nsetacli.add_command(forecast_strategy)
nsetacli.add_command(history)
nsetacli.add_command(live_quote)
nsetacli.add_command(pe_history)
nsetacli.add_command(plot_ta)
nsetacli.add_command(scan)
nsetacli.add_command(test_trading_strategy)

def sigint_handler(signum, frame):
	warnings.filterwarnings("ignore")
	warnings.simplefilter("ignore")
	click.secho('[sigint_handler] Keyboard Interrupt received. Exiting.', fg='red', nl=True)
	signal.signal(signum, signal.SIG_DFL)
	os.kill(os.getpid(), signum)

if __name__ == '__main__':
	nsetacli()
