from time import time
from datetime import datetime

from django.utils.timezone import utc

class BaseSystem(object):
    """Represents a general interface to the energy-systems."""

    def __init__(self, system_id, env):
        self.id = system_id #: `int` identifier
        self.env = env #: `:class:BaseEnvironment`

    def calculate(self):
        pass

    def find_dependent_devices_in(self, system_list):
        pass

    def attach_to_cogeneration_unit(self, system):
        pass

    def attach_to_peak_load_boiler(self, system):
        pass

    def attach_to_thermal_consumer(self, system):
        pass

    def attach_to_electrical_consumer(self, system):
        pass

    def connected(self):
        return True


class BaseEnvironment(object):
    """This class manages the simulation of the energy-systems."""

    def __init__(self, initial_time=None, step_size=120, demo=False, forecast=False):
        if initial_time is None:
            self.now = time()
        else:
            self.now = initial_time
        #: a unix timestamp when the simulation starts, if `None` the current time is used
        self.initial_date = datetime.fromtimestamp(self.now).replace(tzinfo=utc)
        #: `int` value of seconds how often the simulated devices calculate their state
        self.step_size = step_size
        #: `bool` if demo modus is active
        self.demo = demo
        #: `bool` seems to be irrelevant
        self.forecast = forecast

    def get_day_of_year(self):
        """Returns an `int` value of the current simulated day"""
        return time.gmtime(self.now).tm_yday