import time

class BaseSystem(object):

    def __init__(self, system_id, env):
        self.id = system_id
        self.env = env

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

    def __init__(self, initial_time=None, demo=False):
        if initial_time is None:
            self.now = time.time()
        else:
            self.now = (int(initial_time) / 3600) * 3600.0

        self.demo = demo
        self.step_size = 120

    def get_day_of_year(self):
        return time.gmtime(self.now).tm_yday
