# -*- coding: utf-8 -*-
from nseta.common.log import tracelog, default_logger, suppress_stdout_stderr
from nseta.resources.resources import *
from nseta.backtests.backtester import *
import click, logging

__VERBOSE__ = default_logger().level == logging.DEBUG
__all__ = ['backtest_custom_strategy', 'backtest_ma_strategy', 'backtest_rsi_strategy', 'backtest_macd_strategy', 'backtest_bbands_strategy', 'backtest_multi_strategy']

@tracelog
def backtest_ma_strategy(df, fast_period=resources.backtest().smac_fast_period, slow_period=resources.backtest().smac_slow_period, plot=False, type_name="smac"):
  bt = resources.backtest()
  ma_dict = {"smac":{"fast_period":bt.smac_fast_period, "slow_period":bt.smac_slow_period},
        "emac":{"fast_period":bt.emac_fast_period, "slow_period":bt.emac_slow_period}}
  return None

@tracelog
def backtest_rsi_strategy(df, rsi_period=resources.backtest().rsi_period, rsi_lower=resources.backtest().rsi_lower, rsi_upper=resources.backtest().rsi_upper, plot=False, type_name="rsi"):
  return None

@tracelog
def backtest_macd_strategy(df, fast_period=resources.backtest().macd_fast_period, slow_period=resources.backtest().macd_slow_period, plot=False, type_name="macd"):
  return None

@tracelog
def backtest_bbands_strategy(df, period=resources.backtest().bbands_period, devfactor=resources.backtest().bbands_devfactor, plot=False, type_name="bbands"):
  return None

@tracelog
def backtest_multi_strategy(df, strats=None, plot=False, type_name="multi"):
  if strats is None:
    strats = {
      "smac": {"fast_period": resources.backtest().multi_smac_fast_period_range, "slow_period": resources.backtest().multi_smac_slow_period_range},
      "rsi": {"rsi_lower": resources.backtest().multi_rsi_lower_range, "rsi_upper": resources.backtest().multi_rsi_upper_range},
    }
  return None

STRATEGY_FORECAST_MAPPING = {
  "rsi": backtest_rsi_strategy,
  "smac": backtest_ma_strategy,
  "macd": backtest_macd_strategy,
  "emac": backtest_ma_strategy,
  "bbands": backtest_bbands_strategy,
  "multi": backtest_multi_strategy,
}

STRATEGY_FORECAST_MAPPING_KEYS = list(STRATEGY_FORECAST_MAPPING.keys())

def backtest_custom_strategy(df, symbol, strategy, lower_limit=resources.forecast().lower, upper_limit=resources.forecast().upper, plot=False):
  return None
