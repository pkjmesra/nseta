import configparser
import os.path

__all__ = ['resources', 'RSI','Forecast']

class RSI:
	def __init__(self, lower, upper):
		self._lower = int(lower)
		self._upper = int(upper)

	@property
	def upper(self):
		return self._upper
	
	@property
	def lower(self):
		return self._lower

class Forecast:
	def __init__(self, lower, upper, training_percent, test_percent):
		self._lower = float(lower)
		self._upper = float(upper)
		self._training_percent = float(training_percent)
		self._test_percent = float(test_percent)

	@property
	def upper(self):
		return self._upper
	
	@property
	def lower(self):
		return self._lower

	@property
	def training_percent(self):
		return self._training_percent

	@property
	def test_percent(self):
		return self._test_percent

class resources:

	def __init__(self):
		self._resources_dir = os.path.dirname(os.path.realpath(__file__))
	
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
	def default_stocks(cls):
		r = cls()
		file_path = r.config_valueforkey('DEFAULT',"DefaultStocks")
		if not os.path.exists(file_path):
			file_path = os.path.join(r.resources_directory, file_path)
		with open(file_path, 'r') as f:
			stocks = [line.rstrip() for line in f]
		return stocks

	@classmethod
	def rsi(cls):
		r = cls()
		lower = r.config_valueforkey('RSI',"Lower")
		upper = r.config_valueforkey('RSI',"Upper")
		return RSI(lower, upper)

	@classmethod
	def forecast(cls):
		r = cls()
		lower = r.config_valueforkey('FORECAST',"Lower")
		upper = r.config_valueforkey('FORECAST',"Upper")
		trg_pc = r.config_valueforkey('FORECAST',"Training_percent")
		tst_pc = r.config_valueforkey('FORECAST',"Test_percent")
		return Forecast(lower, upper, trg_pc, tst_pc)
