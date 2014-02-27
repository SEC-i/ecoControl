import sys
import datetime
import traceback

from simpy.core import Environment, EmptySchedule
from simpy.rt import RealtimeEnvironment


class ForwardableRealtimeEnvironment(RealtimeEnvironment):

    def __init__(self, initial_time=1356998400, measurement_interval=3600.0, strict=False):
        RealtimeEnvironment.__init__(
            self, initial_time, 1.0 / measurement_interval, strict)

        # start_time = time.time()
        # self.start_time = 1356998400  # 01.01.2013 00:00
        # quiet by default
        self.verbose = False

        # time to forward
        self.forward = 0

        # timings
        self.measurement_interval = measurement_interval
        self.steps_per_measurement = 30.0  # every 2min
        self.step_size = self.measurement_interval / self.steps_per_measurement  # in seconds

        # function which gets called every step
        self.step_function = None

        self.last_step = self.now
        self.exiting = False

    def step(self):
        if self.exiting:
            #self._stop_simulate()
            raise EmptySchedule()
        try:
            if self.forward > 0:
                forward_to = self.now + self.forward
                sim_delta = self.forward - self.now

                while self.now < forward_to:
                    self.handle_step_function()
                    Environment.step(self)

                self.env_start += self.forward
                self.forward = 0
                self.exiting = True
            else:
                self.handle_step_function()
                RealtimeEnvironment.step(self)
        except:
            traceback.print_exc()

    def handle_step_function(self):
        # call step_function whenever time has changed
        if self.now > self.last_step and self.step_function is not None:
            self.last_step = self.now
            self.step_function()

    def get_hour_of_day(self):
        return self.get_timetuple().tm_hour

    def get_min_of_hour(self):
        return self.get_timetuple().tm_min

    def get_day_of_year(self):
        return self.get_timetuple().tm_yday

    def get_timetuple(self):
        return datetime.datetime.fromtimestamp(self.now).timetuple()

    def log(self, *args):
        if self.verbose and self.now % self.measurement_interval == 0:
            sys.stdout.write('%d' % self.now)
            for string in enumerate(args):
                sys.stdout.write('\t{0}'.format(string[1]))
            sys.stdout.write('\n')
