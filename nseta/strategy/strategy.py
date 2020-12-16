from nseta.common.log import logdebug, default_logger, suppress_stdout_stderr
from fastquant import backtest
from fbprophet import Prophet
from fbprophet.plot import add_changepoints_to_plot

from datetime import date, datetime, timedelta
from joblib import Parallel, delayed
from matplotlib import pyplot as plt
from pylab import rcParams
from sklearn.metrics import mean_squared_error

import math
import matplotlib
import multiprocessing
import numpy as np
import pandas as pd
import pickle
import seaborn as sns
import time
import click, logging

__all__ = ['backtest_smac_strategy', 'backtest_emac_strategy', 'backtest_rsi_strategy', 'backtest_macd_strategy', 'backtest_bbands_strategy', 'backtest_multi_strategy', 'daily_forecast', 'tune_fourier_order', 'tune_hyperparameters']

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
def tune_fourier_order(df):
	train_size = int(0.75 * len(df))             					# Use 3 years of data as train set. Note there are about 252 trading days in a year
	val_size = int(0.25 * len(df))                  				# Use 1 year of data as validation set
	H = 21															# Forecasting horizon
	fourier_order_list = [None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]      # for hyperparameter tuning
	train_val_size = train_size + val_size 							# Size of train+validation set

	tic = time.time()
	df_prophet = get_prophet_data_frame(df)
	with suppress_stdout_stderr():
		fourier_order_opt, results = hyperparam_tune_fo(df_prophet[0:train_val_size], 
														H, 
														train_size, 
														val_size, 
														fourier_order_list)
	toc = time.time()
	print("Time taken for Fourier Order Hyperparameter tuning= " + str((toc-tic)/60.0) + " mins")

	print("fourier_order_opt = " + str(fourier_order_opt))
	return results

def tune_hyperparameters(df, holidays=None):
	changepoint_prior_scale_list = [0.05, 0.5, 1, 1.5, 2.5]    	# for hyperparameter tuning
	fourier_order_list = [None, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # for hyperparameter tuning
	window_list = [None, 0, 1, 2]                               # for hyperparameter tuning
	
	train_size = int(0.75 * len(df))              				# Use 3 years of data as train set. Note there are about 252 trading days in a year
	val_size = int(0.25 * len(df))                  			# Use 1 year of data as validation set
	H = 21														# Forecasting horizon
	train_val_size = train_size + val_size 						# Size of train+validation set
	ts = get_prophet_data_frame(df)
	
	toc = time.time()
	changepoint_prior_scale_opt, fourier_order_opt, window_opt, results = hyperparam_tune_cp_fo_wd(ts, H, train_size, val_size, changepoint_prior_scale_list, fourier_order_list, window_list, holidays)
	toc = time.time()
	print("Time taken for Hyperparameter tuning= " + str((toc-tic)/60.0) + " mins")
	return changepoint_prior_scale_opt, fourier_order_opt, window_opt, results

@logdebug
def get_prophet_data_frame(df):
	# Fit model on closing prices
	ts = df.reset_index()[["dt", "close"]]
	# ts = df[['dt', 'close']].rename(columns={'date':'ds', 'close':'y'})
	ts.columns = ['ds', 'y']
	return ts

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
	train_size = int(0.75 * len(df)) - periods              	# Use 3 years of data as train set. Note there are about 252 trading days in a year
	val_size = int(0.25 * len(df))                  			# Use 1 year of data as validation set
	H = 21														# Forecasting horizon
	train_val_size = train_size + val_size 						# Size of train+validation set

	ts = get_prophet_data_frame(df)
	if not ts['y'].count() >= 2:
		click.secho("Dataframe has less than 2 non-NaN rows. Cannot fit the model.", fg='red', nl=True)
		return

	m = init_modeler(changepoint_prior_scale=0.05, fourier_order=None, holidays=None)

	forecast = fit_model(m, ts, train_val_size, periods)
	# forecast = get_preds_prophet(df, H, changepoint_prior_scale=0.05, fourier_order=None, holidays=None)

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
def init_modeler(changepoint_prior_scale=0.05, fourier_order=None, holidays=None):
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
			changepoint_prior_scale=.05
		   )
	if holidays is not None:
		m = Prophet(changepoint_prior_scale=changepoint_prior_scale, holidays=holidays)
	else:
		m = Prophet(changepoint_prior_scale=changepoint_prior_scale)
		m.add_country_holidays(country_name='IN')
	if (fourier_order is not None) and (~np.isnan(fourier_order)): # add monthly seasonality
		m.add_seasonality(name='monthly', period=21, fourier_order=int(fourier_order))
	# Turn off fbprophet stdout logger
	logging.getLogger('fbprophet').setLevel(default_logger().level)
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
def fit_model(m, ts, train_val_size, periods, exclude_weekends=False):
	with suppress_stdout_stderr():
		m.fit(ts[0:train_val_size])
		ts.head(10)
		future = m.make_future_dataframe(periods=3*periods, freq='D')
		
		# Eliminate weekend from future dataframe
		if exclude_weekends:
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

def get_mape(y_true, y_pred): 
	"""
	Compute mean absolute percentage error (MAPE)
	"""
	y_true, y_pred = np.array(y_true), np.array(y_pred)
	return np.mean(np.abs((y_true - y_pred) / y_true)) * 100

def get_mae(a, b):
	"""
	Comp mean absolute error e_t = E[|a_t - b_t|]. a and b can be lists.
	Returns a vector of len = len(a) = len(b)
	"""
	return np.mean(abs(np.array(a)-np.array(b)))

def get_rmse(a, b):
	"""
	Comp RMSE. a and b can be lists.
	Returns a scalar.
	"""
	return math.sqrt(np.mean((np.array(a)-np.array(b))**2))

@logdebug
def get_preds_prophet(df, H, train_size, changepoint_prior_scale=0.05, fourier_order=None, holidays=None):
	"""
	Use Prophet to forecast for the next H timesteps, starting at df[len(df)]
	Inputs
		df: dataframe with headers 'ds' and 'y' (necessary for Prophet)
		H : forecast horizon
		changepoint_prior_scale : to detect changepoints in time series analysis trajectories
		fourier_order           : determines how quickly seasonality can change
		holidays                : dataframe containing holidays you will like to model. 
								  Must have 'holiday' and 'ds' columns
	Outputs
		A list of predictions
	"""
	# Fit prophet model
	with suppress_stdout_stderr():
		if holidays is not None:
			m = Prophet(changepoint_prior_scale=changepoint_prior_scale, holidays=holidays)
		else:
			m = Prophet(changepoint_prior_scale=2.5) # TODO: Fix this change_scale hardcoding
		if (fourier_order is not None) and (~np.isnan(fourier_order)): # add monthly seasonality
			m.add_seasonality(name='monthly', period=21, fourier_order=int(fourier_order))

		m.fit(df)
		
		# Make future dataframe
		future = m.make_future_dataframe(periods=2*H, freq='D')
		
		# Eliminate weekend from future dataframe
		future['day'] = future['ds'].dt.weekday
		future = future[future['day']<=4]
		
		# Predict
		forecast = m.predict(future) # Note this prediction includes the original dates
	forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]

	return forecast['yhat'][len(df):len(df)+H]

def processInput(i, df, H, train_size, changepoint_prior_scale=0.05, fourier_order=10, holidays=None):
	preds_list = get_preds_prophet(df[i-train_size:i], H, changepoint_prior_scale, fourier_order, holidays)
	# Compute error metrics
	rmse = get_rmse(df[i:i+H]['y'], preds_list)
	mape = get_mape(df[i:i+H]['y'], preds_list)
	mae = get_mae(df[i:i+H]['y'], preds_list)
	
	return (rmse, mape, mae)

def get_preds_prophet_parallelized(df, H, train_size, changepoint_prior_scale=0.05, fourier_order=None, holidays=None):
	"""
	This is a parallelized implementation of get_preds_prophet.
	Given a dataframe consisting of both train+validation, do predictions of forecast horizon H on the validation set, 
	at H/2 intervals.
	Inputs
		df                     : dataframe with headers 'ds' and 'y' (necessary for Prophet)
		H                      : forecast horizon
		train_size             : length of training set
		val_size               : length of validation set. Note len(df) = train_size + val_size
		changepoint_prior_scale: to detect changepoints in time series analysis trajectories
		fourier_order          : determines how quickly seasonality can change
		holidays               : dataframe containing holidays you will like to model. 
								 Must have 'holiday' and 'ds' columns
	Outputs
		mean of rmse, mean of mape, mean of mae, dict of predictions
	"""
	inputs = range(train_size, len(df)-H, int(H/2))

	num_cores = multiprocessing.cpu_count()

	results = Parallel(n_jobs=num_cores)(delayed(processInput)(i, df, H, train_size, changepoint_prior_scale, fourier_order, holidays) for i in inputs)
	# results has format [(rmse1, mape1, mae1), (rmse2, mape2, mae2), ...]

	rmse = [errors[0] for errors in results]
	mape = [errors[1] for errors in results]
	mae = [errors[2] for errors in results]
	
	return np.mean(rmse), np.mean(mape), np.mean(mae)

def get_error_metrics(df, H, train_size, val_size, changepoint_prior_scale=0.05, fourier_order=None, holidays=None):
	"""
	Given a dataframe consisting of both train+validation, do predictions of forecast horizon H on the validation set, 
	at H/2 intervals.
	Inputs
		df                     : dataframe with headers 'ds' and 'y' (necessary for Prophet)
		H                      : forecast horizon
		train_size             : length of training set
		val_size               : length of validation set. Note len(df) = train_size + val_size
		changepoint_prior_scale: to detect changepoints in time series analysis trajectories
		fourier_order          : determines how quickly seasonality can change
		holidays               : dataframe containing holidays you will like to model. 
								 Must have 'holiday' and 'ds' columns
	Outputs
		mean of rmse, mean of mape, mean of mae, dict of predictions
	"""
	# assert len(df) == train_size + val_size
	
	# Predict using Prophet, and compute error metrics also
	rmse = [] # root mean square error
	mape = [] # mean absolute percentage error
	mae = []  # mean absolute error
	preds_dict = {}
	
	rmse_mean, mape_mean, mae_mean = get_preds_prophet_parallelized(df, H, train_size, changepoint_prior_scale, fourier_order, holidays)
	# print("RMSE: " + rmse_mean + "MAPE: " + mape_mean+ "MAE: " + mae_mean)
	return rmse_mean, mape_mean, mae_mean

def hyperparam_tune_cp(df, H, train_size, val_size, changepoint_prior_scale_list):
	"""
	Hyperparameter tuning - changepoint
	Inputs
		df                     : dataframe with headers 'ds' and 'y' (necessary for Prophet)
		H                      : forecast horizon
		train_size             : length of training set
		val_size               : length of validation set. Note len(df) = train_size + val_size
		changepoint_prior_scale_list: list of changepoint_prior_scale values to try
	Outputs
		optimum hyperparameters
	"""
	rmse_mean_list = []
	mape_mean_list = []
	mae_mean_list = []
	for changepoint_prior_scale in changepoint_prior_scale_list:
		print("changepoint_prior_scale = " + str(changepoint_prior_scale))
		rmse_mean, mape_mean, mae_mean = get_error_metrics(df, H, train_size, val_size, changepoint_prior_scale)
		rmse_mean_list.append(rmse_mean)
		mape_mean_list.append(mape_mean)
		mae_mean_list.append(mae_mean)
	
	# Create results dataframe
	results = pd.DataFrame({'changepoint_prior_scale': changepoint_prior_scale_list,
							'rmse': rmse_mean_list,
							'mape(%)': mape_mean_list,
							'mae': mae_mean_list})
	
	# Return hyperparam corresponding to lowest error metric
	return changepoint_prior_scale_list[np.argmin(rmse_mean_list)], results

def hyperparam_tune_fo(df, H, train_size, val_size, fourier_order_list):
	"""
	Hyperparameter tuning - fourier order
	Inputs
		df                     : dataframe with headers 'ds' and 'y' (necessary for Prophet)
		H                      : forecast horizon
		train_size             : length of training set
		val_size               : length of validation set. Note len(df) = train_size + val_size
		fourier_order_list     : list of fourier_order values to try
	Outputs
		optimum hyperparameters
	"""
	rmse_mean_list = []
	mape_mean_list = []
	mae_mean_list = []
	for fourier_order in fourier_order_list:
		print("fourier_order = " + str(fourier_order))
		rmse_mean, mape_mean, mae_mean = get_error_metrics(df, H, train_size, val_size, 0.05, fourier_order)
		rmse_mean_list.append(rmse_mean)
		mape_mean_list.append(mape_mean)
		mae_mean_list.append(mae_mean)
		
	# Create results dataframe
	results = pd.DataFrame({'fourier_order': fourier_order_list,
							'rmse': rmse_mean_list,
							'mape(%)': mape_mean_list,
							'mae': mae_mean_list})
		
	# Return hyperparam corresponding to lowest error metric
	return fourier_order_list[np.argmin(rmse_mean_list)], results

def hyperparam_tune_wd(df, H, train_size, val_size, window_list, holidays):
	"""
	Hyperparameter tuning - upper and lower windows for holidays
	Inputs
		df                     : dataframe with headers 'ds' and 'y' (necessary for Prophet)
		H                      : forecast horizon
		train_size             : length of training set
		val_size               : length of validation set. Note len(df) = train_size + val_size
		window_list            : list of upper and lower window values to try
		holidays               : dataframe containing holidays you will like to model. 
								 Must have 'holiday' and 'ds' columns
	Outputs
		optimum hyperparameters
	"""
	rmse_mean_list = []
	mape_mean_list = []
	mae_mean_list = []
	for window in window_list:
		print("window = " + str(window))
		
		if window is None:
			rmse_mean, mape_mean, mae_mean = get_error_metrics(df=df, 
																  H=H, 
																  train_size=train_size, 
																  val_size=val_size, 
																  holidays=None)
		else:
			# Add lower_window and upper_window which extend the holiday out to 
			# [lower_window, upper_window] days around the date
			holidays['lower_window'] = -window
			holidays['upper_window'] = +window
		
			rmse_mean, mape_mean, mae_mean = get_error_metrics(df=df, 
																  H=H, 
																  train_size=train_size, 
																  val_size=val_size, 
																  holidays=holidays)
		rmse_mean_list.append(rmse_mean)
		mape_mean_list.append(mape_mean)
		mae_mean_list.append(mae_mean)
		
	# Create results dataframe
	results = pd.DataFrame({'window': window_list,
							'rmse': rmse_mean_list,
							'mape(%)': mape_mean_list,
							'mae': mae_mean_list})
		
	# Return hyperparam corresponding to lowest error metric
	return window_list[np.argmin(rmse_mean_list)], results

def hyperparam_tune_cp_fo_wd(df, H, train_size, val_size, changepoint_prior_scale_list, 
							 fourier_order_list, window_list, holidays):
	"""
	Hyperparameter tuning - changepoint, fourier_order, holidays
	Inputs
		df                     : dataframe with headers 'ds' and 'y' (necessary for Prophet)
		H                      : forecast horizon
		train_size             : length of training set
		val_size               : length of validation set. Note len(df) = train_size + val_size
		changepoint_prior_scale_list: list of changepoint_prior_scale values to try
		fourier_order_list          : list of fourier_order values to try
		window_list                 : list of upper and lower window values to try
		holidays                    : dataframe containing holidays you will like to model. 
									  Must have 'holiday' and 'ds' columns
	Outputs
		optimum hyperparameters
	"""
	rmse_mean_list = []
	mape_mean_list = []
	mae_mean_list = []
	cp_list = []
	fo_list = []
	wd_list = []
	for changepoint_prior_scale in changepoint_prior_scale_list:
		for fourier_order in fourier_order_list:
			for window in window_list:
				if changepoint_prior_scale is None:
					changepoint_prior_scale = 2.5
				if window is None:
					rmse_mean, mape_mean, mae_mean = get_error_metrics(df, 
																		  H, 
																		  train_size, 
																		  val_size, 
																		  changepoint_prior_scale, 
																		  fourier_order, 
																		  holidays=None)
				else:
					if holidays is not None:
						# Add lower_window and upper_window which extend the holiday out to 
						# [lower_window, upper_window] days around the date
						holidays['lower_window'] = -window
						holidays['upper_window'] = +window
		
					rmse_mean, mape_mean, mae_mean = get_error_metrics(df, 
																		  H, 
																		  train_size, 
																		  val_size, 
																		  changepoint_prior_scale, 
																		  fourier_order, 
																		  holidays)
				rmse_mean_list.append(rmse_mean)
				mape_mean_list.append(mape_mean)
				mae_mean_list.append(mae_mean)
				cp_list.append(changepoint_prior_scale)
				fo_list.append(fourier_order)
				wd_list.append(window)
		
	# Return hyperparam corresponding to lowest error metric
	results = pd.DataFrame({'changepoint_prior_scale': cp_list, 
							'fourier_order': fo_list,
							'window': wd_list,
							'rmse': rmse_mean_list,
							'mape(%)': mape_mean_list,
							'mae': mae_mean_list})
	temp = results[results['rmse'] == results['rmse'].min()]
	changepoint_prior_scale_opt = temp['changepoint_prior_scale'].values[0]
	fourier_order_opt = temp['fourier_order'].values[0]
	window_opt = temp['window'].values[0]
	
	return changepoint_prior_scale_opt, fourier_order_opt, window_opt, results

