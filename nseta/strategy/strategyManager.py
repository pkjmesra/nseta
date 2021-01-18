import inspect
import pandas as pd
import numpy as np
from datetime import datetime

from nseta.strategy.strategy import *
from nseta.strategy.rsiSignalStrategy import *
from nseta.strategy.bbandsSignalStrategy import *
from nseta.strategy.macdSignalStrategy import *
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger
from nseta.scanner.tiscanner import scanner
from nseta.common.multithreadedScanner import multithreaded_scan
from nseta.common.ti import ti
from nseta.common.history import *
from nseta.plots.plots import plot_rsi

__all__ = ['STRATEGY_MAPPING', 'strategyManager']

@tracelog
def smac_strategy(df,  lower, upper, plot=False):
	backtest_smac_strategy(df, fast_period=10, slow_period=50, plot=plot)

@tracelog
def emac_strategy(df,  lower, upper, plot=False):
	backtest_emac_strategy(df, fast_period=9, slow_period=50, plot=plot)

@tracelog
def bbands_strategy(df,  lower, upper, plot=False):
	backtest_bbands_strategy(df, period=20, devfactor=2.0)

@tracelog
def rsi_strategy(df,  lower=30, upper=70, plot=False):
	if lower is None:
		lower = 30
	if upper is None:
		upper = 70
	backtest_rsi_strategy(df, rsi_period=14, rsi_lower=lower, rsi_upper=upper, plot=plot)

@tracelog
def macd_strategy(df,  lower, upper, plot=False):
	backtest_macd_strategy(df, fast_period=12, slow_period=26, plot=plot)

@tracelog
def multi_strategy(df,  lower, upper, plot=False):
	SAMPLE_STRAT_DICT = {
		"smac": {"fast_period": 10, "slow_period": 50},
		"rsi": {"rsi_lower": 30, "rsi_upper": 70},
	}
	results = backtest_multi_strategy(df, SAMPLE_STRAT_DICT, plot=plot)
	print(results[['smac.fast_period', 'smac.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())

STRATEGY_MAPPING = {
	"rsi": rsi_strategy,
	"smac": smac_strategy,
	"macd": macd_strategy,
	"emac": emac_strategy,
	"bbands": bbands_strategy,
	"multi": multi_strategy
}

class strategyManager:

	def multithreadedScanner_callback(self, **kwargs):
		start = kwargs['start']
		end = kwargs['end']
		strategy = kwargs['strategy']
		upper = kwargs['upper']
		lower = kwargs['lower']
		intraday = kwargs['intraday']
		stocks = kwargs['stocks']

		if start is not None:
			sd = datetime.strptime(start, "%Y-%m-%d").date()
		if end is not None:
			ed = datetime.strptime(end, "%Y-%m-%d").date()
		strategies = ['rsi', 'macd', 'bbands']
		if strategy is not None and strategy in strategies:
			strategies = [strategy]
		frames = []
		for stock in stocks:
			df_summary_dict = {'Symbol':['?'], 'MACD-PnL':[np.nan], 'RSI-PnL':[np.nan], 'BBANDS-PnL':[np.nan], 'Recommendation':['?']}
			df_summary = pd.DataFrame(df_summary_dict)
			for s in strategies:
				try:
					if intraday:
						summary = self.test_intraday_trading_strategy(stock, s, lower, upper, backtest_lib=False)
					else:
						summary = self.test_historical_trading_strategy(stock, sd, ed, s, lower, upper, backtest_lib=False)
					if summary is not None and len(summary) > 0:
						df_summary['Symbol'].iloc[0] = stock
						df_summary['{}-PnL'.format(s.upper())].iloc[0] = summary['PnL'].iloc[0]
						df_summary['Recommendation'].iloc[0] = summary['Recommendation'].iloc[0]
				except Exception as e:
					default_logger().debug(e, exc_info=True)
					click.secho('Failed to test trading strategy for symbol: {}.'.format(stock), fg='red', nl=True)
					continue
			if df_summary is not None and len(df_summary) > 0:
				frames.append(df_summary)
		full_summary = pd.concat(frames)
		return [full_summary, None]

	def scan_trading_strategy(self,symbol, start, end, strategy, upper, lower, clear, orderby, intraday=False):
		scn = scanner()
		if symbol is not None and len(symbol) > 0:
			symbols = [x.strip() for x in symbol.split(',')]
		else:
			symbols = []
		stocks = scn.stocks_list(symbols)

		frame = inspect.currentframe()
		args, _, _, kwargs = inspect.getargvalues(frame)
		del(kwargs['frame'])
		del(kwargs['self'])
		del(kwargs['symbol'])
		kwargs['callbackInstance'] = self
		kwargs['stocks'] = stocks
		list_returned = multithreaded_scan(**kwargs)
		full_summary = list_returned.pop(0)
		return full_summary

	def test_historical_trading_strategy(self, symbol, sd, ed, strategy, lower, upper, plot=False, backtest_lib=True):
		df = self.get_historical_dataframe(symbol, sd, ed)
		if df is not None and len(df) > 0:
			if backtest_lib:
				self.run_test_strategy(df, symbol, strategy,  lower, upper, plot=plot)
			return self.test_signals(df, lower, upper, strategy, plot=plot, show_detail=backtest_lib)
		else:
			return None

	def test_intraday_trading_strategy(self, symbol, strategy,lower, upper, plot=False, backtest_lib=True):
		df = self.get_intraday_dataframe(symbol, strategy)
		if df is not None and len(df) > 0:
			if backtest_lib:
				self.run_test_strategy(df, symbol, strategy, lower, upper, plot=plot)
			return self.test_signals(df, lower, upper, strategy, intraday=True, plot=plot, show_detail=backtest_lib)
		else:
			return None

	@tracelog
	def get_historical_dataframe(self, symbol, sd, ed):
		historyinstance = historicaldata()
		df = historyinstance.daily_ohlc_history(symbol, sd, ed, type=ResponseType.History)
		if df is not None and len(df) > 0:
			default_logger().debug("\n{}\n".format(df.to_string(index=False)))
			df = df.sort_values(by='Date',ascending=True)
			df['datetime'] = df['Date']
		return df

	@tracelog
	def get_intraday_dataframe(self, symbol, strategy):
		s = scanner(strategy)
		df = s.ohlc_intraday_history(symbol)
		if df is not None and len(df) > 0:
			df = df.sort_values(by='Date',ascending=True)
		return df

	def run_test_strategy(self, df, symbol, strategy,  lower, upper, plot=False):
		strategy = strategy.lower()
		if strategy in STRATEGY_MAPPING:
			STRATEGY_MAPPING[strategy](df,  float(lower), float(upper))
		elif strategy == 'custom':
			df = self.prepare_for_historical_strategy(df, symbol)
			backtest_custom_strategy(df, symbol, strategy, upper_limit=float(upper), lower_limit=float(lower))
		else:
			STRATEGY_MAPPING['rsi'](df,  float(upper), float(lower))

	def test_signals(self, df, lower, upper, strategy, intraday = False, plot=False, show_detail=True):
		tiinstance = ti()
		df = tiinstance.update_ti(df)
		df = df.sort_values(by='Date',ascending=True)
		results = None
		summary = None
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

	def prepare_for_historical_strategy(self, df, symbol):
		df['datetime'] = df['Date']
		df['dt'] = df['Date']
		df['close'] = df['Close']
		df = self.reset_date_index(df)
		return df

	def reset_date_index(self, df):
		df.set_index('dt', inplace=True)
		return df