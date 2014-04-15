from threading import Thread
from collections import deque
import itertools

from flask import make_response, request
from functools import update_wrapper


class BulkProcessor(object):

    def __init__(self, env, processes):
        self.env = env
        self.processes = processes

    def loop(self):
        while True:
            # call step function for all processes
            for process in self.processes:
                process.step()
            yield self.env.timeout(self.env.step_size)


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
                       'thermal_consumption', 'warmwater_consumption', 'outside_temperature', 'electrical_consumption']

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

    def get(self, start=None):
        if start is not None:
            i = 0
            while i < len(self.data[0]) and start + 1 > self.data[0][i]:
                i += 1

        output = []
        for index, value in enumerate(self.values):
            if start is not None:
                output.append(
                    (value, list(itertools.islice(self.data[index], i, None))))
            else:
                output.append((value, list(self.data[index])))
        return output

    def get_last(self, value):
        index = self.values.index(value)
        if len(self.data[index]) > 0:
            print len(self.data[index])
            return self.data[index][-1]  # return newest item
        else:
            return None

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
        if value == 'warmwater_consumption':
            return self.thermal_consumer.get_warmwater_consumption_power()
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
