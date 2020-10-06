import click
from nseta.cli.historycli import *
from nseta.cli.modelcli import *
from nseta.cli.plotscli import *
from nseta.cli.strategycli import *
from nseta.cli.livecli import *

@click.group()
@click.option('--debug/--no-debug', default=False, help='--debug to turn debugging on. Default is off')
def nsetacli(debug):
    if debug:
        click.echo('Debug mode is %s' % ('on' if debug else 'off'))

nsetacli.add_command(history)
nsetacli.add_command(pe_history)
nsetacli.add_command(plot_ta)
nsetacli.add_command(create_cdl_model)
nsetacli.add_command(test_trading_strategy)
nsetacli.add_command(forecast_strategy)
nsetacli.add_command(live_quote)

if __name__ == '__main__':
    nsetacli()
