import logging
import os
import time
import warnings
import inspect

from functools import wraps
# from inspect import getcallargs, getfullargspec
from collections import OrderedDict, Iterable
from itertools import *

__all__ = ['setup_custom_logger', 'default_logger', 'log_to', 'tracelog', 'suppress_stdout_stderr']
__trace__ = False
__filter__ = None
__DEBUG__ = False

class filterlogger:
	def __init__(self, logger=None):
		self._logger = logger

	@property
	def logger(self):
		return self._logger

	@property
	def level(self):
		return self.logger.level

	@level.setter
	def level(self, level):
		self.logger.setLevel(level)

	@staticmethod
	def getlogger(logger):
		global __filter__
		if __filter__ is not None:
			return filterlogger(logger=logger)
		else:
			return logger

	def debug(self, e, exc_info=False):
		global __filter__
		line = str(e)
		global __DEBUG__
		if __DEBUG__:
			frame = inspect.stack()[1]
			filename = (frame[0].f_code.co_filename).rsplit('/', 1)[1]
			components = str(frame).split(',')
			line = '{} - {} - {}\n{}'.format(filename, components[5],components[6] , line)
			if __filter__ in line.upper():
				self.logger.debug(line, exc_info=exc_info)

	def info(self, line):
		global __filter__
		if __filter__ in line.upper():
			self.logger.info(line)
	
	def warn(self, line):
		global __filter__
		if __filter__ in line.upper():
			self.logger.warn(line)

	def error(self, line):
		self.logger.error(line)

	def setLevel(self, level):
		self.logger.setLevel(level)
	
	def critical(self, line):
		self.logger.critical(line)

	def addHandler(self, hdl):
		self.logger.addHandler(hdl)

	def removeHandler(self, hdl):
		self.logger.removeHandler(hdl)

def setup_custom_logger(name, levelname=logging.DEBUG, trace=False, log_file_path='logs.log', filter=None):
	trace_formatter = logging.Formatter(fmt='\n%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(module)s - %(funcName)s - %(lineno)d\n%(message)s\n')
	console_info_formatter = logging.Formatter(fmt='\n%(levelname)s - %(filename)s(%(funcName)s - %(lineno)d)\n%(message)s\n')
	global __trace__
	__trace__ = trace

	global __filter__
	__filter__ = filter if filter is None else filter.upper()

	logger = logging.getLogger(name)
	logger.setLevel(levelname)

	consolehandler = logging.StreamHandler()
	consolehandler.setFormatter(console_info_formatter if levelname == logging.INFO else trace_formatter)
	consolehandler.setLevel(levelname)
	logger.addHandler(consolehandler)

	if levelname == logging.DEBUG:
		filehandler = logging.FileHandler(log_file_path)
		filehandler.setFormatter(trace_formatter)
		filehandler.setLevel(levelname)
		logger.addHandler(filehandler)
		global __DEBUG__
		__DEBUG__ = True
		logger.debug('Logging started. Filter:{}'.format(filter))

	if trace:
		tracelogger = logging.getLogger('nseta_file_logger')
		tracelogger.setLevel(levelname)
		tracelogger.addHandler(consolehandler)
		if levelname == logging.DEBUG:
			tracelogger.addHandler(filehandler)
		logger.debug('Tracing started')
	# Turn off pystan warnings
	warnings.simplefilter("ignore", DeprecationWarning)
	warnings.simplefilter("ignore", FutureWarning)
	
	return logger

def default_logger():
	return filterlogger.getlogger(logging.getLogger('nseta'))

def file_logger():
	return filterlogger.getlogger(logging.getLogger('nseta_file_logger'))

def trace_log(line):
	global __trace__
	if __trace__:
		default_logger().info(line)
	else:
		file_logger().info(line)

def flatten(l):
	"""Flatten a list (or other iterable) recursively"""
	for el in l:
		if isinstance(el, Iterable) and not isinstance(el, str):
			for sub in flatten(el):
				yield sub
		else:
			yield el

def getargnames(func):
	"""Return an iterator over all arg names, including nested arg names and varargs.
	Goes in the order of the functions argspec, with varargs and
	keyword args last if present."""
	(args, varargs, varkw, defaults, kwonlyargs, kwonlydefaults, annotations) = inspect.getfullargspec(func)
	return chain(flatten(args), filter(None, [varargs, varkw]))

def getcallargs_ordered(func, *args, **kwargs):
	"""Return an OrderedDict of all arguments to a function.
	Items are ordered by the function's argspec."""
	argdict = inspect.getcallargs(func, *args, **kwargs)
	return OrderedDict((name, argdict[name]) for name in getargnames(func))

def describe_call(func, *args, **kwargs):
	yield "Calling %s with args:" % func.__name__
	for argname, argvalue in getcallargs_ordered(func, *args, **kwargs).items():
		yield "\t%s = %s" % (argname, repr(argvalue))

def log_to(logger_func):
	"""A decorator to log every call to function (function name and arg values).
	logger_func should be a function that accepts a string and logs it
	somewhere. The default is logging.debug.
	If logger_func is None, then the resulting decorator does nothing.
	This is much more efficient than providing a no-op logger
	function: @log_to(lambda x: None).
	"""
	if logger_func is not None:
		def decorator(func):
			@wraps(func)
			def wrapper(*args, **kwargs):
				global __DEBUG__
				if __DEBUG__:
					frame = inspect.stack()[1]
					filename = (frame[0].f_code.co_filename).rsplit('/', 1)[1]
					components = str(frame).split(',')
					func_description = '{} - {} - {}'.format(filename, components[5],components[6])
					description = func_description
					for line in describe_call(func, *args, **kwargs):
						description = description + "\n" + line
					logger_func(description)
					startTime = time.time()
					ret_val = func(*args, **kwargs)
					time_spent = time.time() - startTime
					logger_func('\n%s called (%s): %.3f  (TIME_TAKEN)' % (func_description, func.__name__, time_spent))
					return ret_val
				else:
					return func(*args, **kwargs)
			return wrapper
	else:
		decorator = lambda x: x
	return decorator

tracelog = log_to(trace_log)

# def timeit(method):
#     def timed(*args, **kw):
#         ts = time.time()
#         result = method(*args, **kw)
#         te = time.time()
#         if 'log_time' in kw:
#             name = kw.get('log_name', method.__name__.upper())
#             kw['log_time'][name] = int((te - ts) * 1000)
#         else:
#             print ('%r  %2.2f ms' % \
#                   (method.__name__, (te - ts) * 1000))
#         return result
#     return timed

class suppress_stdout_stderr(object):
	'''
	A context manager for doing a "deep suppression" of stdout and stderr in
	Python, i.e. will suppress all print, even if the print originates in a
	compiled C/Fortran sub-function.
	   This will not suppress raised exceptions, since exceptions are printed
	to stderr just before a script exits, and after the context manager has
	exited (at least, I think that is why it lets exceptions through).

	'''
	def __init__(self):
		# Open a pair of null files
		self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
		# Save the actual stdout (1) and stderr (2) file descriptors.
		self.save_fds = [os.dup(1), os.dup(2)]

	def __enter__(self):
		# Assign the null pointers to stdout and stderr.
		os.dup2(self.null_fds[0], 1)
		os.dup2(self.null_fds[1], 2)

	def __exit__(self, *_):
		# Re-assign the real stdout/stderr back to (1) and (2)
		os.dup2(self.save_fds[0], 1)
		os.dup2(self.save_fds[1], 2)
		# Close the null files
		for fd in self.null_fds + self.save_fds:
			os.close(fd)
