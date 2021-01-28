from nseta.common.log import tracelog, default_logger, suppress_stdout_stderr
from fastquant import backtest
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot

from pylab import rcParams

from matplotlib import pyplot as plt
from nseta.resources.resources import *

# import matplotlib
import click, logging

__VERBOSE__ = default_logger().level == logging.DEBUG
__all__ = ['backtest_custom_strategy', 'backtest_smac_strategy', 'backtest_emac_strategy', 'backtest_rsi_strategy', 'backtest_macd_strategy', 'backtest_bbands_strategy', 'backtest_multi_strategy', 'daily_forecast']

@tracelog
def backtest_smac_strategy(df, fast_period=resources.backtest().smac_fast_period, slow_period=resources.backtest().smac_slow_period, plot=False):
	if __VERBOSE__:
		result = backtest('smac', df.dropna(), fast_period=fast_period, slow_period=slow_period, verbose=__VERBOSE__, plot=plot)
	else:
		with suppress_stdout_stderr():
			result = backtest('smac', df.dropna(), fast_period=fast_period, slow_period=slow_period, verbose=__VERBOSE__, plot=plot)
	print("\n{}".format(result[['fast_period', 'slow_period', 'init_cash', 'final_value', 'pnl']].head()))
	return result

@tracelog
def backtest_emac_strategy(df, fast_period=resources.backtest().emac_fast_period, slow_period=resources.backtest().emac_slow_period, plot=False):
	if __VERBOSE__:
		result = backtest('emac', df.dropna(), fast_period=fast_period, slow_period=slow_period, verbose=__VERBOSE__, plot=plot)
	else:
		with suppress_stdout_stderr():
			result = backtest('emac', df.dropna(), fast_period=fast_period, slow_period=slow_period, verbose=__VERBOSE__, plot=plot)
	print("\n{}".format(result[['fast_period', 'slow_period', 'init_cash', 'final_value', 'pnl']].head()))
	return result

@tracelog
def backtest_rsi_strategy(df, rsi_period=resources.backtest().rsi_period, rsi_lower=resources.backtest().rsi_lower, rsi_upper=resources.backtest().rsi_upper, plot=False):
	if __VERBOSE__:
		result = backtest('rsi', df.dropna(), rsi_period=rsi_period, rsi_upper=rsi_upper, rsi_lower=rsi_lower, verbose=__VERBOSE__, plot=plot)
	else:
		with suppress_stdout_stderr():
			result = backtest('rsi', df.dropna(), rsi_period=rsi_period, rsi_upper=rsi_upper, rsi_lower=rsi_lower, verbose=__VERBOSE__, plot=plot)
	print("\n{}".format(result[['rsi_period', 'rsi_upper', 'rsi_lower', 'init_cash', 'final_value', 'pnl']].head()))
	return result

@tracelog
def backtest_macd_strategy(df, fast_period=resources.backtest().macd_fast_period, slow_period=resources.backtest().macd_slow_period, plot=False):
	if __VERBOSE__:
		result = backtest('macd', df.dropna(), fast_period=fast_period, slow_period=slow_period, signal_period=resources.backtest().macd_signal_period,
		sma_period=resources.backtest().macd_sma_period, dir_period=resources.backtest().macd_dir_period, verbose=__VERBOSE__, plot=plot)
	else:
		with suppress_stdout_stderr():
			result = backtest('macd', df.dropna(), fast_period=fast_period, slow_period=slow_period, signal_period=resources.backtest().macd_signal_period,
				sma_period=resources.backtest().macd_sma_period, dir_period=resources.backtest().macd_dir_period, verbose=__VERBOSE__, plot=plot)
	print("\n{}".format(result[['fast_period', 'slow_period', 'signal_period', 'init_cash', 'final_value', 'pnl']].head()))
	return result

@tracelog
def backtest_bbands_strategy(df, period=resources.backtest().bbands_period, devfactor=resources.backtest().bbands_devfactor, plot=False):
	if __VERBOSE__:
		result = backtest('bbands', df.dropna(), period=period, devfactor=devfactor, verbose=__VERBOSE__, plot=plot)
	else:
		with suppress_stdout_stderr():
			result = backtest('bbands', df.dropna(), period=period, devfactor=devfactor, verbose=__VERBOSE__, plot=plot)
	print("\n{}".format(result[['period', 'devfactor', 'init_cash', 'final_value', 'pnl']].head()))
	return result

@tracelog
def backtest_multi_strategy(df, strats=None, plot=False):
	if strats is None:
		strats = {
			"smac": {"fast_period": resources.backtest().multi_smac_fast_period_range, "slow_period": resources.backtest().multi_smac_slow_period_range},
			"rsi": {"rsi_lower": resources.backtest().multi_rsi_lower_range, "rsi_upper": resources.backtest().multi_rsi_upper_range},
		}
	if __VERBOSE__:
		result = backtest("multi", df.dropna(), strats=strats, verbose=__VERBOSE__, plot=plot)
	else:
		with suppress_stdout_stderr():
			result = backtest("multi", df.dropna(), strats=strats, verbose=__VERBOSE__, plot=plot)
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

def backtest_custom_strategy(df, symbol, strategy, lower_limit=resources.forecast().lower, upper_limit=resources.forecast().upper, plot=False):
	plt, result = daily_forecast(df, symbol, strategy, upper_limit=float(upper_limit), lower_limit=float(lower_limit), periods=resources.forecast().period, plot=plot)
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
@tracelog
def daily_forecast(df, symbol, strategy, upper_limit=resources.forecast().upper, lower_limit=resources.forecast().lower, periods=resources.forecast().period, plot=False):
	train_size = int(resources.forecast().training_percent * len(df)) - periods              # Use 3 years of data as train set. Note there are about 252 trading days in a year
	val_size = int(resources.forecast().test_percent * len(df))                  # Use 1 year of data as validation set
	train_val_size = train_size + val_size # Size of train+validation set

	# Fit model on closing prices
	ts = df.reset_index()[["dt", "close"]]
	# ts = df[['dt', 'close']].rename(columns={'date':'ds', 'close':'y'})
	ts.columns = ['ds', 'y']
	if not ts['y'].count() >= 2:
		click.secho("Dataframe has less than 2 non-NaN rows. Cannot fit the model.", fg='red', nl=True)
		return

	# changepoint_prior_scale_list = [0.05, 0.5, 1, 1.5, 2.5]     # for hyperparameter tuning
	# fourier_order_list = [None, 2, 4, 6, 8, 10]                 # for hyperparameter tuning
	# window_list = [None, 0, 1, 2]                               # for hyperparameter tuning
	# H = 21													  # Forecasting horizon
	# print(hyperparam_tune_cp_fo_wd(ts, H, train_size, val_size, changepoint_prior_scale_list, fourier_order_list, window_list, None))

	m = init_modeler()

	if default_logger().level == logging.DEBUG:
		print('Running in debug mode')
		forecast = fit_model(m, ts, train_val_size, periods)
	else:
		with suppress_stdout_stderr():
			forecast = fit_model(m, ts, train_val_size, periods)

	forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail()

	plt = plot_forecast(m,forecast, symbol, strategy, df, train_val_size, periods)

	if __VERBOSE__:
		result = predict_buy_sell_1day_returns(df, forecast, strategy, upper_limit, lower_limit, plot=plot)
	else:
		with suppress_stdout_stderr():
			result = predict_buy_sell_1day_returns(df, forecast, strategy, upper_limit, lower_limit, plot=plot)
	print("\n{}".format(result[['init_cash', 'final_value', 'pnl']].head()))
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
	m = Prophet(growth=resources.forecast().growth,
			seasonality_mode=resources.forecast().seasonality_mode,
			daily_seasonality=resources.forecast().daily_seasonality,
			weekly_seasonality=resources.forecast().weekly_seasonality,
			yearly_seasonality=resources.forecast().yearly_seasonality,
			interval_width=resources.forecast().interval_width, #uncertainty
			holidays=None,
			n_changepoints=resources.forecast().n_changepoints,
			changepoint_prior_scale=resources.forecast().changepoint_prior_scale
		   )
	m.add_seasonality(name=resources.forecast().seasonality_name, period=resources.forecast().seasonality_period, fourier_order=resources.forecast().fourier_order)
	# Turn off fbprophet stdout logger
	logging.getLogger('fbprophet').setLevel(resources.forecast().fbprophet_log_level) # default_logger().level
	m.add_country_holidays(country_name=resources.forecast().country_name)
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
@tracelog
def fit_model(m, ts, train_val_size, periods):
	m.fit(ts[0:train_val_size])
	ts.head(10)
	future = m.make_future_dataframe(periods=resources.forecast().future_period_factor *periods, freq=resources.forecast().fbprophet_future_dataframe_frequency)
	# Eliminate weekend from future dataframe
	future['day'] = future['ds'].dt.weekday
	future = future[future['day']<=4]
	future.tail()
	# Predict and plot
	forecast = m.predict(future)
	return forecast

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
		plt.title(symbol.upper()+' Forecasted Closing Price, trend and strategic points - Strategy:' + strategy.upper(), fontsize=resources.forecast().plot_font_size)
		plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.90, hspace=0.25,
							wspace=0.5)

		# Plot the predictions
		rcParams['figure.figsize'] = 10, 8 # width 10, height 8
		rcParams.update({'font.size': resources.forecast().plot_font_size})

		ax = df.plot(x='datetime', y='close', style='bx-', grid=True)

		# Plot the predictions
		preds_list = forecast['yhat'][train_val_size:train_val_size+periods]
		ax.plot(df['datetime'][train_val_size:train_val_size+periods], preds_list, marker='x')

		ax.set_xlabel("Date")
		ax.set_ylabel("INR")
		ax.legend(['Close', 'Predictions'])
	return plt

@tracelog
def predict_buy_sell_1day_returns(df, forecast, strategy, upper_limit, lower_limit, plot=False):
	# Convert predictions to expected 1 day returns
	expected_1day_return = forecast.set_index("ds").yhat.pct_change().shift(-1).multiply(100)

	# Backtest the predictions, given that we buy the given symbol when the predicted 
	# next day return is > +1.5%, and sell when it's < -1.5%.
	df[strategy] = expected_1day_return.multiply(-1)
	if strategy == 'custom':
		# forecast['datetime'] = forecast['ds']
		result = backtest(strategy, df, upper_limit=upper_limit, lower_limit=-lower_limit, custom_column=strategy, plot=plot)
	else:
		if strategy in STRATEGY_FORECAST_MAPPING_KEYS:
			result = STRATEGY_FORECAST_MAPPING[strategy](df, plot=plot)
	return result

