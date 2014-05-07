from threading import Thread
import itertools
from datetime import datetime
import pytz
import logging

from django.db import connection

from server.models import Sensor, SensorValue, DeviceConfiguration

logger = logging.getLogger('simulation')

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


class MeasurementStorage():

    def __init__(self, env, devices, demo=False):
        self.env = env
        self.devices = devices
        self.sensors = Sensor.objects.filter(
            device_id__in=[x.id for x in devices])
        self.demo = demo

        # initialize empty deques
        self.data = []
        for i in self.sensors:
            self.data.append([])


    def take(self):
        if not self.demo and self.env.now % 3600 != 0:
            return
        sensor_values = []
        timestamp = datetime.utcfromtimestamp(self.env.now).replace(tzinfo=pytz.utc)
        i = 0
        for device in self.devices:
            for sensor in Sensor.objects.filter(device_id=device.id):
                value = getattr(device, sensor.key, None)
                if value is not None:
                    # in case value is a function, call that function
                    if hasattr(value, '__call__'):
                        value = value()

                    if self.demo:
                        sensor_values.append((sensor.id, value, timestamp))
                    else:
                        if sensor.in_diagram:
                            self.data[i].append(
                                [int(self.env.now), round(float(value), 2)])
                i += 1

        if len(sensor_values) > 0:
            cursor = connection.cursor()
            cursor.executemany("""INSERT INTO "server_sensorvalue" ("sensor_id", "value", "timestamp") VALUES (%s, %s, %s)""", sensor_values)

    def get(self, start=None):
        if start is not None:
            i = 0
            while i < len(self.data[0]) and start + 1 > self.data[0][i]:
                i += 1

        output = []
        for index, sensor in enumerate(self.sensors):
            if start is not None:
                output.append(
                    (sensor.id, list(itertools.islice(self.data[index], i, None))))
            else:
                output.append((sensor.id, list(self.data[index])))
        return output

    def get_new(self):
        output = []
        for index, sensor in enumerate(self.sensors):
            if sensor.in_diagram:
                output.append({
                    'id': sensor.id,
                    'device_id': sensor.device_id,
                    'name': sensor.name,
                    'unit': sensor.unit,
                    'key': sensor.key,
                    'data': list(self.data[index])
                })
        return output

    def get_last(self, value):
        index = self.sensors.index(value)
        if len(self.data[index]) > 0:
            return self.data[index][-1]  # return newest item
        else:
            return None

    def clear(self):
        for i in self.data:
            self.data[i].clear()


def parse_hourly_demand_values(namespace, data):
    output = []
    for i in range(24):
        key = namespace + '_' + str(i)
        if key in data:
            output.append(float(data[key]))
    return output


def parse_value(config):
    try:
        if config.value_type == DeviceConfiguration.STR:
            return str(config.value)
        elif config.value_type == DeviceConfiguration.INT:
            return int(config.value)
        elif config.value_type == DeviceConfiguration.FLOAT:
            return float(config.value)
        else:
            logger.warning(
                "Couldn't determine type of %s (%s)" % (config.value, config.value_type))
    except ValueError:
        logger.warning("ValueError parsing %s to %s" % (config.value, config.value_type))
    return str(config.value)
