#!/usr/bin/env python
import threading, time
from peewee import *
from crawler.functions import add_CHPUMockMeasurement
from crawler.helpers import write_pidfile_or_fail
from config import Configuration

# instantiate database wrapper
db = PostgresqlDatabase(Configuration.DATABASE)

# Crawler thread class
class Crawler(threading.Thread):
	def __init__(self, frequency=1):
		threading.Thread.__init__(self)
		self.daemon = True
		self.frequency = frequency
		#make sure only one instance is running at a time
		self.is_unique_thread = True
		if not write_pidfile_or_fail("/tmp/crawler.pid"):
			self.is_unique_thread = False
		# start thread immediately
		self.start()
	def run(self):
		if self.is_unique_thread:
			# add new measurement approx. every minute
			print " * Crawling..."
			while(True):
				add_CHPUMockMeasurement()
				time.sleep(self.frequency)
		else:
			print " * Duplicate crawler thread avoided"
