from fastquant import backtest
from fbprophet import Prophet
from matplotlib import pyplot as plt

import click


def backtest_smac_strategy(df, fast_period=10, slow_period=50):
	result = backtest('smac', df, fast_period=fast_period, slow_period=slow_period, verbose=False)
	print(result[['fast_period', 'slow_period', 'init_cash', 'final_value', 'pnl']].head())

def backtest_emac_strategy(df, fast_period=10, slow_period=50):
	result = backtest('emac', df, fast_period=fast_period, slow_period=slow_period, verbose=False)
	print(result[['fast_period', 'slow_period', 'init_cash', 'final_value', 'pnl']].head())

def backtest_rsi_strategy(df, rsi_period=14, rsi_lower=30):
	result = backtest('rsi', df, rsi_period=rsi_period, rsi_upper=70, rsi_lower=rsi_lower, verbose=False)
	print(result[['rsi_period', 'rsi_upper', 'rsi_lower', 'init_cash', 'final_value', 'pnl']].head())

def backtest_macd_strategy(df, fast_period=12, slow_period=26):
	result = backtest('macd', df, fast_period=fast_period, slow_period=slow_period, signal_period=9, 
		sma_period=30, dir_period=10, verbose=False)
	print(result[['fast_period', 'slow_period', 'signal_period', 'init_cash', 'final_value', 'pnl']].head())

def backtest_bbands_strategy(df, period=20, devfactor=2.0):
	result = backtest('bbands', df, period=period, devfactor=devfactor, verbose=False)
	print(result[['period', 'devfactor', 'init_cash', 'final_value', 'pnl']].head())

def backtest_multi_strategy(df, key_variable="smac", fast_period=10, slow_period=50, rsi_lower=30, rsi_upper=70):
	strats = { 
		key_variable: {"fast_period": fast_period, "slow_period": slow_period},
		"rsi": {"rsi_lower": rsi_lower, "rsi_upper": rsi_upper} 
	}
	result = backtest("multi", df, strats=strats, verbose=False)
	# print(result[[key_variable +'.fast_period', key_variable+'.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
	return result

'''
This powerful strategy allows to backtest our own trading strategies 
using any type of model after the forecast!
Predictions based on any model can be used as a custom indicator to 
be backtested using fastquant. You just need to add a custom column 
in the input dataframe, and set values for upper_limit and lower_limit.
The strategy is structured similar to RSIStrategy where you can set an 
upper_limit, above which the asset is sold (considered "overbought"), 
and a lower_limit, below which the asset is bought (considered "underbought). 
upper_limit is set to 95 by default, while lower_limit is set to 5 by default.

We are going to use the custom strategy to backtest a custom indicator based 
on in-sample time series forecasts. The forecasts are generated using 
Facebook's Prophet package.
'''
def daily_forecast(df, symbol, upper_limit=1.5, lower_limit=1.5):
	# Fit model on closing prices
	ts = df.reset_index()[["dt", "close"]]
	ts.columns = ['ds', 'y']
	if not ts['y'].count() >= 2:
		click.secho("Dataframe has less than 2 non-NaN rows. Cannot fit the model.", fg='red', nl=True)
		return
	m = Prophet(daily_seasonality=True, yearly_seasonality=True).fit(ts)
	forecast = m.make_future_dataframe(periods=0, freq='D')

	# Predict and plot
	pred = m.predict(forecast)
	fig1 = m.plot(pred)
	plt.subplot()
	plt.title(symbol+' Forecasted Daily Closing Price', fontsize=20)
	plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.90, hspace=0.25,
	                    wspace=0.5)

	# Convert predictions to expected 1 day returns
	expected_1day_return = pred.set_index("ds").yhat.pct_change().shift(-1).multiply(100)

	# Backtest the predictions, given that we buy the given symbol when the predicted 
	# next day return is > +1.5%, and sell when it's < -1.5%.
	df["custom"] = expected_1day_return.multiply(-1)
	
	result = backtest("custom", df.dropna(),upper_limit=upper_limit, lower_limit=-lower_limit)
	print(result[['init_cash', 'final_value', 'pnl']].head())
	return plt
