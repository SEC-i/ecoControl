from threading import Thread
from collections import deque

from flask import make_response
from functools import update_wrapper


class SimulationBackgroundRunner(Thread):

    def __init__(self, env):
        Thread.__init__(self)
        self.daemon = True
        self.env = env

    def run(self):
        self.env.run()


class MeasurementCache():

    def __init__(self, env, cu, plb, heat_storage, thermal_consumer, electrical_consumer, cache_limit=24 * 365):
        self.values = ['time', 'cu_workload', 'plb_workload', 'hs_temperature',
                       'thermal_consumption', 'outside_temperature', 'electrical_consumption']

        self.env = env
        self.cu = cu
        self.plb = plb
        self.heat_storage = heat_storage
        self.thermal_consumer = thermal_consumer
        self.electrical_consumer = electrical_consumer

        # initialize empty deques
        self.data = []
        for i in self.values:
            self.data.append(deque(maxlen=cache_limit))

    def take(self):
        # take measurements each hour
        if self.env.now % self.env.measurement_interval == 0:
            for index, value in enumerate(self.values):
                self.data[index].append(round(self.get_mapped_value(value), 2))

    def get(self):
        output = []
        for index, value in enumerate(self.values):
            output.append((value, list(self.data[index])))
        return output

    def clear(self):
        for i in self.data:
            self.data[i].clear()

    def get_mapped_value(self, value):
        if value == 'time':
            return self.env.now
        if value == 'cu_workload':
            return self.cu.workload
        if value == 'plb_workload':
            return self.plb.workload
        if value == 'hs_temperature':
            return self.heat_storage.get_temperature()
        if value == 'thermal_consumption':
            return self.thermal_consumer.get_consumption_power()
        if value == 'outside_temperature':
            return self.thermal_consumer.get_outside_temperature()
        if value == 'electrical_consumption':
            return self.electrical_consumer.get_consumption_power()
        return 0


def parse_hourly_demand_values(namespace, data):
    output = []
    for i in range(24):
        key = namespace + '_' + str(i)
        if key in data:
            output.append(float(request.form[key]))
    return output
