#!/usr/bin/env python

# add system path
import sys
sys.path.insert(0, '..')

from optparse import OptionParser
import time

from webapi.main import app, db
from crawler.main import Crawler

if __name__ == '__main__':
	# setting up OptionParser for command line inputs
	parser = OptionParser() 
	parser.add_option("--crawler", action="store_true", dest="crawler_only", default=False, help="Start crawler only") 
	parser.add_option("--webapi", action="store_true", dest="webapi_only", default=False, help="Start webapi only") 
	(options, args) = parser.parse_args()
	
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
		app.run(host="0.0.0.0")