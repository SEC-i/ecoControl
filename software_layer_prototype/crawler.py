#!/usr/bin/env python

from peewee import *
from app import db
from models import *

import threading
import datetime, time, json, urllib2, sys

# crawl data and save sensor data
def addMeasurement():
	url = "http://172.16.19.114/api/sensor/"
	data = json.load(urllib2.urlopen(url))

	sensor_data = Measurement()
	sensor_data.sensor_id = data['sensor_id']
	sensor_data.status = data['status']
	sensor_data.temperature = data['temperature']
	sensor_data.electrical_power = data['electrical_power']
	sensor_data.save()

# Crawler thread class
class Crawler(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.start()
	def run(self):
		# add new measurement approx. every minute
		print " * Crawling..."
		while(True):
			addMeasurement()
			time.sleep(1)

if __name__ == '__main__':
	# instanciate crawler
	Crawler()

	# wait until KeyboardInterrupt
	while True:
		try:
			time.sleep(1)
		except KeyboardInterrupt:
			print "\nStopping crawler..."
			sys.exit(1)
    