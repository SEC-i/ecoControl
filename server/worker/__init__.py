import time
from threading import Thread

import functions

WORKER_INTERVAL = 60


class Worker(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            functions.check_thresholds()

            time.sleep(WORKER_INTERVAL)
