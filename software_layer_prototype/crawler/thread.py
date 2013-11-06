import threading, time
from crawler.functions import add_measurement
from crawler.helpers import write_pidfile_or_fail

# Crawler thread class
class Crawler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		#make sure only one instance is running at a time
		self.unique = True
		if not write_pidfile_or_fail("/tmp/crawler.pid"):
			self.unique = False
		# start thread immediately
		self.start()
	def run(self):
		if self.unique:
			# add new measurement approx. every minute
			print " * Crawling..."
			while(True):
				add_measurement()
				time.sleep(1)
		else:
			print " * Duplicate crawler thread avoided"