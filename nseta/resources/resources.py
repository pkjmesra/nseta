import configparser
import os.path

__all__ = ['resources']

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
