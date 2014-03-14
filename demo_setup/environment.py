import time
import traceback

from simpy.core import Environment, EmptySchedule
from simpy.rt import RealtimeEnvironment


class DemoEnvironment(RealtimeEnvironment):

    def __init__(self, initial_time=1356998400, strict=False, real_time=False):
        RealtimeEnvironment.__init__(
            self, initial_time, 1.0, strict)
        self.real_time = real_time

        self.measurement_interval = 3600.0
        self.steps_per_measurement = 3600.0
        self.step_size = 1.0

        self.stop_simulation = False

    def step(self):
        if self.stop_simulation:
            raise EmptySchedule()

        if self.real_time:
            RealtimeEnvironment.step(self)
        else:
            while self.now < time.time():
                Environment.step(self)

            self.env_start = time.time()
            self.real_time = True

    def stop(self):
        self.stop_simulation = True

    def get_day_of_year(self):
        return time.gmtime(self.now).tm_yday
