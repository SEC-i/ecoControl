import sys
import datetime

from simpy.core import Environment
from simpy.rt import RealtimeEnvironment

from data import outside_temperatures_2013


class ForwardableRealtimeEnvironment(RealtimeEnvironment):

    def __init__(self, initial_time=1356998400, granularity=3600.0, strict=False):
        RealtimeEnvironment.__init__(
            self, initial_time, 1.0 / granularity, strict)

        # start_time = time.time()
        # self.start_time = 1356998400  # 01.01.2013 00:00
        # quiet by default
        self.verbose = False

        # time to forward
        self.forward = 0

        # timings
        self.granularity = granularity
        self.accuracy = 30.0  # every 2min
        self.step_size = self.granularity / self.accuracy  # in seconds

        # function which gets called every step
        self.step_function = None

        self.last_step = self.now

    def step(self):
        if self.forward > 0:
            forward_to = self.now + self.forward
            sim_delta = self.forward - self.now

            while self.now < forward_to:
                self.handle_step_function()
                Environment.step(self)

            self.env_start += self.forward
            self.forward = 0
        else:
            self.handle_step_function()
            return RealtimeEnvironment.step(self)

    def handle_step_function(self):
        # call step_function whenever time has changed
        if self.now > self.last_step and self.step_function is not None:
            self.last_step = self.now
            self.step_function()

    def get_outside_temperature(self, offset_days = 0):
        day = (self.get_day_of_year() + offset_days) % 365
        return outside_temperatures_2013[day]

    def get_hour_of_day(self):
        return self.get_timetuple().tm_hour

    def get_day_of_year(self):
        return self.get_timetuple().tm_yday

    def get_timetuple(self):
        return datetime.datetime.fromtimestamp(self.now).timetuple()

    def log(self, *args):
        if self.verbose and self.now % self.granularity == 0:  # each hour:
            sys.stdout.write('%d' % self.now)
            for string in enumerate(args):
                sys.stdout.write('\t{0}'.format(string[1]))
            sys.stdout.write('\n')
