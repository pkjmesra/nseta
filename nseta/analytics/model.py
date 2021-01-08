import numpy as np
from nseta.analytics.candle_rankings import candle_rankings
from nseta.common.log import *
import talib
from itertools import compress

__all__ = ['model_candlestick', 'get_candle_funcs','create_pattern_data', 'pick_best_rank_from_pattern', 'recognize_candlestick_pattern']

# patterns not found in the patternsite.com
exclude_items = ('CDLCOUNTERATTACK',
				 'CDLLONGLINE',
				 'CDLSHORTLINE',
				 'CDLSTALLEDPATTERN',
				 'CDLKICKINGBYLENGTH')

def get_candle_funcs():
	funcs = talib.get_function_groups()['Pattern Recognition']
	candle_names = [candle for candle in funcs if candle not in exclude_items]

	return candle_names

'''
TA-Lib creates individual columns for each pattern. While 0 corresponds 
to no pattern, positive values represent bullish patterns and negative 
values represent bearish patterns.
'''
@tracelog
def create_pattern_data(data_frame):
	df = data_frame
	# extract OHLC
	O = df['Open'].astype(float)
	H = df['High'].astype(float)
	L = df['Low'].astype(float)
	C = df['Close'].astype(float)

	candle_names = get_candle_funcs()

	# create columns for each pattern
	for candle in candle_names:
		# below is same as;
		# df["CDL3LINESTRIKE"] = talib.CDL3LINESTRIKE(O, H, L, C)
		df[candle] = getattr(talib, candle)(O, H, L, C)

	return df

'''
Creates the pattern labels and found pattern counts.
We basically have 3 cases:
	No Pattern: Fill the cell with “NO_PATTERN”
	Single Pattern: Fill the cell with Pattern Name
	Multiple Patterns: Fill the cell with lowest (best) ranking Pattern Name
'''
@tracelog
def pick_best_rank_from_pattern(data_frame):
	df = data_frame
	df['candlestick_pattern'] = np.nan
	df['candlestick_match_count'] = np.nan
	candle_names = get_candle_funcs()

	for index, row in df.iterrows():

		# no pattern found
		if len(row[candle_names]) - sum(row[candle_names] == 0) == 0:
			df.loc[index,'candlestick_pattern'] = "NO_PATTERN"
			df.loc[index, 'candlestick_match_count'] = 0
		# single pattern found
		elif len(row[candle_names]) - sum(row[candle_names] == 0) == 1:
			# bull pattern 100 or 200
			if any(row[candle_names].values > 0):
				pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bull'
				df.loc[index, 'candlestick_pattern'] = pattern
				df.loc[index, 'candlestick_match_count'] = 1
			# bear pattern -100 or -200
			else:
				pattern = list(compress(row[candle_names].keys(), row[candle_names].values != 0))[0] + '_Bear'
				df.loc[index, 'candlestick_pattern'] = pattern
				df.loc[index, 'candlestick_match_count'] = 1
		# multiple patterns matched -- select best performance
		else:
			# filter out pattern names from bool list of values
			patterns = list(compress(row[candle_names].keys(), row[candle_names].values != 0))
			container = []
			for pattern in patterns:
				if row[pattern] > 0:
					container.append(pattern + '_Bull')
				else:
					container.append(pattern + '_Bear')
				rank_list = [candle_rankings[p] for p in container]
				if len(rank_list) == len(container):
					rank_index_best = rank_list.index(min(rank_list))
					df.loc[index, 'candlestick_pattern'] = container[rank_index_best]
					df.loc[index, 'candlestick_match_count'] = len(container)

	return df

'''
We will extract candlestick patterns using TA-Lib (supports 61 patterns as of Sep 2020). 
We will rank them based on the “Overall performance rank” and select the best performance 
pattern for each candle.
'''
@tracelog
def recognize_candlestick_pattern(data_frame, steps):
	"""
	Recognizes candlestick patterns and appends 2 additional columns to df;
	1st - Best Performance candlestick pattern matched by www.thepatternsite.com
	2nd - # of matched patterns
	"""
	df = create_pattern_data(data_frame)
	candle_names = get_candle_funcs()
	df = pick_best_rank_from_pattern(df)

	# clean up candle columns
	if not steps:
		cols_to_drop = candle_names
		df.drop(cols_to_drop, axis = 1, inplace = True)

	return df

@tracelog
def model_candlestick(df, steps):
	return recognize_candlestick_pattern(df, steps)

