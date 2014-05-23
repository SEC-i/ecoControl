import time
from threading import Thread

import functions


class Worker(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        step = 0
        while True:
            # every minute
            functions.check_thresholds()

            # every 10 minutes
            if step % 10 == 0:
                # functions.refresh_views()
                pass

            # make sure step is within a day
            step = (step + 1) % (60 * 60 * 24)

            time.sleep(60)  # wait a minute
