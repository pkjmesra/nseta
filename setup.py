# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# import atexit, os
import sys
import setuptools  # noqa
from distutils.core import setup
import nseta

__USERNAME__ = 'pkjmesra'

with open("README.md", "r") as fh:
	long_description = fh.read()
with open("requirements.txt", "r") as fh:
	install_requires = fh.read().splitlines()

SYS_MAJOR_VERSION = str(sys.version_info.major)
SYS_VERSION = SYS_MAJOR_VERSION + '.' +str(sys.version_info.minor)

WHEEL_NAME = 'nseta-'+nseta.__version__+'-py'+SYS_MAJOR_VERSION+'-none-any.whl'
TAR_FILE = 'nseta-'+nseta.__version__+'.tar.gz'
EGG_FILE = 'nseta-'+nseta.__version__+'-py'+SYS_VERSION+'.egg'
DIST_FILES = [WHEEL_NAME, TAR_FILE, EGG_FILE]
DIST_DIR = 'dist/'

# def _post_build():
# 	if "bdist_wheel" in sys.argv:
# 		for count, filename in enumerate(os.listdir(DIST_DIR)):
# 			if filename in DIST_FILES:
# 				os.rename(DIST_DIR + filename, DIST_DIR + filename.replace('nseta-', 'nseta_'+__USERNAME__+'-'))

# atexit.register(_post_build)

setup(
	name = 'nseta',
	packages=setuptools.find_packages(where="./", exclude=["docs", "tests"]),
	include_package_data = True,    # include everything in source control
	package_data={'nseta.resources': ['config.txt', 'stocks.txt']},
	# ...but exclude README.txt from all packages
    exclude_package_data = { '': ['*.yml'] },
	version = nseta.__version__,
	description = 'Library to analyse and predict financial data from National Stock Exchange (NSE - India) in pandas dataframe ',
	long_description = long_description,
	long_description_content_type="text/markdown",
	author = 'Praveen K Jha',
	author_email = __USERNAME__+'@gmail.com',
	license = 'OSI Approved (MIT)',
	url = 'https://github.com/'+__USERNAME__+'/nseta', # use the URL to the github repo
	entry_points='''
	[console_scripts]
	nsetacli=nseta.cli.nsetacli:nsetacli
	nseta=nseta.cli.nsetacli:nsetacli
	''',
	download_url = 'https://github.com/'+__USERNAME__+'/nseta/archive/v' + nseta.__version__ + '.zip',
	classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
	],
	install_requires = install_requires,
	keywords = ['NSE', 'Technical Indicators', 'Backtesting', 'Forecasting'],
	test_suite="tests",
),
python_requires='>=3.6',
