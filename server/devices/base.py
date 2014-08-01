from time import time, gmtime


class BaseDevice(object):
    """Represents a general interface to the energy-systems."""

    def __init__(self, device_id, env):
        self.id = device_id #: `int` identifier
        self.env = env #: `:class:BaseEnvironment`

    def calculate(self):
        pass

    def find_dependent_devices_in(self, device_list):
        pass

    def attach_to_cogeneration_unit(self, device):
        pass

    def attach_to_peak_load_boiler(self, device):
        pass

    def attach_to_thermal_consumer(self, device):
        pass

    def attach_to_electrical_consumer(self, device):
        pass

    def connected(self):
        return True


class BaseEnvironment(object):
    """This class manages the simulation of the energy-systems."""

    def __init__(self, initial_time=None, step_size=120, demomode=False, forecast=False):
        """ demomode indicates, if running in demomode, not if this is the demo simulation"""
        if initial_time is None:
            self.now = time()
        else:
            self.now = initial_time
        #: a unix timestamp representing the start of simulation
        #: if initial_time is `None` the current time is used
        self.initial_date = self.now
        #: `int` value of seconds how often the simulated devices calculate their state
        self.step_size = step_size
        #: `bool` decides if demo modus is active
        self.demo_mode = demomode
        #: `bool` seems to be irrelevant
        self.forecast = forecast

    def get_day_of_year(self):
        """Returns an `int` value of the current simulated day"""
        return gmtime(self.now).tm_yday

    def is_demo_simulation(self):
        return self.demo_mode and not self.forecast