from nseta.common.log import logdebug, default_logger, suppress_stdout_stderr
from fastquant import backtest
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot

from pylab import rcParams

from matplotlib import pyplot as plt

import matplotlib
import click, logging

__all__ = ['backtest_smac_strategy', 'backtest_emac_strategy', 'backtest_rsi_strategy', 'backtest_macd_strategy', 'backtest_bbands_strategy', 'backtest_multi_strategy', 'daily_forecast']

@logdebug
def backtest_smac_strategy(df, fast_period=10, slow_period=50):
	result = backtest('smac', df.dropna(), fast_period=fast_period, slow_period=slow_period, verbose=False)
	print(result[['fast_period', 'slow_period', 'init_cash', 'final_value', 'pnl']].head())
	return result

@logdebug
def backtest_emac_strategy(df, fast_period=10, slow_period=50):
	result = backtest('emac', df.dropna(), fast_period=fast_period, slow_period=slow_period, verbose=False)
	print(result[['fast_period', 'slow_period', 'init_cash', 'final_value', 'pnl']].head())
	return result

@logdebug
def backtest_rsi_strategy(df, rsi_period=14, rsi_lower=30):
	result = backtest('rsi', df.dropna(), rsi_period=rsi_period, rsi_upper=70, rsi_lower=rsi_lower, verbose=False)
	print(result[['rsi_period', 'rsi_upper', 'rsi_lower', 'init_cash', 'final_value', 'pnl']].head())
	return result

@logdebug
def backtest_macd_strategy(df, fast_period=12, slow_period=26):
	result = backtest('macd', df.dropna(), fast_period=fast_period, slow_period=slow_period, signal_period=9, 
		sma_period=30, dir_period=10, verbose=False)
	print(result[['fast_period', 'slow_period', 'signal_period', 'init_cash', 'final_value', 'pnl']].head())
	return result

@logdebug
def backtest_bbands_strategy(df, period=20, devfactor=2.0):
	result = backtest('bbands', df.dropna(), period=period, devfactor=devfactor, verbose=False)
	print(result[['period', 'devfactor', 'init_cash', 'final_value', 'pnl']].head())
	return result

@logdebug
def backtest_multi_strategy(df, key_variable="smac", fast_period=10, slow_period=50, rsi_lower=30, rsi_upper=70):
	strats = { 
		key_variable: {"fast_period": fast_period, "slow_period": slow_period},
		"rsi": {"rsi_lower": rsi_lower, "rsi_upper": rsi_upper} 
	}
	result = backtest("multi", df.dropna(), strats=strats, verbose=False)
	# print(result[[key_variable +'.fast_period', key_variable+'.slow_period', 'rsi.rsi_lower', 'rsi.rsi_upper', 'init_cash', 'final_value', 'pnl']].head())
	return result

STRATEGY_FORECAST_MAPPING = {
	"rsi": backtest_rsi_strategy,
	"smac": backtest_smac_strategy,
	"macd": backtest_macd_strategy,
	"emac": backtest_emac_strategy,
	"bbands": backtest_bbands_strategy,
	"multi": backtest_multi_strategy,
}

STRATEGY_FORECAST_MAPPING_KEYS = list(STRATEGY_FORECAST_MAPPING.keys())

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
@logdebug
def daily_forecast(df, symbol, strategy, upper_limit=1.5, lower_limit=1.5, periods=0):
	train_size = int(0.75 * len(df)) - periods              # Use 3 years of data as train set. Note there are about 252 trading days in a year
	val_size = int(0.25 * len(df))                  # Use 1 year of data as validation set
	changepoint_prior_scale_list = [0.05, 0.5, 1, 1.5, 2.5]     # for hyperparameter tuning
	H = 21											# Forecasting horizon
	train_val_size = train_size + val_size # Size of train+validation set
	fourier_order_list = [None, 2, 4, 6, 8, 10]                 # for hyperparameter tuning
	window_list = [None, 0, 1, 2]                               # for hyperparameter tuning

	# Fit model on closing prices
	ts = df.reset_index()[["dt", "close"]]
	# ts = df[['dt', 'close']].rename(columns={'date':'ds', 'close':'y'})
	ts.columns = ['ds', 'y']
	if not ts['y'].count() >= 2:
		click.secho("Dataframe has less than 2 non-NaN rows. Cannot fit the model.", fg='red', nl=True)
		return

	# print(hyperparam_tune_cp_fo_wd(ts, H, train_size, val_size, changepoint_prior_scale_list, fourier_order_list, window_list, None))

	m = init_modeler()

	forecast = fit_model(m, ts, train_val_size, periods)

	forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

	plt = plot_forecast(m,forecast, symbol, strategy, df, train_val_size, periods)

	result = predict_buy_sell_1day_returns(df, forecast, strategy, upper_limit, lower_limit)

	# get_error_metrics(ts, periods, train_size, val_size, 2.5, 10, None)

	return plt, result

'''
We are going to use Facebook's Prophet to fit the model and forecast stock prices. 
Prophet uses a decomposable time series model with three main model components: 
growth, seasonality and holidays. 
They are combined using the equation y(t) = g(t) + s(t) + h(t) + e(t),
	where 
	g(t) represents the growth function which models non-periodic changes, 
	s(t) represents periodic changes due to weekly or yearly seasonality, 
	h(t) represents the effects of holidays, and 
	e(t) represents the error term. 
Such decomposable time series are very common in forecasting.
'''
def init_modeler():
	# m = Prophet(daily_seasonality=True, yearly_seasonality=True).fit(ts)
	# Time series usually have abrupt changes in their trajectories. Prophet 
	# by default employs automatic changepoint detection. However, the strength 
	# of this changepoint detection can be adjusted by using the parameter 
	# changepoint_prior_scale. Increasing changepoint_prior_scale will make the 
	# trend more flexible and result in overfitting. Decreasing the 
	# changepoint_prior_scale will make the trend less flexible and result in 
	# underfitting. By default, this parameter is set to 0.05.	
	m = Prophet(growth="linear",
			seasonality_mode='additive',
			daily_seasonality=True,
			weekly_seasonality=False,
			yearly_seasonality=False,
			interval_width=0.95, #uncertainty
			holidays=None,
			n_changepoints=20,
			changepoint_prior_scale=2.5
		   )
	m.add_seasonality(name='monthly', period=21, fourier_order=10)
	# Turn off fbprophet stdout logger
	logging.getLogger('fbprophet').setLevel(default_logger().level)
	m.add_country_holidays(country_name='IN')
	return m

'''
We should be performing various forecasts at different dates in this dataset, 
and average the results. For all forecasts, we should be comparing the Prophet 
method with the Last Value method. To evaluate the effectiveness of our methods, 
we should be using the root mean square error (RMSE), mean absolute percentage 
error (MAPE), and mean absolute error (MAE) metrics. For all metrics, the lower 
the value, the better the prediction.
In the Last Value method, we can simply set the prediction as the last observed 
value. In our context, this means we set current closing price as the previous 
day’s closing price. This may be the most cost-effective forecasting model and is 
commonly used as a benchmark against which more sophisticated models can be compared.
'''
@logdebug
def fit_model(m, ts, train_val_size, periods):
	with suppress_stdout_stderr():
		m.fit(ts[0:train_val_size])
		ts.head(10)
		future = m.make_future_dataframe(periods=3*periods, freq='D')
		# Eliminate weekend from future dataframe
		future['day'] = future['ds'].dt.weekday
		future = future[future['day']<=4]
		future.tail()
		# Predict and plot
		forecast = m.predict(future)
	return forecast

@logdebug
def plot_forecast(m, forecast, symbol, strategy, df, train_val_size, periods):
	if periods > 0:
		fig1 = m.plot(forecast, uncertainty=True)
		# fig2 = m.plot_components(forecast)
		add_changepoints_to_plot(fig1.gca(), m, forecast) # Returns a = add_changepoints_to_plot...
		# fig1.axes[0].set_xlim(datestring_to_datetime("2020-02-01"),
		#                       datestring_to_datetime("2020-04-30")
		#                      )
		fig1.axes[0].set_xlabel('Date')
		fig1.axes[0].set_ylabel('Price')
		plt.subplot()
		plt.title(symbol.upper()+' Forecasted Closing Price, trend and strategic points - Strategy:' + strategy.upper(), fontsize=15)
		plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.90, hspace=0.25,
							wspace=0.5)

		# Plot the predictions
		rcParams['figure.figsize'] = 10, 8 # width 10, height 8
		matplotlib.rcParams.update({'font.size': 14})

		ax = df.plot(x='datetime', y='close', style='bx-', grid=True)

		# Plot the predictions
		preds_list = forecast['yhat'][train_val_size:train_val_size+periods]
		ax.plot(df['datetime'][train_val_size:train_val_size+periods], preds_list, marker='x')
			
		ax.set_xlabel("Date")
		ax.set_ylabel("INR")
		ax.legend(['Close', 'Predictions'])
	return plt

@logdebug
def predict_buy_sell_1day_returns(df, forecast, strategy, upper_limit, lower_limit):
	# Convert predictions to expected 1 day returns
	expected_1day_return = forecast.set_index("ds").yhat.pct_change().shift(-1).multiply(100)

	# Backtest the predictions, given that we buy the given symbol when the predicted 
	# next day return is > +1.5%, and sell when it's < -1.5%.
	forecast[strategy] = expected_1day_return.multiply(-1)
	if strategy == 'custom':
		result = backtest(strategy, forecast.dropna(),upper_limit=upper_limit, lower_limit=-lower_limit)
	else:
		if strategy in STRATEGY_FORECAST_MAPPING_KEYS:
			result = STRATEGY_FORECAST_MAPPING[strategy](df)

	print(result[['init_cash', 'final_value', 'pnl']].head())
	return result

