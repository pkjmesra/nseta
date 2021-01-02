import pandas as pd
import io
from nseta.common.urls import equity_symbol_list_url, index_constituents_url
from nseta.common.log import tracelog

def get_symbol_list():
	res = equity_symbol_list_url()
	df = pd.read_csv(io.StringIO(res.content.decode('utf-8')))
	return df

@tracelog
def get_index_constituents_list(index):
	res = index_constituents_url(index.lower())
	df = pd.read_csv(io.StringIO(res.content.decode('utf-8')))
	return df
