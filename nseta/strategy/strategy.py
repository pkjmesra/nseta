from fastquant import backtest
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot

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

# def backtest_custom_strategy(df, symbol, strategy, upper_limit, lower_limit):
# 	plt, result = daily_forecast(df, symbol, strategy, upper_limit, lower_limit, 0)
# 	return result

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
def daily_forecast(df, symbol, strategy, upper_limit=1.5, lower_limit=1.5, periods=0):
	# Fit model on closing prices
	ts = df.reset_index()[["dt", "close"]]
	ts.columns = ['ds', 'y']
	if not ts['y'].count() >= 2:
		click.secho("Dataframe has less than 2 non-NaN rows. Cannot fit the model.", fg='red', nl=True)
		return
	# m = Prophet(daily_seasonality=True, yearly_seasonality=True).fit(ts)
	m = Prophet(growth="linear",
            seasonality_mode='additive',
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            interval_width=0.95, #uncertainty
            holidays=None,
            n_changepoints=20,
           ) 
	m.add_country_holidays(country_name='IN')
	m.fit(ts)

	future = m.make_future_dataframe(periods=periods, freq='D')
	future.tail()

	# Predict and plot
	forecast = m.predict(future)
	forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

	if periods > 0:
		fig1 = m.plot(forecast, uncertainty=True)
		# fig2 = m.plot_components(forecast)
		a = add_changepoints_to_plot(fig1.gca(), m, forecast)
		# fig1.axes[0].set_xlim(datestring_to_datetime("2020-02-01"),
		#                       datestring_to_datetime("2020-04-30")
		#                      )
		fig1.axes[0].set_xlabel('Date')
		fig1.axes[0].set_ylabel('Price')
		plt.subplot()
		plt.title(symbol.upper()+' Forecasted Closing Price, trend and strategic points - Strategy:' + strategy.upper(), fontsize=15)
		plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.90, hspace=0.25,
		                    wspace=0.5)

	# Convert predictions to expected 1 day returns
	expected_1day_return = forecast.set_index("ds").yhat.pct_change().shift(-1).multiply(100)

	# Backtest the predictions, given that we buy the given symbol when the predicted 
	# next day return is > +1.5%, and sell when it's < -1.5%.
	df[strategy] = expected_1day_return.multiply(-1)
	if strategy == 'custom':
		result = backtest(strategy, df.dropna(),upper_limit=upper_limit, lower_limit=-lower_limit)
	else:
		result = backtest(strategy, df.dropna())
	print(result[['init_cash', 'final_value', 'pnl']].head())
	return plt, result
