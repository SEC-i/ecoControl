import time
import logging

from simpy.core import Environment, EmptySchedule
from simpy.rt import RealtimeEnvironment

logger = logging.getLogger('simulation')

class ForwardableRealtimeEnvironment(RealtimeEnvironment):

    def __init__(self, initial_time=1356998400, interval=120, strict=False):
        RealtimeEnvironment.__init__(
            self, initial_time, 1.0 / 3600, strict)

        # time to forward
        self.forward = 0
        self.initial_time = initial_time
        self.step_size = interval

        # function which gets called every step
        self.step_function = None
        self.step_function_kwarguments = {}

        self.last_step = self.now
        self.stop_simulation = False
        self.stop_after_forward = False

    def step(self):
        if self.stop_simulation:
            logger.info("Environment: Stop stepping")
            raise EmptySchedule()

        if self.forward > 0:
            forward_to = self.now + self.forward
            sim_delta = self.forward - self.now

            while self.now < forward_to:
                self.handle_step_function()
                Environment.step(self)

            self.env_start += self.forward
            self.forward = 0
            if self.stop_after_forward:
                logger.info("Environment: Stop stepping")
                raise EmptySchedule()
        else:
            self.handle_step_function()
            RealtimeEnvironment.step(self)

    def stop(self):
        self.stop_simulation = True

    def handle_step_function(self):
        # call step_function whenever time has changed
        if self.now > self.last_step and self.step_function is not None:
            self.last_step = self.now
            if self.step_function_kwarguments != {}:
                self.step_function(self.step_function_kwarguments)
            else:
                self.step_function()

    def get_day_of_year(self):
        return time.gmtime(self.now).tm_yday

    def register_step_function(self, function, kwargs={}):
        if self.step_function != None:
            logger.warning("Environment: Overwriting existing step_function " + self.step_function)
        self.step_function = function
        self.step_function_kwarguments = kwargs
