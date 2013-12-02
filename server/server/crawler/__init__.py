#!/usr/bin/env python
import logging

from functions import start_crawling
from server.helpers import write_pidfile_or_fail

logger = logging.getLogger('crawler')

# Crawler thread class
class Crawler():
    def __init__(self):
        #make sure only one instance is running at a time
        self.is_unique_thread = True
        if write_pidfile_or_fail("/tmp/crawler.pid"):
            print " * Crawling..."
            logger.debug("Crawling started")
            start_crawling()
        else:
            logger.debug("Duplicate crawler thread avoided")
            print " * Duplicate crawler thread avoided"