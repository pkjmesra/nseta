# -*- coding: utf-8 -*-
import signal
import os
import warnings

import click, logging
import nseta
from nseta.cli.historycli import history, pe_history
from nseta.cli.modelcli import create_cdl_model
from nseta.cli.plotscli import plot_ta
from nseta.cli.strategycli import test_trading_strategy, forecast_strategy, scan_trading_strategy
from nseta.cli.livecli import live_quote, scan, top_picks, news
from nseta.common import log
from nseta.archives.archiver import archiver

__all__ = ['nsetacli']

@click.group(invoke_without_command=True, no_args_is_help=True)
@click.option('--debug/--no-debug', default=False, help='--debug to turn debugging on. Default is off')
@click.option('--resources', '-r', is_flag=True, help='Shows the resources directory path so you can navigate there and make changes to config and stocks list if you want to.')
@click.option('--version', '-v', is_flag=True, help='Shows the version of this library')
@click.option('--trace/--no-trace', default=False, help='--trace to turn tracing on (works only with --debug). Default is off.')
@click.option('--filter','-f', default=None, help='--filter <TEXT> to show only logs that match the filter text. Works only with --debug')
def nsetacli(debug, resources, version, trace, filter):
  signal.signal(signal.SIGINT, sigint_handler)
  arch = archiver()
  log_file_path = os.path.join(arch.logs_directory,'logs.log')
  if debug:
    click.echo('Debug mode is %s' % ('on' if debug else 'off'))
    if trace:
      click.echo('Tracing mode is %s' % ('on' if trace else 'off'))
    log.setup_custom_logger('nseta', logging.DEBUG, trace, log_file_path=log_file_path, filter=filter)
  else:
    log.setup_custom_logger('nseta', logging.INFO, log_file_path=log_file_path)
  if version:
    click.echo('nseta {}'.format(nseta.__version__))
  if resources:
    click.echo('#### nseta {} ####\n'.format(nseta.__version__))
    click.echo('Please check the default "config.txt" and "stocks.txt" files and edit as per your needs. These are under: \n {}\n'.format(arch.resources_directory))
    click.echo('If you would instead like to just scan for your own user defined stocks/tickers (as per NSE ticker name), please edit "userStocks.txt" file. This is under: \n {}\n'.format(arch.userData_directory))
    click.echo('All the log files and stocks data is downloaded under: \n {}\n'.format(arch.userData_directory))


@click.command(help='Force clears log files, downloaded contents etc. As good as a fresh install (with --deepclean option.)')
@click.option('--deepclean','-d', default=False, is_flag=True, help='--deepclean if you want all files removed.')
def clear(deepclean):
  arch = archiver()
  arch.clear_all(deep_clean=deepclean)
  if deepclean:
    click.secho('Removed all log files, contents and downloaded/saved files.', fg='green', nl=True)
  else:
    click.secho('Removed top-level results that were saved earlier.', fg='yellow', nl=True)

nsetacli.add_command(clear)
nsetacli.add_command(create_cdl_model)
nsetacli.add_command(forecast_strategy)
nsetacli.add_command(history)
nsetacli.add_command(live_quote)
nsetacli.add_command(news)
nsetacli.add_command(pe_history)
nsetacli.add_command(plot_ta)
nsetacli.add_command(scan)
nsetacli.add_command(test_trading_strategy)
nsetacli.add_command(top_picks)
nsetacli.add_command(scan_trading_strategy)


def sigint_handler(signum, frame):
  warnings.filterwarnings('ignore')
  warnings.simplefilter('ignore')
  click.secho('[sigint_handler] Keyboard Interrupt received. Exiting.', fg='red', nl=True)
  signal.signal(signum, signal.SIG_DFL)
  os.kill(os.getpid(), signum)

if __name__ == '__main__':
  nsetacli()
