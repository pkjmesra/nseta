from nseta.strategy.strategy import *
from nseta.strategy.rsiSignalStrategy import *
from nseta.strategy.bbandsSignalStrategy import *
from nseta.plots.plots import plot_rsi
from nseta.common.history import *
from nseta.common.ti import ti
from nseta.scanner.tiscanner import scanner
from nseta.common.log import tracelog, default_logger
from nseta.cli.inputs import *
from nseta.scanner.tiscanner import scanner
from nseta.archives.archiver import *

import click
from datetime import datetime

__all__ = ['test_trading_strategy', 'forecast_strategy']

@tracelog
def smac_strategy(df, autosearch, lower, upper):
	if not autosearch:
		backtest_smac_strategy(df, fast_period=10, slow_period=50)
	else:
		backtest_smac_strategy(df, fast_period=range(10, 30), slow_period=range(40, 50))

@tracelog
def emac_strategy(df, autosearch, lower, upper):
	if not autosearch:
		backtest_emac_strategy(df, fast_period=9, slow_period=50)
	else:
		backtest_emac_strategy(df, fast_period=range(9, 30), slow_period=range(40, 50))

@tracelog
def bbands_strategy(df, autosearch, lower, upper):
	backtest_bbands_strategy(df, period=20, devfactor=2.0)

@tracelog
def rsi_strategy(df, autosearch, lower=30, upper=70):
	if not autosearch:
		if lower is None:
			lower = 30
		if upper is None:
			upper = 70
		backtest_rsi_strategy(df, rsi_period=14, rsi_lower=lower, rsi_upper=upper)
	else:
		backtest_rsi_strategy(df, rsi_period=[7,14], rsi_lower=[15,30], rsi_upper=[70,80] )

@tracelog
def macd_strategy(df, autosearch, lower, upper):
	if not autosearch:
		backtest_macd_strategy(df, fast_period=12, slow_period=26)
	else:
		backtest_macd_strategy(df, fast_period=range(4, 12, 2), slow_period=range(14, 26, 2))

@tracelog
def multi_strategy(df, autosearch, lower, upper):
	if not autosearch:
		SAMPLE_STRAT_DICT = {
			"smac": {"fast_period": 10, "slow_period": 50},
			"rsi": {"rsi_lower": 30, "rsi_upper": 70},
		}
		results = backtest_multi_strategy(df, SAMPLE_STRAT_DICT)
		print(results[['smac.fast_period', 'smac.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
	else:
		SAMPLE_STRAT_DICT = {
			"smac": {"fast_period": 10, "slow_period": [40, 50]},
			"emac": {"fast_period": 9, "slow_period": [40, 50]},
			"macd": {"fast_period": 12, "slow_period": [26, 40]},
			"rsi": {"rsi_lower": [15, 20], "rsi_upper": [70, 80]},
		}
		results = backtest_multi_strategy(df, SAMPLE_STRAT_DICT)
		print(results[['smac.fast_period', 'smac.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
		print ('\n')
		print(results[['emac.fast_period', 'emac.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
		print('\n')
		print(results[['macd.fast_period', 'macd.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
		print('\n')

STRATEGY_MAPPING = {
	"rsi": rsi_strategy,
	"smac": smac_strategy,
	# "base": BaseStrategy,
	"macd": macd_strategy,
	"emac": emac_strategy,
	"bbands": bbands_strategy,
	# "buynhold": BuyAndHoldStrategy,
	# "sentiment": SentimentStrategy,
	# "custom": CustomStrategy,
	# "ternary": TernaryStrategy,
	"multi": multi_strategy
}

STRATEGY_MAPPING_KEYS = list(STRATEGY_MAPPING.keys()) + ['custom']

@click.command(help='Measure the performance of your trading strategy')
@click.option('--symbol', '-S',  help='Security code')
@click.option('--start', '-s', help='Start date in yyyy-mm-dd format')
@click.option('--end', '-e', help='End date in yyyy-mm-dd format')
@click.option('--strategy', default='rsi', type=click.Choice(STRATEGY_MAPPING_KEYS),
	help=', '.join(STRATEGY_MAPPING_KEYS) + ". Choose one.")
@click.option('--upper', '-u', help='Used as upper limit, for example, for RSI. Only when strategy is "custom", we buy the security when the predicted next day return is > +{upper} %')
@click.option('--lower', '-l', help='Used as lower limit, for example, for RSI. Only when strategy is "custom", we sell the security when the predicted next day return is < -{lower} %')
@click.option('--autosearch/--no-autosearch', default=False, 
	help='--auto for allowing to automatically measure the performance of your trading strategy on multiple combinations of parameters.')
@click.option('--clear', '-c', default=False, is_flag=True, help='Clears the cached data for the given options.')
@click.option('--intraday', '-i', is_flag=True, help='Test trading strategy for the current intraday price history (Optional)')
@tracelog
def test_trading_strategy(symbol, start, end, autosearch, strategy, upper, lower, clear, intraday=False):
	if not intraday:
		if not validate_inputs(start, end, symbol, strategy):
			print_help_msg(test_trading_strategy)
			return
		sd = datetime.strptime(start, "%Y-%m-%d").date()
		ed = datetime.strptime(end, "%Y-%m-%d").date()
	try:
		if lower is None:
			lower = 25
		if upper is None:
			upper = 75
		if clear:
			arch = archiver()
			arch.clearcache(response_type=ResponseType.Intraday if intraday else ResponseType.History, force_clear=True)
		if intraday:
			test_intraday_trading_strategy(symbol, strategy, autosearch, lower, upper)
		else:
			test_historical_trading_strategy(symbol, sd, ed, strategy, autosearch, lower, upper)
	except Exception as e:
		default_logger().error(e, exc_info=True)
		click.secho('Failed to test trading strategy. Please check the inputs.', fg='red', nl=True)
		return
	except SystemExit:
		pass

@click.command(help='Forecast & measure performance of a trading model')
@click.option('--symbol', '-S',  help='Security code')
@click.option('--start', '-s', help='Start date in yyyy-mm-dd format')
@click.option('--end', '-e', help='End date in yyyy-mm-dd format')
@click.option('--strategy', default='rsi', type=click.Choice(STRATEGY_MAPPING_KEYS), 
	help=', '.join(STRATEGY_MAPPING_KEYS) + ". Choose one.")
@click.option('--upper', '-u', default=1.5, help='Only when strategy is "custom". We buy the security when the predicted next day return is > +{upper} %')
@click.option('--lower', '-l', default=1.5, help='Only when strategy is "custom". We sell the security when the predicted next day return is < -{lower} %')
@click.option('--clear', '-c', default=False, is_flag=True, help='Clears the cached data for the given options.')
@tracelog
def forecast_strategy(symbol, start, end, strategy, upper, lower, clear):
	if not validate_inputs(start, end, symbol, strategy):
		print_help_msg(forecast_strategy)
		return
	sd = datetime.strptime(start, "%Y-%m-%d").date()
	ed = datetime.strptime(end, "%Y-%m-%d").date()
	try:
		if clear:
			arch = archiver()
			arch.clearcache(response_type=ResponseType.History, force_clear=True)
		df = get_historical_dataframe(symbol, sd, ed)
		df = prepare_for_historical_strategy(df, symbol)
		plt, result = daily_forecast(df, symbol, strategy, upper_limit=float(upper), lower_limit=float(lower), periods=7)
		if plt is not None:
			plt.show()
	except Exception as e:
		default_logger().error(e, exc_info=True)
		click.secho('Failed to forecast trading strategy. Please check the inputs.', fg='red', nl=True)
		return
	except SystemExit:
		pass

def test_intraday_trading_strategy(symbol, strategy, autosearch, lower, upper):
	df = get_intraday_dataframe(symbol, strategy)
	if df is not None and len(df) > 0:
		run_test_strategy(df, symbol, strategy, autosearch, lower, upper)
		test_intraday_signals(df, lower, upper, strategy)

def get_intraday_dataframe(symbol, strategy):
	s = scanner(strategy)
	df = s.ohlc_intraday_history(symbol)
	# df = map_keys(df)
	# try:
	# 	if df is not None and len(df) > 0:
	# 		for key in INTRADAY_EQUITY_HEADERS:
	# 			if key in df.keys():
	# 				df.drop([key], axis = 1, inplace = True)
	# except Exception as e:
	# 	default_logger().debug(e, exc_info=True)
	# 	pass
	return df

def run_test_strategy(df, symbol, strategy, autosearch, lower, upper):
	strategy = strategy.lower()
	if strategy in STRATEGY_MAPPING:
		STRATEGY_MAPPING[strategy](df, autosearch, float(lower), float(upper))
	elif strategy == 'custom':
		df = prepare_for_historical_strategy(df, symbol)
		backtest_custom_strategy(df, symbol, strategy, upper_limit=float(upper), lower_limit=float(lower))
	else:
		STRATEGY_MAPPING['rsi'](df, autosearch, float(upper), float(lower))

def test_intraday_signals(df, lower, upper, strategy):
	tiinstance = ti()
	df = tiinstance.update_ti(df)
	if strategy.lower() == 'rsi':
		rsisignal = rsiSignalStrategy()
		rsisignal.set_limits(lower, upper)
		results = rsisignal.test_strategy(df)
		print("\n{}\n".format(results.to_string(index=False)))
		(plot_rsi(df)).show()
	elif strategy.lower() == 'bbands':
		bbandsSignal = bbandsSignalStrategy()
		results = bbandsSignal.test_strategy(df)
		print("\n{}\n".format(results.to_string(index=False)))

def get_historical_dataframe(symbol, sd, ed):
	historyinstance = historicaldata()
	df = historyinstance.daily_ohlc_history(symbol, sd, ed)
	df['datetime'] = df['Date']
	return df

def test_historical_trading_strategy(symbol, sd, ed, strategy, autosearch, lower, upper):
	df = get_historical_dataframe(symbol, sd, ed)
	run_test_strategy(df, symbol, strategy, autosearch, lower, upper)

def prepare_for_historical_strategy(df, symbol):
	tiscanner = scanner()
	# df = tiscanner.map_keys(df, symbol)
	df['datetime'] = df['Date']
	df['dt'] = df['Date']
	df['close'] = df['Close']
	df = reset_date_index(df)
	# df.drop(EQUITY_HEADERS, axis = 1, inplace = True)
	return df

def reset_date_index(df):
	df.set_index('dt', inplace=True)
	return df

# def map_keys(df):
# 	for key in KEY_MAPPING.keys():
# 		df[key] = df[KEY_MAPPING[key]]
# 	return df

