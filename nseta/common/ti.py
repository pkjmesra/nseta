from nseta.common.log import default_logger, logdebug
import talib as ta

__all__ = ['update_ti', 'get_rsi_df', 'get_mom_df', 'get_dmi_df', 'get_macd_df', 'get_sma_df', 'get_ema_df', 'get_adx_df', 'get_bbands_df', 'get_obv_df']

@logdebug
def update_ti(df):
	try:
		df['RSI'] = get_rsi_df(df)
		df['MOM'] = get_mom_df(df)
		# df['DMI'] = get_dmi_df(df)
		# df[['macd','macdsignal', 'macdhist']] = get_macd_df(df)
		# df[['Close','SMA(10)', 'SMA(50)']] = get_sma_df(df)
		# df = get_ema_df(df)
		# df['ADX'] = get_adx_df(df)
		# df = get_bbands_df(df)
		# df['OBV'] = get_obv_df(df)
	except Exception as e:
		default_logger().debug(e, exc_info=True)
		pass
	except SystemExit:
		pass
	return df

@logdebug
def get_rsi_df(df):
	df['RSI'] = ta.RSI(df['Close'],14)
	return df['RSI']

@logdebug
def get_mom_df(df):
	df['MOM'] = ta.MOM(df['Close'],2)
	return df['MOM']

@logdebug
def get_dmi_df(df):
	df['DMI'] = ta.DX(df['High'],df['Low'],df['Close'],timeperiod=14)
	return df['DMI']

@logdebug
def get_macd_df(df):
	df['macd'], df['macdsignal'], df['macdhist'] = ta.MACDEXT(df['Close'], fastperiod=12, fastmatype=0, slowperiod=26, slowmatype=0, signalperiod=9, signalmatype=0)
	return df[['macd','macdsignal', 'macdhist']]

@logdebug
def get_sma_df(df):
	df['SMA(10)'] = ta.SMA(df['Close'],10)
	df['SMA(50)'] = ta.SMA(df['Close'],50)
	return df[['Close','SMA(10)', 'SMA(50)']]

@logdebug
def get_ema_df(df):
	df['EMA(10)'] = ta.EMA(df['Close'], timeperiod = 10)
	return df[['Close','EMA(10)']]

@logdebug
def get_adx_df(df):
	df['ADX'] = ta.ADX(df['High'],df['Low'], df['Close'], timeperiod=14)
	return df['ADX']

@logdebug
def get_bbands_df(df):
	df['BBands-U'], df['BBands-M'], df['BBands-L'] = ta.BBANDS(df['Close'], timeperiod =20)
	return df[['Close','BBands-U','BBands-M','BBands-L']]

@logdebug
def get_obv_df(df):
	df['OBV'] = ta.OBV(df['Close'], df['Volume'])
	return df['OBV']
