import configparser
import os.path

__all__ = ['resources', 'RSI','Forecast','Backtest','Scanner']

def split_into_range_int(str_val):
	return sum(((list(range(*[int(b) + c
			for c, b in enumerate(a.split('-'))]))
			if '-' in a else [int(a)]) for a in str_val.split(',')), [])

def split_into_range_str(str_val):
	return sum((([a]) for a in str_val.split(',')), [])

class Default:
	def __init__(self, version=0.6, defaultstocks_path='stocks.txt', UserDataDirectory=None,
		numeric_to_human_format = False):
		self._version = version
		self._defaultstocks_filepath = defaultstocks_path
		self._resources_dir = os.path.dirname(os.path.realpath(__file__))
		self._user_data_dir = UserDataDirectory if len(UserDataDirectory) > 0 else None
		self._numeric_to_human_format = numeric_to_human_format.lower() in ("yes", "true", "t", "1")

	@property
	def version(self):
		return self._version

	@property
	def defaultstocks_filepath(self):
		return self._defaultstocks_filepath

	@property
	def user_data_dir(self):
		return self._user_data_dir

	@property
	def resources_directory(self):
		return self._resources_dir

	@property
	def stocks(self):
		file_path = self.defaultstocks_filepath
		if not os.path.exists(file_path):
			file_path = os.path.join(self.resources_directory, file_path)
		with open(file_path, 'r') as f:
			stocks = [line.rstrip() for line in f]
		return stocks

	@property
	def numeric_to_human_format(self):
		return self._numeric_to_human_format

class Scanner:
	def __init__(self, userstocks_path='userstocks.txt',Background_Scan_Frequency_Intraday=10,
		Background_Scan_Frequency_Live=60,Background_Scan_Frequency_Quotes=60,
		Background_Scan_Frequency_Volume=30,volume_scan_columns=None,swing_scan_columns=None,
		enumerate_volume_scan_signals=False, intraday_scan_columns = None, live_scan_columns=None,
		crossover_reminder_percent=0.075, scan_results_max_count = 30, max_column_length=55):
		self._userstocks_filepath = userstocks_path
		self._Background_Scan_Frequency_Intraday = int(Background_Scan_Frequency_Intraday)
		self._Background_Scan_Frequency_Live = int(Background_Scan_Frequency_Live)
		self._Background_Scan_Frequency_Quotes = int(Background_Scan_Frequency_Quotes)
		self._Background_Scan_Frequency_Volume = int(Background_Scan_Frequency_Volume)
		self._volume_scan_columns = volume_scan_columns
		self._swing_scan_columns = swing_scan_columns
		self._enumerate_volume_scan_signals = enumerate_volume_scan_signals
		self._intraday_scan_columns = intraday_scan_columns
		self._live_scan_columns = live_scan_columns
		self._crossover_reminder_percent = float(crossover_reminder_percent)
		self._scan_results_max_count = int(scan_results_max_count)
		self._max_column_length = int(max_column_length)

	@property
	def userstocks_filepath(self):
		return self._userstocks_filepath

	@property
	def background_scan_frequency_intraday(self):
		return self._Background_Scan_Frequency_Intraday

	@property
	def background_scan_frequency_live(self):
		return self._Background_Scan_Frequency_Live

	@property
	def background_scan_frequency_quotes(self):
		return self._Background_Scan_Frequency_Quotes

	@property
	def background_scan_frequency_volume(self):
		return self._Background_Scan_Frequency_Volume

	@property
	def volume_scan_columns(self):
		return self._volume_scan_columns

	@property
	def swing_scan_columns(self):
		return self._swing_scan_columns

	@property
	def intraday_scan_columns(self):
		return self._intraday_scan_columns

	@property
	def live_scan_columns(self):
		return self._live_scan_columns

	@property
	def enumerate_volume_scan_signals(self):
		return self._enumerate_volume_scan_signals

	@property
	def crossover_reminder_percent(self):
		return self._crossover_reminder_percent

	@property
	def scan_results_max_count(self):
		return self._scan_results_max_count
		
	@property
	def max_column_length(self):
		return self._max_column_length

class Backtest:
	def __init__(self, init_cash=100000, smac_fast_period=10,smac_slow_period=50,
		emac_fast_period=10,emac_slow_period=50,macd_fast_period=12,
		macd_slow_period=26,macd_signal_period=9,macd_sma_period=30,
		macd_dir_period=10,multi_smac_fast_period_range=[10],
		multi_smac_slow_period_range=[10,50],multi_rsi_lower_range=[15,20],
		multi_rsi_upper_range=[75,85],bbands_period=20,bbands_devfactor=2.0,
		rsi_period=14,rsi_upper=75,rsi_lower=25, intraday_margin=0.2,
		max_fund_utilization_per_tran=0.5, commission=0.00067471, strict_strategy = False,
		profit_threshhold_percent = 5, loss_threshhold_percent = 1):
		self._init_cash = float(init_cash)
		self._smac_fast_period = int(smac_fast_period)
		self._smac_slow_period= int(smac_slow_period)
		self._emac_fast_period = int(emac_fast_period)
		self._emac_slow_period= int(emac_slow_period)
		self._macd_fast_period = int(macd_fast_period)
		self._macd_slow_period= int(macd_slow_period)
		self._macd_signal_period= int(macd_signal_period)
		self._macd_sma_period= int(macd_sma_period)
		self._macd_dir_period= int(macd_dir_period)
		self._multi_smac_fast_period_range= multi_smac_fast_period_range
		self._multi_smac_slow_period_range= multi_smac_slow_period_range
		self._multi_rsi_lower_range= multi_rsi_lower_range
		self._multi_rsi_upper_range= multi_rsi_upper_range
		self._bbands_period= int(bbands_period)
		self._bbands_devfactor = float(bbands_devfactor)
		self._rsi_period = int(rsi_period)
		self._rsi_upper = int(rsi_upper)
		self._rsi_lower = int(rsi_lower)
		self._intraday_margin = float(intraday_margin)
		self._max_fund_utilization_per_tran = float(max_fund_utilization_per_tran)
		self._commission = float(commission)
		self._strict_strategy = strict_strategy.lower() in ("yes", "true", "t", "1")
		self._profit_threshhold_percent = float(profit_threshhold_percent)
		self._loss_threshhold_percent = float(loss_threshhold_percent)

	@property
	def init_cash(self):
		return self._init_cash

	@property
	def smac_fast_period(self):
		return self._smac_fast_period

	@property
	def smac_slow_period(self):
		return self._smac_slow_period

	@property
	def emac_fast_period(self):
		return self._emac_fast_period

	@property
	def emac_slow_period(self):
		return self._emac_slow_period

	@property
	def macd_fast_period(self):
		return self._macd_fast_period

	@property
	def macd_slow_period(self):
		return self._macd_slow_period

	@property
	def macd_signal_period(self):
		return self._macd_signal_period

	@property
	def macd_sma_period(self):
		return self._macd_sma_period

	@property
	def macd_dir_period(self):
		return self._macd_dir_period

	@property
	def multi_smac_fast_period_range(self):
		return self._multi_smac_fast_period_range

	@property
	def multi_smac_slow_period_range(self):
		return self._multi_smac_slow_period_range

	@property
	def multi_rsi_lower_range(self):
		return self._multi_rsi_lower_range

	@property
	def multi_rsi_upper_range(self):
		return self._multi_rsi_upper_range

	@property
	def bbands_period(self):
		return self._bbands_period

	@property
	def bbands_devfactor(self):
		return self._bbands_devfactor

	@property
	def rsi_period(self):
		return self._rsi_period

	@property
	def rsi_upper(self):
		return self._rsi_upper

	@property
	def rsi_lower(self):
		return self._rsi_lower

	@property
	def intraday_margin(self):
		return self._intraday_margin

	@property
	def max_fund_utilization_per_tran(self):
		return self._max_fund_utilization_per_tran

	@property
	def commission(self):
		return self._commission

	@property
	def strict_strategy(self):
		return self._strict_strategy

	@property
	def profit_threshhold_percent(self):
		return self._profit_threshhold_percent

	@property
	def loss_threshhold_percent(self):
		return self._loss_threshhold_percent

class RSI:
	def __init__(self, lower=25, upper=75, period = 14):
		self._lower = int(lower)
		self._upper = int(upper)
		self._period = int(period)

	@property
	def upper(self):
		return self._upper
	
	@property
	def lower(self):
		return self._lower

	@property
	def period(self):
		return self._period

class Forecast:
	def __init__(self, lower=1.5, upper=1.5, training_percent=0.75, test_percent=0.25,
		period=7, growth='linear', seasonality_mode='additive', seasonality_name='monthly',
		seasonality_period=21, fourier_order=10, daily_seasonality=True,
		weekly_seasonality=False, yearly_seasonality=False, interval_width=0.95,
		holidays_file_path=None, n_changepoints=20,
		changepoint_prior_scale=2.5, fbprophet_log_level='INFO',
		country_name='IN', future_period_factor=3,plot_font_size=15,
		fbprophet_future_dataframe_frequency='D'):
		self._lower = float(lower)
		self._upper = float(upper)
		self._training_percent = float(training_percent)
		self._test_percent = float(test_percent)
		self._period = int(period)
		self._growth = growth
		self._seasonality_mode = seasonality_mode
		self._seasonality_name = seasonality_name
		self._seasonality_period = int(seasonality_period)
		self._fourier_order = int(fourier_order)
		self._daily_seasonality = daily_seasonality.lower() in ("yes", "true", "t", "1")
		self._weekly_seasonality = weekly_seasonality.lower() in ("yes", "true", "t", "1")
		self._yearly_seasonality = yearly_seasonality.lower() in ("yes", "true", "t", "1")
		self._interval_width = float(interval_width)
		self._holidays_file_path = holidays_file_path
		self._n_changepoints = int(n_changepoints)
		self._changepoint_prior_scale = float(changepoint_prior_scale)
		self._fbprophet_log_level = fbprophet_log_level
		self._country_name = country_name
		self._future_period_factor = int(future_period_factor)
		self._plot_font_size = int(plot_font_size)
		self._fbprophet_future_dataframe_frequency = fbprophet_future_dataframe_frequency
	
	@property
	def lower(self):
		return self._lower

	@property
	def upper(self):
		return self._upper

	@property
	def training_percent(self):
		return self._training_percent

	@property
	def test_percent(self):
		return self._test_percent

	@property
	def period(self):
		return self._period

	@property
	def growth(self):
		return self._growth

	@property
	def seasonality_mode(self):
		return self._seasonality_mode

	@property
	def seasonality_name(self):
		return self._seasonality_name

	@property
	def seasonality_period(self):
		return self._seasonality_period

	@property
	def fourier_order(self):
		return self._fourier_order

	@property
	def daily_seasonality(self):
		return self._daily_seasonality

	@property
	def weekly_seasonality(self):
		return self._weekly_seasonality

	@property
	def yearly_seasonality(self):
		return self._yearly_seasonality

	@property
	def interval_width(self):
		return self._interval_width

	@property
	def holidays_file_path(self):
		return self._holidays_file_path

	@property
	def n_changepoints(self):
		return self._n_changepoints

	@property
	def changepoint_prior_scale(self):
		return self._changepoint_prior_scale

	@property
	def fbprophet_log_level(self):
		return self._fbprophet_log_level

	@property
	def country_name(self):
		return self._country_name

	@property
	def future_period_factor(self):
		return self._future_period_factor

	@property
	def fbprophet_future_dataframe_frequency(self):
		return self._fbprophet_future_dataframe_frequency

	@property
	def plot_font_size(self):
		return self._plot_font_size

class resources:

	def __init__(self, res_dir=None):
		self._resources_dir = os.path.dirname(os.path.realpath(__file__)) if res_dir is None else res_dir
	
	@property
	def resources_directory(self):
		return self._resources_dir

	def default_config(self):
		file_path = "config.txt"
		if not os.path.exists(file_path):
			file_path = os.path.join(self.resources_directory, file_path)
		config = configparser.ConfigParser()
		config.read(file_path)
		return config

	def config_section(self, section_name):
		config = self.default_config()
		if section_name in config:
			return config[section_name]
		else:
			return None

	def config_valueforkey(self, section_name, key_name):
		config = self.default_config()
		if section_name in config:
			section = config[section_name]
			if key_name in section:
				return section[key_name]
			else:
				return None
		else:
			return None

	@classmethod #@staticmethod
	def default(cls):
		r = cls()
		version = r.config_valueforkey('DEFAULT',"version")
		file_path = r.config_valueforkey('DEFAULT',"DefaultStocksFilePath")
		user_dir = r.config_valueforkey('DEFAULT',"UserDataDirectory")
		numeric_to_human_format = r.config_valueforkey('DEFAULT',"numeric_to_human_format")
		return Default(version, file_path, user_dir, numeric_to_human_format)

	@classmethod
	def rsi(cls):
		r = cls()
		lower = r.config_valueforkey('RSI',"Lower")
		upper = r.config_valueforkey('RSI',"Upper")
		period = r.config_valueforkey('RSI',"period")
		return RSI(lower, upper, period)

	@classmethod
	def forecast(cls):
		r = cls()
		lower = r.config_valueforkey('FORECAST',"Lower")
		upper = r.config_valueforkey('FORECAST',"Upper")
		trg_pc = r.config_valueforkey('FORECAST',"Training_percent")
		tst_pc = r.config_valueforkey('FORECAST',"Test_percent")
		period = r.config_valueforkey('FORECAST',"period")
		growth = r.config_valueforkey('FORECAST',"growth")
		sm = r.config_valueforkey('FORECAST',"seasonality_mode")
		sn = r.config_valueforkey('FORECAST',"seasonality_name")
		sp = r.config_valueforkey('FORECAST',"seasonality_period")
		fo = r.config_valueforkey('FORECAST',"fourier_order")
		ds = r.config_valueforkey('FORECAST',"daily_seasonality")
		ws = r.config_valueforkey('FORECAST',"weekly_seasonality")
		ys = r.config_valueforkey('FORECAST',"yearly_seasonality")
		iw = r.config_valueforkey('FORECAST',"interval_width")
		hfp = r.config_valueforkey('FORECAST',"holidays_file_path")
		nc = r.config_valueforkey('FORECAST',"n_changepoints")
		cps = r.config_valueforkey('FORECAST',"changepoint_prior_scale")
		fll = r.config_valueforkey('FORECAST',"fbprophet_log_level")
		cn = r.config_valueforkey('FORECAST',"country_name")
		fpf = r.config_valueforkey('FORECAST',"future_period_factor")
		pfs = r.config_valueforkey('FORECAST',"plot_font_size")
		ffdf = r.config_valueforkey('FORECAST',"fbprophet_future_dataframe_frequency")
		return Forecast(lower, upper, trg_pc, tst_pc, period, growth, sm,sn,sp,fo,ds,ws,ys,iw,hfp,nc,cps,fll,cn,fpf,pfs,ffdf)

	@classmethod
	def backtest(cls):
		r = cls()
		ic = r.config_valueforkey('BACKTEST',"init_cash")
		sfp = r.config_valueforkey('BACKTEST',"smac_fast_period")
		ssp = r.config_valueforkey('BACKTEST',"smac_slow_period")
		efp = r.config_valueforkey('BACKTEST',"emac_fast_period")
		esp = r.config_valueforkey('BACKTEST',"emac_slow_period")
		mfp = r.config_valueforkey('BACKTEST',"macd_fast_period")
		msp = r.config_valueforkey('BACKTEST',"macd_slow_period")
		masp = r.config_valueforkey('BACKTEST',"macd_signal_period")
		msmap = r.config_valueforkey('BACKTEST',"macd_sma_period")
		mdp = r.config_valueforkey('BACKTEST',"macd_dir_period")
		msfpr = split_into_range_int(r.config_valueforkey('BACKTEST',"multi_smac_fast_period_range"))
		msspr = split_into_range_int(r.config_valueforkey('BACKTEST',"multi_smac_slow_period_range"))
		mrlr = split_into_range_int(r.config_valueforkey('BACKTEST',"multi_rsi_lower_range"))
		mrur = split_into_range_int(r.config_valueforkey('BACKTEST',"multi_rsi_upper_range"))
		bp = r.config_valueforkey('BACKTEST',"bbands_period")
		bd = r.config_valueforkey('BACKTEST',"bbands_devfactor")
		rp = r.config_valueforkey('BACKTEST',"rsi_period")
		ru = r.config_valueforkey('BACKTEST',"rsi_upper")
		rl = r.config_valueforkey('BACKTEST',"rsi_lower")
		im = r.config_valueforkey('BACKTEST',"intraday_margin")
		mfupt = r.config_valueforkey('BACKTEST',"max_fund_utilization_per_tran")
		com = r.config_valueforkey('BACKTEST',"commission")
		ss = r.config_valueforkey('BACKTEST',"strict_strategy")
		ptp = r.config_valueforkey('BACKTEST',"profit_threshhold_percent")
		ltp = r.config_valueforkey('BACKTEST',"loss_threshhold_percent")
		
		return Backtest(ic, sfp,ssp,efp,esp,mfp,msp,masp,msmap,mdp,msfpr,msspr,mrlr,mrur,bp,bd,rp,ru,rl,im,mfupt,com,ss,ptp,ltp)

	@classmethod
	def scanner(cls):
		r = cls()
		usfp = r.config_valueforkey('SCANNER',"UserStocksFilePath")
		bsfi = r.config_valueforkey('SCANNER',"Background_Scan_Frequency_Intraday")
		bsfl = r.config_valueforkey('SCANNER',"Background_Scan_Frequency_Live")
		bsfq = r.config_valueforkey('SCANNER',"Background_Scan_Frequency_Quotes")
		bsfv = r.config_valueforkey('SCANNER',"Background_Scan_Frequency_Volume")
		vsc = split_into_range_str(r.config_valueforkey('SCANNER',"volume_scan_columns"))
		ssc = split_into_range_str(r.config_valueforkey('SCANNER',"swing_scan_columns"))
		evss = r.config_valueforkey('SCANNER',"enumerate_volume_scan_signals").lower() in ("yes", "true", "t", "1")
		isc = split_into_range_str(r.config_valueforkey('SCANNER',"intraday_scan_columns"))
		lsc = split_into_range_str(r.config_valueforkey('SCANNER',"live_scan_columns"))
		crp = r.config_valueforkey('SCANNER',"crossover_reminder_percent")
		srmc = r.config_valueforkey('SCANNER',"scan_results_max_count")
		mcl = r.config_valueforkey('SCANNER',"max_column_length")
		return Scanner(usfp, bsfi, bsfl,bsfq, bsfv,vsc,ssc, evss,isc,lsc,crp,srmc,mcl)
