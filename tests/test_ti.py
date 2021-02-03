# -*- coding: utf-8 -*-
import unittest
import logging
import pandas as pd
import numpy as np
from nseta.common.ti import ti
from baseUnitTest import baseUnitTest

class TestTI(baseUnitTest):
	def setUp(self, redirect_logs=True):
		self.sample_dict = {'Date':['2021-02-03'],'Open':[100], 'High':[120], 'Low':[80], 'Close':[110], 'Volume':[10000000]}
		self.sample_row = ['2021-02-03', 100, 120, 80, 110, 10000000]
		super().setUp()

	def test_update_ti_none_df(self):
		t = ti()
		result = t.update_ti(None)
		self.assertEqual(None, result)

	def test_update_ti_rsi(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, rsi=True)
		self.assertTrue('RSI' in result.keys())
		self.assertTrue(np.isnan(result['RSI'].iloc[0]))
		df.drop(['RSI'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, rsi=True)
		self.assertFalse(np.isnan(result['RSI'].iloc[14]))

	def test_update_ti_mom(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, mom=True)
		self.assertTrue('MOM' in result.keys())
		self.assertTrue(np.isnan(result['MOM'].iloc[0]))
		df.drop(['MOM'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, mom=True)
		self.assertFalse(np.isnan(result['MOM'].iloc[14]))

	def test_update_ti_sma(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, sma=True)
		self.assertTrue('SMA(10)' in result.keys())
		self.assertTrue(np.isnan(result['SMA(10)'].iloc[0]))
		df.drop(['SMA(10)', 'SMA(50)'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, sma=True)
		self.assertFalse(np.isnan(result['SMA(10)'].iloc[14]))

	def test_update_ti_ema(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, ema=True)
		self.assertTrue('EMA(9)' in result.keys())
		self.assertTrue(np.isnan(result['EMA(9)'].iloc[0]))
		df.drop(['EMA(9)'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, ema=True)
		self.assertFalse(np.isnan(result['EMA(9)'].iloc[14]))

	def test_update_ti_macd(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, macd=True)
		self.assertTrue('macd(12)' in result.keys())
		self.assertTrue(np.isnan(result['macd(12)'].iloc[0]))
		df.drop(['macd(12)', 'macdsignal(9)', 'macdhist(26)'], axis = 1, inplace = True)
		for n in range(33):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, macd=True)
		self.assertFalse(np.isnan(result['macd(12)'].iloc[33]))

	def test_update_ti_bbands(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, bbands=True)
		self.assertTrue('BBands-U' in result.keys())
		self.assertTrue(np.isnan(result['BBands-U'].iloc[0]))
		df.drop(['BBands-U','BBands-M','BBands-L'], axis = 1, inplace = True)
		for n in range(19):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, bbands=True)
		self.assertFalse(np.isnan(result['BBands-U'].iloc[19]))

	def test_update_ti_obv(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, obv=True)
		self.assertTrue('OBV' in result.keys())
		self.assertFalse(np.isnan(result['OBV'].iloc[0]))

	def test_update_ti_obv_volume_none(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		df.drop(['Volume'], axis = 1, inplace = True)
		result = t.update_ti(df, obv=True)
		self.assertTrue('OBV' in result.keys())
		self.assertTrue(np.isnan(result['OBV'].iloc[0]))

	def test_update_ti_no_pivots(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		df.drop(['Low'], axis = 1, inplace = True)
		result = t.update_ti(df, pivots=True)
		self.assertFalse('PP' in result.keys())

	def test_update_ti_pivots(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, pivots=True)
		self.assertTrue('PP' in result.keys())
		self.assertFalse(np.isnan(result['PP'].iloc[0]))

	def test_update_ti_dmi(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, dmi=True)
		self.assertTrue('DMI' in result.keys())
		df.drop(['DMI'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, dmi=True)
		self.assertFalse(np.isnan(result['DMI'].iloc[14]))

	def test_update_ti_atr(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, atr=True)
		self.assertTrue('ATR' in result.keys())
		df.drop(['ATR'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, atr=True)
		self.assertFalse(np.isnan(result['ATR'].iloc[14]))

	def test_update_ti_natr(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, natr=True)
		self.assertTrue('NATR' in result.keys())
		df.drop(['NATR'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, natr=True)
		self.assertFalse(np.isnan(result['NATR'].iloc[14]))

	def test_update_ti_trange(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, trange=True)
		self.assertTrue('TRANGE' in result.keys())
		df.drop(['TRANGE'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, trange=True)
		self.assertFalse(np.isnan(result['TRANGE'].iloc[14]))

	def test_update_ti_adx(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, adx=True)
		self.assertTrue('ADX' in result.keys())
		self.assertTrue(np.isnan(result['ADX'].iloc[0]))
		df.drop(['ADX'], axis = 1, inplace = True)
		for n in range(34):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, adx=True)
		self.assertFalse(np.isnan(result['ADX'].iloc[33]))

	def test_update_ti_volatility(self):
		t = ti()
		df = pd.DataFrame(self.sample_dict)
		result = t.update_ti(df, volatility=True)
		self.assertTrue('Volatility' in result.keys())
		self.assertTrue(np.isnan(result['Volatility'].iloc[0]))
		df.drop(['Volatility', 'ATR'], axis = 1, inplace = True)
		for n in range(15):
			df = df.append(pd.Series(self.sample_row, index=df.columns), ignore_index=True)
		result = t.update_ti(df, volatility=True)
		self.assertFalse(np.isnan(result['Volatility'].iloc[14]))

	def tearDown(self):
		super().tearDown()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestTI)
	result = unittest.TextTestRunner(verbosity=2).run(suite)
	if six.PY2:
		if result.wasSuccessful():
			print("tests OK")
		for (test, error) in result.errors:
			print("=========Error in: %s===========" % test)
			print(error)
			print("======================================")

		for (test, failures) in result.failures:
			print("=========Error in: %s===========" % test)
			print(failures)
			print("======================================")
