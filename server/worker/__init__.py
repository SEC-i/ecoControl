import time
from threading import Thread
import logging

from server.forecasting import get_forecast
from server.devices import get_initialized_scenario, get_user_function, execute_user_function

import functions

logger = logging.getLogger('worker')


class Worker(Thread):

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        (self.env, self.devices) = get_initialized_scenario()
        self.user_function = get_user_function(self.devices)

    def run(self):
        step = 0
        while True:
            # every minute
            functions.check_thresholds()

            if not execute_user_function(self.user_function, self.env, self.devices, get_forecast):
                logger.warning('user_function failed')

            # every 10 minutes
            if step % 10 == 0:
                # functions.refresh_views()
                pass

            # make sure step is within a day
            step = (step + 1) % (60 * 60 * 24)

            time.sleep(60)  # wait a minute
