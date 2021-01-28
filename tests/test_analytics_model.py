# -*- coding: utf-8 -*-
import unittest

from nseta.analytics.model import *
from nseta.archives.archiver import archiver
from baseUnitTest import baseUnitTest
import nseta.common.urls as urls

FIXTURE_PATH = 'tests/fixtures/BANDHANBNK_01-01-2020_08-01-2021'
class TestAnalyticsModel(baseUnitTest):
	def setUp(self, redirect_logs=True):
		super().setUp()
		arch = archiver()
		self.df = archiver.restore_from_path(FIXTURE_PATH)

	def test_get_candle_funcs(self):
		candle_names = get_candle_funcs()
		self.assertEqual(len(candle_names), 56)

	def test_create_pattern_data(self):
		df = create_pattern_data(self.df)
		self.assertEqual(len(df.keys()), 73)
		self.assertIn("CDL3LINESTRIKE", df.columns, str(df.columns))

	def test_pick_best_rank_from_pattern(self):
		df = create_pattern_data(self.df)
		df_ranked = pick_best_rank_from_pattern(df)
		self.assertIn("candlestick_pattern", df_ranked.columns, str(df_ranked.columns))
		self.assertIn("candlestick_match_count", df_ranked.columns, str(df_ranked.columns))
		CDLENGULFING_Bull = df_ranked['candlestick_pattern'].iloc[2]
		self.assertEqual(CDLENGULFING_Bull, 'CDLENGULFING_Bull')

	def test_recognize_candlestick_pattern(self):
		df_pattern = recognize_candlestick_pattern(self.df, False)
		self.assertEqual(len(df_pattern.keys()), 17)
		self.assertIn("candlestick_pattern", df_pattern.columns, str(df_pattern.columns))
		self.assertIn("candlestick_match_count", df_pattern.columns, str(df_pattern.columns))
		NO_PATTERN = df_pattern['candlestick_pattern'].iloc[0]
		self.assertEqual(NO_PATTERN, 'NO_PATTERN')
		self.assertNotIn("CDLSTICKSANDWICH", df_pattern.columns, str(df_pattern.columns))
		df_pattern_steps = recognize_candlestick_pattern(self.df, True)
		self.assertIn("CDLSTICKSANDWICH", df_pattern_steps.columns, str(df_pattern_steps.columns))
		self.assertEqual(len(df_pattern_steps.keys()), 73)

	def test_model_candlestick(self):
		df_pattern = model_candlestick(self.df, False)
		self.assertEqual(len(df_pattern.keys()), 17)
		self.assertIn("candlestick_pattern", df_pattern.columns, str(df_pattern.columns))
		self.assertIn("candlestick_match_count", df_pattern.columns, str(df_pattern.columns))
		NO_PATTERN = df_pattern['candlestick_pattern'].iloc[0]
		self.assertEqual(NO_PATTERN, 'NO_PATTERN')
		self.assertNotIn("CDLSTICKSANDWICH", df_pattern.columns, str(df_pattern.columns))
		df_pattern_steps = model_candlestick(self.df, True)
		self.assertIn("CDLSTICKSANDWICH", df_pattern_steps.columns, str(df_pattern_steps.columns))
		self.assertEqual(len(df_pattern_steps.keys()), 73)

	def tearDown(self):
		super().tearDown()

if __name__ == '__main__':

	suite = unittest.TestLoader().loadTestsFromTestCase(TestAnalyticsModel)
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
