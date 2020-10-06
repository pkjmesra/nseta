import click
from datetime import datetime

def validate_inputs(start, end,symbol):
    try:
        sd = datetime.strptime(start, "%Y-%m-%d").date()
        ed = datetime.strptime(end, "%Y-%m-%d").date()
    except:
        click.secho("Please provide start and end date in format yyyy-mm-dd", fg='red', nl=True)
        return False
    return validate_symbol(symbol)

def print_help_msg(command):
    with click.Context(command) as ctx:
        click.echo(command.get_help(ctx))

def validate_symbol(symbol):
    if not symbol:
        click.secho("Please provide security/index code", fg='red', nl=True)
        return False
    return True
