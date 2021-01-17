import click
from datetime import datetime, timedelta
from nseta.common.log import tracelog, default_logger

__all__ = ['validate_inputs', 'print_help_msg', 'validate_symbol']

STRATEGY_DAYS_MAPPING = {
	"rsi": 20,
	"smac": 63,
	"macd": 50,
	"emac": 63,
	"bbands": 28,
	"multi": 63,
	"custom": 20,
}

@tracelog
def validate_inputs(start, end,symbol, strategy=None, skip_symbol=False):
	try:
		sd = datetime.strptime(start, "%Y-%m-%d").date()
		ed = datetime.strptime(end, "%Y-%m-%d").date()
		if strategy is not None:
			if timedelta(STRATEGY_DAYS_MAPPING[strategy.lower()]) > (ed-sd):
				click.secho("Please provide start and end date with a time delta of at least " + str(STRATEGY_DAYS_MAPPING[strategy.lower()]) + " days for the selected strategy.", fg='red', nl=True)
				return False
	except Exception as e:
		default_logger().debug(e, exc_info=True)
		click.secho("Please provide start and end date in format yyyy-mm-dd", fg='red', nl=True)
		return False
	except SystemExit:
		pass
	return True if skip_symbol else validate_symbol(symbol)

@tracelog
def print_help_msg(command):
	with click.Context(command) as ctx:
		click.echo(command.get_help(ctx))

@tracelog
def validate_symbol(symbol):
	if not symbol:
		click.secho("Please provide security/index code", fg='red', nl=True)
		return False
	return True
