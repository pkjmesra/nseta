import click
from datetime import datetime

__all__ = ['validate_inputs', 'print_help_msg', 'validate_symbol']

def validate_inputs(start, end,symbol):
    try:
        datetime.strptime(start, "%Y-%m-%d").date()
        datetime.strptime(end, "%Y-%m-%d").date()
    except Exception:
        click.secho("Please provide start and end date in format yyyy-mm-dd", fg='red', nl=True)
        return False
    except SystemExit:
        pass
    return validate_symbol(symbol)

def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def validate_symbol(symbol):
    if not symbol:
        click.secho("Please provide security/index code", fg='red', nl=True)
        return False
    return True
