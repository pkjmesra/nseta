from nseta.common.log import default_logger
import talib as ta
import pandas as pd
import numpy as np

__all__ = ['ti']

class ti:

	def update_ti(self, df, rsi=False,mom=False,sma=False,ema=False,macd=False,
		bbands=False,obv=False,dmi=False,atr=False,natr=False,trange=False,
		volatility=False,atre=False,adx=False,pivots=False):
		if df is None or len(df) == 0:
			return df
		try:
			if rsi:
				df['RSI'] = self.get_rsi_df(df)
			if mom:
				df['MOM'] = self.get_mom_df(df)
			if sma:
				df[['Close','SMA(10)', 'SMA(50)']] = self.get_sma_df(df)
			if ema:
				df[['Close','EMA(9)']] = self.get_ema_df(df)
			if macd:
				df[['macd(12)','macdsignal(9)', 'macdhist(26)']] = self.get_macd_df(df)
			if bbands:
				df[['Close','BBands-U','BBands-M','BBands-L']] = self.get_bbands_df(df)
			if obv:
				df['OBV'] = self.get_obv_df(df)
			can_have_pivots = True
			for key in ['Low', 'High', 'Close']:
				if key not in df.keys():
					can_have_pivots = False
					break
			if can_have_pivots:
				if pivots:
					df = self.get_ppsr_df(df)
				if dmi:
					df['DMI'] = self.get_dmi_df(df)
				if atr:
					df['ATR'] = self.get_atr_df(df)
				if natr:
					df['NATR'] = self.get_natr_df(df)
				if trange:
					df['TRANGE'] = self.get_trange_df(df)
				if volatility:
					df['Volatility'] = self.get_atr_ratio(df)
				if atre:
					df['ATRE-F'], df['ATRE-S'], df['ATRE'] = self.get_atr_extreme(df)
				if adx:
					df['ADX'] = self.get_adx_df(df)
		except Exception as e:
			default_logger().debug(e, exc_info=True)
		except SystemExit:
			pass
		return df

	def get_rsi_df(self, df):
		df['RSI'] = ta.RSI(df['Close'],14).apply(lambda x: round(x, 2))
		return df['RSI']

	def get_mom_df(self, df):
		df['MOM'] = ta.MOM(df['Close'],2).apply(lambda x: round(x, 2))
		return df['MOM']

	def get_dmi_df(self, df):
		df['DMI'] = ta.DX(df['High'],df['Low'],df['Close'],timeperiod=14)
		return df['DMI']

	def get_macd_df(self, df):
		df['macd(12)'], df['macdsignal(9)'], df['macdhist(26)'] = ta.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
		df['macd(12)'] = df['macd(12)'].apply(lambda x: round(x, 3))
		df['macdsignal(9)']= df['macdsignal(9)'].apply(lambda x: round(x, 3))
		df['macdhist(26)'] = df['macdhist(26)'].apply(lambda x: round(x, 3))
		return df[['macd(12)','macdsignal(9)', 'macdhist(26)']]

	def get_sma_df(self, df):
		df['SMA(10)'] = ta.SMA(df['Close'],10).apply(lambda x: round(x, 2))
		df['SMA(50)'] = ta.SMA(df['Close'],50).apply(lambda x: round(x, 2))
		return df[['Close','SMA(10)', 'SMA(50)']]

	def get_ema_df(self, df):
		df['EMA(9)'] = ta.EMA(df['Close'], timeperiod = 9).apply(lambda x: round(x, 2))
		return df[['Close','EMA(9)']]

	def get_adx_df(self, df):
		df['ADX'] = ta.ADX(df['High'],df['Low'], df['Close'], timeperiod=14).apply(lambda x: round(x, 2))
		return df['ADX']

	def get_bbands_df(self, df):
		df['BBands-U'], df['BBands-M'], df['BBands-L'] = ta.BBANDS(df['Close'], timeperiod =20)
		df['BBands-U'] = df['BBands-U'].apply(lambda x: round(x, 2))
		df['BBands-M'] = df['BBands-M'].apply(lambda x: round(x, 2))
		df['BBands-L'] = df['BBands-L'].apply(lambda x: round(x, 2))
		return df[['Close','BBands-U','BBands-M','BBands-L']]

	def get_obv_df(self, df):
		if ('Close' not in df.keys()) or ('Volume' not in df.keys()):
			return np.nan
		df['OBV'] = ta.OBV(df['Close'], df['Volume'])
		return df['OBV']

	def get_atr_df(self, df):
		df['ATR'] = ta.ATR(df['High'], df['Low'], df['Close'], timeperiod=14).apply(lambda x: round(x, 2))
		return df['ATR']

	def get_natr_df(self, df):
		df['NATR'] = ta.NATR(df['High'], df['Low'], df['Close'], timeperiod=14).apply(lambda x: round(x, 2))
		return df['NATR']

	def get_trange_df(self, df):
		df['TRANGE'] = ta.TRANGE(df['High'], df['Low'], df['Close']).apply(lambda x: round(x, 2))
		return df['TRANGE']

	def get_atr_extreme(self, df):
		"""
			ATR Exterme: which is based on 《Volatility-Based Technical Analysis》
			TTI is 'Trading The Invisible'

			@return: fasts, slows
		"""
		highs = df['High']
		lows = df['Low']
		closes = df['Close']
		slowPeriod=30
		fastPeriod=3
		atr = self.get_atr_df(df)

		highsMean = ta.EMA(highs, 5)
		lowsMean = ta.EMA(lows, 5)
		closesMean = ta.EMA(closes, 5)

		atrExtremes = np.where(closes > closesMean,
							   ((highs - highsMean)/closes * 100) * (atr/closes * 100),
							   ((lows - lowsMean)/closes * 100) * (atr/closes * 100)
							   )
		fasts = ta.MA(atrExtremes, fastPeriod)
		slows = ta.EMA(atrExtremes, slowPeriod)
		return fasts, slows, np.std(atrExtremes[-slowPeriod:])

	def get_atr_ratio(self, df):
		"""
			ATR(14)/MA(14)
		"""
		closes = df['Close']

		atr = self.get_atr_df(df)
		ma = ta.MA(closes, timeperiod=14)

		volatility = atr/ma

		s = pd.Series(volatility, index=df.index, name='volatility').dropna()
		return pd.DataFrame({'volatility':round(s,2)})

	def get_ppsr_df(self, df):
		PP = pd.Series((df['High'] + df['Low'] + df['Close']) / 3)
		R1 = pd.Series(2 * PP - df['Low'])
		S1 = pd.Series(2 * PP - df['High'])
		R2 = pd.Series(PP + df['High'] - df['Low'])
		S2 = pd.Series(PP - df['High'] + df['Low'])
		R3 = pd.Series(df['High'] + 2 * (PP - df['Low']))
		S3 = pd.Series(df['Low'] - 2 * (df['High'] - PP))
		psr = {'PP':round(PP,2), 'R1':round(R1,2), 'S1':round(S1,2), 'R2':round(R2,2), 'S2':round(S2,2), 'R3':round(R3,2), 'S3':round(S3,2)}
		PSR = pd.DataFrame(psr)
		keys = ['PP','R1','R2','R3','S1','S2','S3']
		for key in keys:
			df[key] = PSR[key]
		return df
