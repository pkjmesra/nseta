# -*- coding: utf-8 -*-
import datetime
import os
import inspect
import threading
from time import time, sleep

from nseta.common.log import tracelog, default_logger
from nseta.common.multithreadedScanner import multithreaded_scan
from nseta.common.history import historicaldata
from nseta.archives.archiver import *
from nseta.resources.resources import *
from nseta.common.tradingtime import *
from nseta.scanner.baseStockScanner import ScannerType

__all__ = ['dataDownloaderJob']

class dataDownloaderJob:
  def __init__(self):
    self._downloaders = {(ScannerType.Intraday).name:dataDownloaderChild(ScannerType.Intraday),}
      # (ScannerType.Live).name:dataDownloaderChild(ScannerType.Live),
      # (ScannerType.Quote).name:dataDownloaderChild(ScannerType.Quote),
      # (ScannerType.Swing).name:dataDownloaderChild(ScannerType.Swing),
      # (ScannerType.Volume).name:dataDownloaderChild(ScannerType.Volume),
      # (ScannerType.TopPick).name:dataDownloaderChild(ScannerType.TopPick),
      # (ScannerType.News).name:dataDownloaderChild(ScannerType.News)}
  
  @property
  def downloaders(self):
    return self._downloaders

  def start(self):
    default_logger().debug('Starting job for downloading data')
    frame = inspect.currentframe()
    args, _, _, kwargs = inspect.getargvalues(frame)
    del(kwargs['frame'])
    del(kwargs['self'])
    kwargs1=dict(kwargs)
    kwargs1['terminate_after_iter'] = 0
    wait_time = 180
    kwargs1['wait_time'] = wait_time
    threads = []
    for key in self.downloaders:
      downloaderChild = self.downloaders[key]
      downloaderChild.shouldRun = True
      b = threading.Thread(name='download_background_{}'.format((downloaderChild.scanner_type).name), target=downloaderChild.download_background, args=[kwargs1], daemon=True)
      b.start()
      threads.append(b)
    for t in threads:
      t.join()

  def stop(self):
    default_logger().debug('Stopping job for downloading data')
    for key in self.downloaders:
      downloaderChild = self.downloaders[key]
      downloaderChild.shouldRun = False

class dataDownloaderChild:
  def __init__(self, scanner_type=ScannerType.Unknown):
    self._stocksdict = {}
    self._instancedict = {}
    self._total_counter = 0
    self._periodicity = 1
    self._time_spent = 0
    self._scanner_type = scanner_type

  @property
  def time_spent(self):
    return self._time_spent

  @time_spent.setter
  def time_spent(self, value):
    self._time_spent = value

  @property
  def periodicity(self):
    return self._periodicity

  @periodicity.setter
  def periodicity(self, value):
    self._periodicity = value

  @property
  def total_counter(self):
    return self._total_counter

  @total_counter.setter
  def total_counter(self, value):
    self._total_counter = value

  @property
  def scanner_type(self):
    return self._scanner_type

  @property
  def runnerFilePath(self):
    return os.path.join(resources.default().user_data_dir,'DO_NOT_DELETE_{}runner.txt'.format((self.scanner_type).name))

  @property
  def shouldRun(self):
    run = os.path.exists(self.runnerFilePath)
    return run

  @shouldRun.setter
  def shouldRun(self, value):
    self.flag_file(value)

  def flag_file(self, shouldCreate):
    runnerTmpFile = self.runnerFilePath
    if not os.path.exists(runnerTmpFile):
      if shouldCreate:
        # Creates a new file
        with open(runnerTmpFile, "w") as fhandle:
          pass
    elif not shouldCreate:
      os.remove(runnerTmpFile)

  @tracelog
  def stocks_list(self, stocks=[]):
    global __scan_counter__
    __scan_counter__ = 0
    # If stocks array is empty, pull stock list from stocks.txt or userstocks.txt file
    stocks = stocks if stocks is not None and len(stocks) > 0 else resources.default().stocks
    self.total_counter = len(stocks)
    return stocks

  @tracelog
  def scan(self, stocks=[]):
    start_time = time()
    stocks = self.stocks_list(stocks)
    frame = inspect.currentframe()
    _, _, _, kwargs = inspect.getargvalues(frame)
    del(kwargs['frame'])
    del(kwargs['self'])
    kwargs['scanner_type'] = self.scanner_type
    kwargs['callbackMethod'] = self.multithreadedScanner_callback
    kwargs['items'] = stocks
    kwargs['max_per_thread'] = 3
    multithreaded_scan(**kwargs)
    end_time = time()
    time_spent = end_time-start_time
    self.time_spent += time_spent

  def multithreadedScanner_callback(self, **kwargs):
      scanner_type = kwargs['scanner_type']
      del(kwargs['scanner_type'])
      self.scan_quanta(**kwargs)
      return None, None

  @tracelog
  def scan_quanta(self, **kwargs):
    stocks = kwargs['items']
    for symbol in stocks:
      try:
        arc = archiver()
        arc.remove_cached_file(arc.get_path(symbol, ResponseType.Intraday), force_clear=True)
        self.ohlc_intraday_history(symbol)
      except Exception as e:
        default_logger().debug('Exception encountered for ' + symbol)
        default_logger().debug(e, exc_info=True)

  @tracelog
  def download_background(self, args):
    iteration = 0
    default_logger().debug(args)
    frame = inspect.currentframe()
    args, _, _, main_args = inspect.getargvalues(frame)
    default_logger().debug(main_args)
    kwargs = main_args['args']
    default_logger().debug(kwargs)
    terminate_after_iter = kwargs['terminate_after_iter']
    wait_time = kwargs['wait_time']
    iteration = 0
    while self.shouldRun:
      iteration = iteration + 1
      if terminate_after_iter > 0 and iteration >= terminate_after_iter:
        self.shouldRun = False
        break
      if not current_datetime_in_ist_trading_time_range():
        default_logger().debug('Running the {} scan for one last time because it is outside the trading hours'.format(self.scanner_type.name))
        terminate_after_iter = iteration
      try:
        self.scan()
      except Exception as e:
        default_logger().debug(e, exc_info=True)
      sleep(wait_time)
    default_logger().debug('Finished all iterations of scanning {}.'.format(self.scanner_type.name))

  
  @tracelog
  def ohlc_intraday_history(self, symbol):
    df = None
    try:
      historyinstance = historicaldata()
      arch = archiver()
      df = historyinstance.daily_ohlc_history(symbol, start=datetime.date.today(), end = datetime.date.today(), intraday=True, type=ResponseType.Intraday, periodicity=self.periodicity)
      if df is not None and len(df) > 0:
        df = self.map_keys(df, symbol)
        arch.archive(df, symbol, ResponseType.Intraday)
      else:
        default_logger().debug('\nEmpty dataframe for {}\n'.format(symbol))
    except Exception as e:
      default_logger().debug(e, exc_info=True)
      return None
    return df

  def map_keys(self, df, symbol):
    try:
      df.loc[:,'Symbol'] = symbol
      df.loc[:,'datetime'] = df.loc[:,'Date']
    except Exception as e:
      default_logger().debug(e, exc_info=True)
    return df
