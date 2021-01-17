import pandas as pd

from nseta.strategy.strategy import *
from nseta.strategy.rsiSignalStrategy import *
from nseta.strategy.bbandsSignalStrategy import *
from nseta.strategy.macdSignalStrategy import *

from nseta.plots.plots import plot_rsi
from nseta.common.history import *
from nseta.common.ti import ti
from nseta.scanner.tiscanner import scanner
from nseta.common.log import tracelog, default_logger
from nseta.cli.inputs import *
from nseta.archives.archiver import *

import click
from datetime import datetime

__all__ = ['test_trading_strategy', 'forecast_strategy', 'scan_trading_strategy']

@tracelog
def smac_strategy(df, autosearch, lower, upper, plot=False):
	# if not autosearch:
	backtest_smac_strategy(df, fast_period=10, slow_period=50, plot=plot)
	# else:
	# 	backtest_smac_strategy(df, fast_period=range(10, 30), slow_period=range(40, 50))

@tracelog
def emac_strategy(df, autosearch, lower, upper, plot=False):
	# if not autosearch:
	backtest_emac_strategy(df, fast_period=9, slow_period=50, plot=plot)
	# else:
	# 	backtest_emac_strategy(df, fast_period=range(9, 30), slow_period=range(40, 50))

@tracelog
def bbands_strategy(df, autosearch, lower, upper, plot=False):
	backtest_bbands_strategy(df, period=20, devfactor=2.0)

@tracelog
def rsi_strategy(df, autosearch, lower=30, upper=70, plot=False):
	# if not autosearch:
	if lower is None:
		lower = 30
	if upper is None:
		upper = 70
	backtest_rsi_strategy(df, rsi_period=14, rsi_lower=lower, rsi_upper=upper, plot=plot)
	# else:
	# 	backtest_rsi_strategy(df, rsi_period=[7,14], rsi_lower=[15,30], rsi_upper=[70,80] )

@tracelog
def macd_strategy(df, autosearch, lower, upper, plot=False):
	# if not autosearch:
	backtest_macd_strategy(df, fast_period=12, slow_period=26, plot=plot)
	# else:
		# backtest_macd_strategy(df, fast_period=range(4, 12, 2), slow_period=range(14, 26, 2))

@tracelog
def multi_strategy(df, autosearch, lower, upper, plot=False):
	# if not autosearch:
	SAMPLE_STRAT_DICT = {
		"smac": {"fast_period": 10, "slow_period": 50},
		"rsi": {"rsi_lower": 30, "rsi_upper": 70},
	}
	results = backtest_multi_strategy(df, SAMPLE_STRAT_DICT, plot=plot)
	print(results[['smac.fast_period', 'smac.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
	# else:
	# 	SAMPLE_STRAT_DICT = {
	# 		"smac": {"fast_period": 10, "slow_period": [40, 50]},
	# 		"emac": {"fast_period": 9, "slow_period": [40, 50]},
	# 		"macd": {"fast_period": 12, "slow_period": [26, 40]},
	# 		"rsi": {"rsi_lower": [15, 20], "rsi_upper": [70, 80]},
	# 	}
	# 	results = backtest_multi_strategy(df, SAMPLE_STRAT_DICT)
	# 	print(results[['smac.fast_period', 'smac.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
	# 	print ('\n')
	# 	print(results[['emac.fast_period', 'emac.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
	# 	print('\n')
	# 	print(results[['macd.fast_period', 'macd.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
	# 	print('\n')

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
@click.option('--plot', '-p', default=False, is_flag=True, help='By default(False). --plot, if you would like the results to be plotted.')
@click.option('--intraday', '-i', is_flag=True, help='Test trading strategy for the current intraday price history (Optional)')
@tracelog
def test_trading_strategy(symbol, start, end, autosearch, strategy, upper, lower, clear, plot, intraday=False):
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

@click.command(help='Test/Measure the performance of your trading strategy for multiple stocks')
@click.option('--symbol', '-S',  help='Comma separated security codes. Skip/Leave empty for scanning all stocks in stocks.py.')
@click.option('--start', '-s', help='Start date in yyyy-mm-dd format')
@click.option('--end', '-e', help='End date in yyyy-mm-dd format')
@click.option('--strategy', default='rsi', type=click.Choice(STRATEGY_MAPPING_KEYS),
	help=', '.join(STRATEGY_MAPPING_KEYS) + ". Choose one.")
@click.option('--upper', '-u', help='Used as upper limit, for example, for RSI. Only when strategy is "custom", we buy the security when the predicted next day return is > +{upper} %')
@click.option('--lower', '-l', help='Used as lower limit, for example, for RSI. Only when strategy is "custom", we sell the security when the predicted next day return is < -{lower} %')
@click.option('--clear', '-c', default=False, is_flag=True, help='Clears the cached data for the given options.')
@click.option('--intraday', '-i', is_flag=True, help='Test trading strategy for the current intraday price history (Optional)')
@tracelog
def scan_trading_strategy(symbol, start, end, strategy, upper, lower, clear, intraday=False):
	if not intraday:
		if not validate_inputs(start, end, symbol, strategy, skip_symbol=True):
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
		scn = scanner()
		if symbol is not None and len(symbol) > 0:
			symbols = [x.strip() for x in symbol.split(',')]
		else:
			symbols = []
		stocks = scn.stocks_list(symbols)
		# strategies = ['rsi', 'macd', 'bbands']
		frames = []
		for stock in stocks:
			try:
				if intraday:
					summary = test_intraday_trading_strategy(stock, strategy, False, lower, upper, backtest_lib=False)
				else:
					summary = test_historical_trading_strategy(stock, sd, ed, strategy, False, lower, upper, backtest_lib=False)
				if summary is not None and len(summary) > 0:
					frames.append(summary)
			except Exception as e:
				default_logger().error(e, exc_info=True)
				click.secho('Failed to test trading strategy for symbol: {}.'.format(stock), fg='red', nl=True)
				continue
		full_summary = pd.concat(frames)
		if full_summary is not None and len(full_summary) > 0:
			print("\n{}\n".format(full_summary.to_string(index=False)))
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
@click.option('--plot', '-p', default=False, is_flag=True, help='By default(False). --plot, if you would like the results to be plotted.')
@tracelog
def forecast_strategy(symbol, start, end, strategy, upper, lower, clear, plot):
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
		plt, result = daily_forecast(df, symbol, strategy, upper_limit=float(upper), lower_limit=float(lower), periods=7, plot=plot)
		if plt is not None:
			plt.show()
	except Exception as e:
		default_logger().error(e, exc_info=True)
		click.secho('Failed to forecast trading strategy. Please check the inputs.', fg='red', nl=True)
		return
	except SystemExit:
		pass

def test_intraday_trading_strategy(symbol, strategy, autosearch, lower, upper, plot=False, backtest_lib=True):
	df = get_intraday_dataframe(symbol, strategy)
	if df is not None and len(df) > 0:
		if backtest_lib:
			run_test_strategy(df, symbol, strategy, autosearch, lower, upper, plot=plot)
		return test_signals(df, lower, upper, strategy, intraday=True, plot=plot, show_detail=backtest_lib)
	else:
		return None

@tracelog
def get_intraday_dataframe(symbol, strategy):
	s = scanner(strategy)
	df = s.ohlc_intraday_history(symbol)
	if df is not None and len(df) > 0:
		df = df.sort_values(by='Date',ascending=True)
	return df

def run_test_strategy(df, symbol, strategy, autosearch, lower, upper, plot=False):
	strategy = strategy.lower()
	if strategy in STRATEGY_MAPPING:
		STRATEGY_MAPPING[strategy](df, autosearch, float(lower), float(upper))
	elif strategy == 'custom':
		df = prepare_for_historical_strategy(df, symbol)
		backtest_custom_strategy(df, symbol, strategy, upper_limit=float(upper), lower_limit=float(lower))
	else:
		STRATEGY_MAPPING['rsi'](df, autosearch, float(upper), float(lower))

def test_signals(df, lower, upper, strategy, intraday = False, plot=False, show_detail=True):
	tiinstance = ti()
	df = tiinstance.update_ti(df)
	df = df.sort_values(by='Date',ascending=True)
	if strategy.lower() == 'rsi':
		df_rsi_dict = {'Symbol':df['Symbol'], 'Date':df['Date'], 'RSI':df['RSI'], 'Close':df['Close']}
		df_rsi = pd.DataFrame(df_rsi_dict)
		rsisignal = rsiSignalStrategy(strict=True, intraday=False)
		rsisignal.set_limits(lower, upper)
		results, summary = rsisignal.test_strategy(df_rsi)
		if plot:
			(plot_rsi(df)).show()
	elif strategy.lower() == 'bbands':
		df_bbands_dict = {'Symbol':df['Symbol'], 'Date':df['Date'], 'BBands-U':df['BBands-U'], 'BBands-M':df['BBands-M'], 'BBands-L':df['BBands-L'], 'Close':df['Close']}
		df_bbands = pd.DataFrame(df_bbands_dict)
		bbandsSignal = bbandsSignalStrategy(strict=False, intraday=False)
		results, summary = bbandsSignal.test_strategy(df_bbands)
	elif strategy.lower() == 'macd':
		df_macd_dict = {'Symbol':df['Symbol'], 'Date':df['Date'], 'macd(12)':df['macd(12)'], 'macdsignal(9)':df['macdsignal(9)'], 'macdhist(26)':df['macdhist(26)'], 'Close':df['Close']}
		df_macd = pd.DataFrame(df_macd_dict)
		macdSignal = macdSignalStrategy(strict=False, intraday=False)
		results, summary = macdSignal.test_strategy(df_macd)
	if results is not None and show_detail:
		print("\n{}\n".format(results.to_string(index=False)))
	if summary is not None and show_detail:
		print("\n{}\n".format(summary.to_string(index=False)))
	return summary

@tracelog
def get_historical_dataframe(symbol, sd, ed):
	historyinstance = historicaldata()
	df = historyinstance.daily_ohlc_history(symbol, sd, ed, type=ResponseType.History)
	if df is not None and len(df) > 0:
		default_logger().debug("\n{}\n".format(df.to_string(index=False)))
		df = df.sort_values(by='Date',ascending=True)
		df['datetime'] = df['Date']
	return df

def test_historical_trading_strategy(symbol, sd, ed, strategy, autosearch, lower, upper, plot=False, backtest_lib=True):
	df = get_historical_dataframe(symbol, sd, ed)
	if df is not None and len(df) > 0:
		if backtest_lib:
			run_test_strategy(df, symbol, strategy, autosearch, lower, upper, plot=plot)
		return test_signals(df, lower, upper, strategy, plot=plot, show_detail=backtest_lib)
	else:
		return None

def prepare_for_historical_strategy(df, symbol):
	df['datetime'] = df['Date']
	df['dt'] = df['Date']
	df['close'] = df['Close']
	df = reset_date_index(df)
	return df

def reset_date_index(df):
	df.set_index('dt', inplace=True)
	return df
