import time
from datetime import datetime
from django.utils.timezone import utc

class BaseDevice(object):

    def __init__(self, device_id, env):
        self.id = device_id
        self.env = env
                
        


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

    def __init__(self, initial_time=None, step_size=120, demo=False, forecast=False):
        if initial_time is None:
            self.now = time.time()
        else:
            self.now = initial_time

        self.step_size = step_size
        self.demo_mode = demo
        self.initial_date = datetime.fromtimestamp(self.now).replace(tzinfo=utc)
        self.forecast = forecast

    def get_day_of_year(self):
        return time.gmtime(self.now).tm_yday
    
    def is_demo_simulation(self):
        return self.demo_mode and not self.forecast
