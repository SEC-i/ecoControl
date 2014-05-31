from datetime import datetime
from io import BytesIO
from StringIO import StringIO
from struct import pack
from threading import Thread
import itertools
import logging
import numpy as np

from django.utils.timezone import utc
from django.db import connection

from server.systems import get_user_function
from server.models import Sensor, SensorValue, DeviceConfiguration

logger = logging.getLogger('simulation')


class BulkProcessor(object):

    def __init__(self, env, systems):
        self.env = env
        self.systems = systems

        self.user_function = get_user_function(systems)

    def loop(self):
        while True:
            self.step()
            yield self.env.timeout(self.env.step_size)

    def step(self):
        # execute user function
        self.user_function(*self.systems)

        # call step function for all systems
        for system in self.systems:
            system.step()


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

        # initialize for forecasting
        self.forecast_data = []
        for i in self.sensors:
            self.forecast_data.append([])
        # initialize for demo
        self.device_map = []
        self.sensor_values = []
        for device in self.devices:
            for sensor in self.sensors:
                if device.id == sensor.device.id:
                    self.device_map.append((sensor, device))

    def take_and_save(self):
        # save demo values every 15mins
        if self.env.now % 60 * 60 != 0:
            return
        timestamp = datetime.utcfromtimestamp(
            self.env.now).replace(tzinfo=utc)
        for (sensor, device) in self.device_map:
            value = getattr(device, sensor.key, None)
            if value is not None:
                # in case value is a function, call that function
                if hasattr(value, '__call__'):
                    value = value()

                self.sensor_values.append((sensor.id, value, timestamp))

        if len(self.sensor_values) > 10000:
            self.flush_data()

    def take_and_cache(self):
        if self.env.now % 3600 != 0:
            return

        for index, sensor in enumerate(self.sensors):
            for device in self.devices:
                if device.id == sensor.device.id and sensor.in_diagram:
                    value = getattr(device, sensor.key, None)
                    if value is not None:
                        # in case value is a function, call that function
                        if hasattr(value, '__call__'):
                            value = value()

                        self.forecast_data[index].append(
                            [self.env.now * 1000, round(float(value), 2)])


    def get(self):
        output = []
        for index, sensor in enumerate(self.sensors):
            if sensor.in_diagram:
                output.append({
                    'id': sensor.id,
                    'device_id': sensor.device_id,
                    'device': sensor.device.name,
                    'name': sensor.name,
                    'unit': sensor.unit,
                    'key': sensor.key,
                    'data': self.forecast_data[index]
                })
        return output

    def get_last(self, value):
        index = self.sensors.index(value)
        if len(self.forecast_data[index]) > 0:
            return self.forecast_data[index][-1]  # return newest item
        return None

    def flush_data(self):
        cursor = connection.cursor()
        # Convert floating point numbers to text, write to COPY input

        cpy = BytesIO()
        for row in self.sensor_values:
            vals = [
                row[0], row[1], connection.ops.value_to_db_datetime(row[2])]
            cpy.write('\t'.join([str(val) for val in vals]) + '\n')

        # Insert forecast_data; database converts text back to floating point
        # numbers
        cpy.seek(0)
        cursor.copy_from(cpy, 'server_sensorvalue',
                         columns=('sensor_id', 'value', 'timestamp'))
        connection.commit()

        cursor.execute(
            "SELECT setval('server_sensorvalue_id_seq',(select max(id) FROM server_sensorvalue)+1);")

        self.sensor_values = []


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
        logger.warning("ValueError parsing %s to %s" %
                       (config.value, config.value_type))
    return str(config.value)
