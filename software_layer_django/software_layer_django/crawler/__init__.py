#!/usr/bin/env python
import threading, time
import logging

from software_layer_django.crawler.functions import crawl_and_save_data
from software_layer_django.crawler.helpers import write_pidfile_or_fail

logger = logging.getLogger('crawler')

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
			logger.debug("Crawler started")
			while(True):
				crawl_and_save_data()

				# log function calls if frequency >= 10 seconds
				if self.frequency>9:
					logger.debug("Crawl function called")
				
				time.sleep(self.frequency)
		else:
			logger.debug("Duplicate crawler thread avoided")
			print " * Duplicate crawler thread avoided"
