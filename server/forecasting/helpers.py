from datetime import datetime
from io import BytesIO
import logging
import array

from django.utils.timezone import utc
from django.db import connection

from server.models import Sensor, SystemConfiguration

logger = logging.getLogger('simulation')


class MeasurementStorage():

    def __init__(self, env, systems, demo=False):
        self.env = env
        self.systems = systems
        self.sensors = Sensor.objects.filter(
            system_id__in=[x.id for x in self.systems])

        if demo:
            # initialize for demo
            self.system_map = []
            self.sensor_values = []
            for system in self.systems:
                for sensor in self.sensors:
                    if system.id == sensor.system.id:
                        self.system_map.append((sensor, system))
        else:
            # initialize for forecasting
            self.forecast_data = [array.array('f') for i in self.sensors]


    def take_and_save(self):
        if self.env.now % 60  != 0:
            return
        timestamp = datetime.utcfromtimestamp(
            self.env.now).replace(tzinfo=utc)
        for (sensor, system) in self.system_map:
            value = getattr(system, sensor.key, None)
            if value is not None:
                # in case value is a function, call that function
                if hasattr(value, '__call__'):
                    value = value()

                self.sensor_values.append((sensor.id, value, timestamp))

        if len(self.sensor_values) > 10000:
            self.flush_data()

    def take_and_cache(self):
        for index, sensor in enumerate(self.sensors):
            for system in self.systems:
                if system.id == sensor.system.id and sensor.in_diagram:
                    value = getattr(system, sensor.key, None)
                    if value is not None:
                        # in case value is a function, call that function
                        if hasattr(value, '__call__'):
                            value = value()

                        self.forecast_data[index].append(float(value))


    def get_cached(self,delete_after=False):
        output = []
        for index, sensor in enumerate(self.sensors):
            if sensor.in_diagram:
                output.append({
                    'id': sensor.id,
                    'system_id': sensor.system_id,
                    'system': sensor.system.name,
                    'name': sensor.name,
                    'unit': sensor.unit,
                    'key': sensor.key,
                    'data': self.forecast_data[index].tolist()
                })
            if delete_after:
                self.forecast_data[index] = []
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

