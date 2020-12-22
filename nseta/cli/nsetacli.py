import click, logging
import nseta
from nseta.cli.historycli import *
from nseta.cli.modelcli import *
from nseta.cli.plotscli import *
from nseta.cli.strategycli import *
from nseta.cli.livecli import *
from nseta.common import log

__all__ = ['nsetacli']

@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option('--debug/--no-debug', default=False, help='--debug to turn debugging on. Default is off')
@click.option('--version', is_flag=True, help='Shows the version of this library')
def nsetacli(debug, version):
	if debug:
		click.echo('Debug mode is %s' % ('on' if debug else 'off'))
		log.setup_custom_logger('nseta', logging.DEBUG)
	else:
		log.setup_custom_logger('nseta', logging.ERROR)
	if version:
		click.echo('nseta ' + nseta.__version__)

nsetacli.add_command(history)
nsetacli.add_command(pe_history)
nsetacli.add_command(plot_ta)
nsetacli.add_command(create_cdl_model)
nsetacli.add_command(test_trading_strategy)
nsetacli.add_command(forecast_strategy)
nsetacli.add_command(live_quote)


if __name__ == '__main__':
	nsetacli()
