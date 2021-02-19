import inspect
import pandas as pd
import numpy as np
import sys
from datetime import datetime
import threading

from nseta.strategy.strategy import *
from nseta.strategy.rsiSignalStrategy import *
from nseta.strategy.bbandsSignalStrategy import *
from nseta.strategy.macdSignalStrategy import *
from nseta.resources.resources import *
from nseta.archives.archiver import *
from nseta.common.log import tracelog, default_logger
from nseta.scanner.stockscanner import scanner
from nseta.scanner.intradayStockScanner import intradayStockScanner
from nseta.common.multithreadedScanner import multithreaded_scan
from nseta.strategy.simulatedorder import OrderType
from nseta.common.ti import ti
from nseta.common.history import *
from nseta.plots.plots import plot_rsi

__all__ = ['STRATEGY_MAPPING', 'strategyManager']

CONCURRENT_STOCK_COUNT = 3
CONCURRENT_STRATEGY_COUNT = 3

@tracelog
def smac_strategy(df,  lower, upper, plot=False):
	backtest_smac_strategy(df, fast_period=resources.backtest().smac_fast_period, slow_period=resources.backtest().smac_slow_period, plot=plot)

@tracelog
def emac_strategy(df,  lower, upper, plot=False):
	backtest_emac_strategy(df, fast_period=resources.backtest().emac_fast_period, slow_period=resources.backtest().emac_slow_period, plot=plot)

@tracelog
def bbands_strategy(df,  lower, upper, plot=False):
	backtest_bbands_strategy(df, period=resources.backtest().bbands_period, devfactor=resources.backtest().bbands_devfactor)

@tracelog
def rsi_strategy(df,  lower=resources.backtest().rsi_lower, upper=resources.backtest().rsi_upper, plot=False):
	lower = resources.backtest().rsi_lower if lower is None else lower
	upper = resources.backtest().rsi_upper if upper is None else upper
	backtest_rsi_strategy(df, rsi_period=resources.backtest().rsi_period, rsi_lower=lower, rsi_upper=upper, plot=plot)

@tracelog
def macd_strategy(df,  lower, upper, plot=False):
	backtest_macd_strategy(df, fast_period=resources.backtest().macd_fast_period, slow_period=resources.backtest().macd_slow_period, plot=plot)

@tracelog
def multi_strategy(df,  lower, upper, plot=False):
	SAMPLE_STRAT_DICT = {
		"smac": {"fast_period": resources.backtest().multi_smac_fast_period_range, "slow_period": resources.backtest().multi_smac_slow_period_range},
		"rsi": {"rsi_lower": resources.backtest().multi_rsi_lower_range, "rsi_upper": resources.backtest().multi_rsi_upper_range},
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

__test_counter__ = 0
__download_counter__ = 0

class strategyManager:

	def __init__(self, order_type=OrderType.Delivery):
		self._strict = resources.backtest().strict_strategy
		self._total_stocks_counter = 0
		self._total_tests_counter = 0

	@property
	def total_stocks_counter(self):
		return self._total_stocks_counter

	@property
	def total_tests_counter(self):
		return self._total_tests_counter

	@property
	def strict(self):
		return self._strict

	@strict.setter
	def strict(self, value):
		self._strict = value

	@tracelog
	def multithreadedScanner_callback(self, **kwargs):
		start = kwargs['start']
		end = kwargs['end']
		upper = kwargs['upper']
		lower = kwargs['lower']
		intraday = kwargs['intraday']
		stocks = kwargs['stocks']
		strategies = kwargs['items']

		if start is not None:
			sd = datetime.strptime(start, "%Y-%m-%d").date()
		if end is not None:
			ed = datetime.strptime(end, "%Y-%m-%d").date()
		frames = []
		instance = intradayStockScanner('all') if intraday else historicaldata()
		for stock in stocks:
			df_summary_dict = {'Symbol':['?'], 'RSI-PnL':[np.nan],'MACD-PnL':[np.nan], 'BBANDS-PnL':[np.nan], 'Reco-RSI':[np.nan], 'Reco-MACD':[np.nan], 'Reco-BBANDS':[np.nan]}
			df_summary = pd.DataFrame(df_summary_dict)
			for strategy in strategies:
				try:
					df = instance.ohlc_intraday_history(stock) if intraday else instance.daily_ohlc_history(stock, sd, ed, type=ResponseType.History)
					summary = self.test_signals(df, lower, upper, strategy, intraday= intraday, plot=False, show_detail=False)
					if summary is not None and len(summary) > 0:
						df_summary['Symbol'].iloc[0] = stock
						df_summary['{}-PnL'.format(strategy.upper())].iloc[0] = summary['PnL'].iloc[0]
						reco = summary['Recommendation'].iloc[0]
						df_summary['Reco-{}'.format(strategy.upper())].iloc[0] = '-' if reco == 'Unknown' else reco
				except Exception as e:
					default_logger().debug(e, exc_info=True)
					default_logger().debug('Failed to test trading strategy for symbol: {}.'.format(stock))
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

		global __download_counter__
		__download_counter__ = 0
		global __test_counter__
		__test_counter__ = 0
		frame = inspect.currentframe()
		args, _, _, kwargs = inspect.getargvalues(frame)
		del(kwargs['frame'])
		del(kwargs['self'])
		del(kwargs['symbol'])
		del(kwargs['symbols'])
		del(kwargs['scn'])
		kwargs1=dict(kwargs)
		kwargs1['stocks'] = stocks
		kwargs1['terminate_after_iter'] = 1
		wait_time = 10
		kwargs1['wait_time'] = wait_time
		b = threading.Thread(name='download_background', target=self.download_background, args=[kwargs1], daemon=True)
		b.start()
		kwargs['callbackMethod'] = self.scan_trading_strategy_segmented
		kwargs['items'] = stocks
		kwargs['max_per_thread'] = CONCURRENT_STOCK_COUNT
		list_returned = multithreaded_scan(**kwargs)
		summary = list_returned.pop(0)
		summary = summary.groupby('Symbol').first()
		summary.reset_index(inplace=True)
		sys.stdout.write("\rDone.".ljust(120))
		sys.stdout.flush()
		return summary

	@tracelog
	def scan_trading_strategy_segmented(self, **args):
		frame = inspect.currentframe()
		gargs, _, _, kwargs_main = inspect.getargvalues(frame)
		del(kwargs_main['frame'])
		del(kwargs_main['self'])
		kwargs = kwargs_main['args']
		strategy = kwargs['strategy']
		if strategy is not None and len(strategy) > 0:
			strategies = [x.strip() for x in strategy.split(',')]
		else:
			strategies = ['rsi', 'macd', 'bbands']
		del(kwargs['strategy'])
		kwargs['stocks'] = kwargs['items']
		kwargs['callbackMethod'] = self.multithreadedScanner_callback
		kwargs['items'] = strategies
		kwargs['max_per_thread'] = CONCURRENT_STRATEGY_COUNT
		self._total_tests_counter = len(strategies) * self.total_stocks_counter
		list_returned = multithreaded_scan(**kwargs)
		summary = list_returned.pop(0)
		return [summary, None]

	@tracelog
	def download_stock_data(self, **kwargs):
		start = kwargs['start']
		end = kwargs['end']
		intraday = kwargs['intraday']
		stocks = kwargs['items']
		if start is not None:
			sd = datetime.strptime(start, "%Y-%m-%d").date()
		if end is not None:
			ed = datetime.strptime(end, "%Y-%m-%d").date()
		instance = intradayStockScanner('all') if intraday else historicaldata()
		for stock in stocks:
			try:
				global __download_counter__
				with threading.Lock():
					__download_counter__ += 1
				sys.stdout.write("\r{}/{}. Fetching for {}".ljust(120).format(__download_counter__, self.total_stocks_counter, stock))
				sys.stdout.flush()
				instance.ohlc_intraday_history(stock) if intraday else instance.daily_ohlc_history(stock, sd, ed, type=ResponseType.History)
			except Exception as e:
				default_logger().debug(e, exc_info=True)
				default_logger().debug('Failed to download data for symbol: {}.'.format(stock))
				continue
		return [None, None]

	def test_historical_trading_strategy(self, symbol, sd, ed, strategy, lower, upper, plot=False, backtest_lib=True):
		df = self.get_historical_dataframe(symbol, sd, ed)
		global __test_counter__
		__test_counter__ = 0
		self._total_tests_counter = 1
		if df is not None and len(df) > 0:
			if backtest_lib:
				self.run_test_strategy(df, symbol, strategy,  lower, upper, plot=plot)
			return self.test_signals(df, lower, upper, strategy, plot=plot, show_detail=backtest_lib)
		else:
			return None

	def test_intraday_trading_strategy(self, symbol, strategy,lower, upper, plot=False, backtest_lib=True):
		df = self.get_intraday_dataframe(symbol, strategy)
		global __test_counter__
		__test_counter__ = 0
		self._total_tests_counter = 1
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
		s = intradayStockScanner(strategy)
		s.periodicity = "1"
		df = s.ohlc_intraday_history(symbol)
		if df is not None and len(df) > 0:
			df.drop(['Open'], axis = 1, inplace = True)
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

	def test_signals(self, df, lower=resources.rsi().lower, upper=resources.rsi().upper, strategy='rsi', intraday = False, plot=False, show_detail=True):
		tiinstance = ti()
		df = tiinstance.update_ti(df, rsi=True, bbands=True, macd=True)
		df = df.sort_values(by='Date',ascending=True)
		symbol = df['Symbol'].iloc[0]
		results = None
		summary = None
		global __test_counter__
		with threading.Lock():
			__test_counter__ += 1
		sys.stdout.write("\r{}/{}. Testing {} trading strategy for {}.".ljust(120).format(__test_counter__, self.total_tests_counter, strategy, symbol))
		sys.stdout.flush()

		if strategy.lower() == 'rsi':
			df_rsi_dict = {'Symbol':df['Symbol'], 'Date':df['Date'], 'RSI':df['RSI'], 'Close':df['Close']}
			df_rsi = pd.DataFrame(df_rsi_dict)
			rsisignal = rsiSignalStrategy(strict=self.strict, intraday=intraday, requires_ledger=show_detail)
			rsisignal.set_limits(lower, upper)
			results, summary = rsisignal.test_strategy(df_rsi)
			if plot:
				(plot_rsi(df)).show()
		elif strategy.lower() == 'bbands':
			df_bbands_dict = {'Symbol':df['Symbol'], 'Date':df['Date'], 'BBands-U':df['BBands-U'], 'BBands-M':df['BBands-M'], 'BBands-L':df['BBands-L'], 'Close':df['Close']}
			df_bbands = pd.DataFrame(df_bbands_dict)
			bbandsSignal = bbandsSignalStrategy(strict=self.strict, intraday=intraday, requires_ledger=show_detail)
			results, summary = bbandsSignal.test_strategy(df_bbands)
		elif strategy.lower() == 'macd':
			df_macd_dict = {'Symbol':df['Symbol'], 'Date':df['Date'], 'macd(12)':df['macd(12)'], 'macdsignal(9)':df['macdsignal(9)'], 'macdhist(26)':df['macdhist(26)'], 'Close':df['Close']}
			df_macd = pd.DataFrame(df_macd_dict)
			macdSignal = macdSignalStrategy(strict=self.strict, intraday=intraday, requires_ledger=show_detail)
			results, summary = macdSignal.test_strategy(df_macd)
		sys.stdout.write("\r{}/{}. Finished testing {} trading strategy for {}.".ljust(120).format(__test_counter__, self.total_tests_counter, strategy, symbol))
		sys.stdout.flush()
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

	@tracelog
	def download_background(self, args):
		iteration = 0
		default_logger().debug(args)
		frame = inspect.currentframe()
		args, _, _, main_args = inspect.getargvalues(frame)
		default_logger().debug(main_args)
		kwargs = main_args['args']
		default_logger().debug(kwargs)
		terminate_after_iter = kwargs['terminate_after_iter']
		stocks = kwargs['stocks']
		self._total_stocks_counter = len(stocks)
		del(kwargs['stocks'])
		del(kwargs['terminate_after_iter'])
		del(kwargs['wait_time'])
		while True:
			iteration = iteration + 1
			kwargs['callbackMethod'] = self.download_stock_data
			kwargs['items'] = stocks
			kwargs['max_per_thread'] = CONCURRENT_STOCK_COUNT
			multithreaded_scan(**kwargs)
			if terminate_after_iter > 0 and iteration >= terminate_after_iter:
				sys.stdout.write("\rDownload Finished.".ljust(120))
				sys.stdout.flush()
				break
		default_logger().debug('Finished downloading for all stocks.')
		return iteration
