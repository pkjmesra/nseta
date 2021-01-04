import os.path
import pandas as pd

__all__ = ['archiver']

class archiver:

	def __init__(self):
		self._archival_dir = os.path.dirname(os.path.realpath(__file__))

	@property
	def archival_directory(self):
		return self._archival_dir
	
	def archive(self, df, file_path):
		if not os.path.exists(file_path):
			file_path = os.path.join(self.archival_directory, file_path)
		df.to_csv(file_path)

	def restore(self, file_path):
		if not os.path.exists(file_path):
			file_path = os.path.join(self.archival_directory, file_path)
		df = pd.read_csv(file_path)
		return df
