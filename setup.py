# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import setuptools  # noqa
from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

setup(
  name = 'nseta',
  packages=setuptools.find_packages(where="./", exclude=["docs", "tests"]),
  version = '0.2',
  description = 'Library to analyse and predict financial data from National Stock Exchange (NSE - India) in pandas dataframe ',
  long_description = long_description,
  long_description_content_type="text/markdown",
  author = 'Praveen K Jha',
  author_email = 'pkjmesra@gmail.com',
  url = 'https://github.com/pkjmesra/nseta', # use the URL to the github repo
  entry_points='''
    [console_scripts]
    nsetacli=nseta.cli.nsetacli:nsetacli
    nseta=nseta.cli.nsetacli:nsetacli
  ''',
  download_url = 'https://github.com/pkjmesra/nseta/archive/v0.2.zip', 
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    ],
  install_requires = install_requires,
  keywords = ['NSE', 'Technical Indicators', 'Backtesting', 'Forecasting'],
),
python_requires='>=3.6',
