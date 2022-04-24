# # -*- coding: utf-8 -*-
# import pandas as pd
# import inspect
# from time import time

# from nseta.common.log import tracelog, default_logger
# from nseta.common.multithreadedScanner import multithreaded_scan
# from nseta.resources.resources import *


# __all__ = ['dataDownloader']

# class dataDownloader:
#   def __init__(self):
#     self._stocksdict = {}
#     self._instancedict = {}
#     self._total_counter = 0
#     self._periodicity = None
#     self._time_spent = 0

#   @property
#   def time_spent(self):
#     return self._time_spent

#   @time_spent.setter
#   def time_spent(self, value):
#     self._time_spent = value

#   @property
#   def total_counter(self):
#     return self._total_counter

#   @total_counter.setter
#   def total_counter(self, value):
#     self._total_counter = value

#   @tracelog
#   def stocks_list(self, stocks=[]):
#     global __scan_counter__
#     __scan_counter__ = 0
#     # If stocks array is empty, pull stock list from stocks.txt or userstocks.txt file
#     stocks = stocks if stocks is not None and len(stocks) > 0 else resources.default().stocks
#     self.total_counter = len(stocks)
#     return stocks

#   @tracelog
#   def scan(self, stocks=[], scanner_type=ScannerType.Unknown):
#     start_time = time()
#     stocks = self.stocks_list(stocks)
#     frame = inspect.currentframe()
#     args, _, _, kwargs = inspect.getargvalues(frame)
#     del(kwargs['frame'])
#     del(kwargs['self'])
#     kwargs['scanner_type'] = scanner_type
#     kwargs['callbackMethod'] = self.multithreadedScanner_callback
#     kwargs['items'] = stocks
#     kwargs['max_per_thread'] = 3
#     list_returned = multithreaded_scan(**kwargs)
#     end_time = time()
#     time_spent = end_time-start_time
#     self.time_spent += time_spent
#     return list_returned.pop(0), list_returned.pop(0)

#   @tracelog
#   def download_background(self, terminate_after_iter=0, wait_time=0):
    
#     RUN_IN_BACKGROUND = True
#     iteration = 0
#     while RUN_IN_BACKGROUND:
#       iteration = iteration + 1
#       if terminate_after_iter > 0 and iteration >= terminate_after_iter:
#         RUN_IN_BACKGROUND = False
#         break
#       if scannerinstance is None:
#         default_logger().debug('scannerinstance is None. Cannot proceed with background scanning')
#         break
#       self._scannerinstance = scannerinstance
#       self.clear_cache(True, force_clear=True)
#       if not current_datetime_in_ist_trading_time_range():
#         click.secho('Running the {} scan for one last time because it is outside the trading hours'.format(self.scanner_type.name), fg='red', nl=True)
#         terminate_after_iter = iteration
#       df, signaldf = scannerinstance.scan(self.stocks, self.scanner_type)
#       self.scan_results(df, signaldf, should_cache= False)
#       time.sleep(wait_time)
#     click.secho('Finished all iterations of scanning {}.'.format(self.scanner_type.name), fg='green', nl=True)
#     return iteration
  
#   def runInBackground(self):
#     return True