#!/usr/bin/env python

# add system path
import sys
sys.path.insert(0, '..')

from optparse import OptionParser
import time

from models import *
from webapi.app import app
from crawler import Crawler
import webapi.views


if __name__ == '__main__':
	# setting up OptionParser for command line inputs
	parser = OptionParser() 
	parser.add_option("--crawler", action="store_true", dest="crawler_only", default=False, help="Start crawler only") 
	parser.add_option("--webapi", action="store_true", dest="webapi_only", default=False, help="Start webapi only")
	parser.add_option("--create-tables", action="store_true", dest="create_tables", default=False, help="Create tables if they don't exist")
	parser.add_option("--drop-tables", action="store_true", dest="drop_tables", default=False, help="Drop tables if they exist")  
	(options, args) = parser.parse_args()

	if options.drop_tables:
		drop_tables()

	if options.create_tables:
		create_tables()

	add_CHPUMock()
	if not options.webapi_only:
		Crawler()
		# while true loop let's thread running
		if options.crawler_only:
			# wait until KeyboardInterrupt
			while True:
				try:
					time.sleep(1)
				except KeyboardInterrupt:
					print "\nStopping crawler..."
					sys.exit(1)

	if not options.crawler_only:
		#webapi.views.addURLs(app)
		app.run(host="0.0.0.0")

		#app.run()
		


