import unittest
import time
import io
import sys
import logging

import nseta.common.urls as urls
from nseta.common.log import *

class baseUnitTest(unittest.TestCase):
	def setUp(self, redirect_logs=True):
		self.startTime = time.time()
		capturedOutput = io.StringIO()                  # Create StringIO object
		sys.stdout = capturedOutput                     #  and redirect stdout.
		self._capturedOutput = capturedOutput
		self._stream_handler = logging.StreamHandler(sys.stdout)
		default_logger().addHandler(self._stream_handler)
		if redirect_logs:
			logging.disable(logging.DEBUG)

	@property
	def capturedOutput(self):
		return self._capturedOutput

	@property
	def stream_handler(self):
		return self._stream_handler

	def tearDown(self):
		urls.session.close()
		default_logger().removeHandler(self.stream_handler)
		sys.stdout = sys.__stdout__                     # Reset redirect.
		t = time.time() - self.startTime
		print('\n%s: %.3f' % (self.id().ljust(100), t))
