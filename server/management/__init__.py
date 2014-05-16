# -*- coding: utf-8 -*-
import sys

from django.db.models.signals import post_syncdb
from django.db import connection

from server.models import Device, Sensor, Configuration, DeviceConfiguration

def install_devices(**kwargs):
    if len(Device.objects.all()) == 0:
        hs = Device(name='Heat Storage', device_type=Device.HS)
        hs.save()
        pm = Device(name='Power Meter', device_type=Device.PM)
        pm.save()
        cu = Device(name='Cogeneration Unit', device_type=Device.CU)
        cu.save()
        plb = Device(name='Peak Load Boiler', device_type=Device.PLB)
        plb.save()
        tc = Device(name='Thermal Consumer', device_type=Device.TC)
        tc.save()
        ec = Device(name='Electrical Consumer', device_type=Device.EC)
        ec.save()
        ce = Device(name='Code Executer', device_type=Device.CE)
        ce.save()
        print "Default power systems initialized"

        sensors = []
        sensors.append(
            Sensor(device=hs, name='Temperature', key='get_temperature', setter='set_temperature', unit='°C', in_diagram=True))
        sensors.append(
            Sensor(device=pm, name='Purchased', key='purchased', unit='kWh'))
        sensors.append(
            Sensor(device=pm, name='Fed in Electricity', key='fed_in_electricity', unit='kWh'))
        sensors.append(
            Sensor(device=cu, name='Workload', key='workload', setter='workload', unit='%', in_diagram=True))
        sensors.append(
            Sensor(device=cu, name='Current Gas Consumption', key='current_gas_consumption', unit='kWh'))
        sensors.append(
            Sensor(device=plb, name='Workload', key='workload', setter='workload', unit='%', in_diagram=True))
        sensors.append(
            Sensor(device=plb, name='Current Gas Consumption', key='current_gas_consumption', unit='kWh'))
        sensors.append(Sensor(device=tc, name='Thermal Consumption',
                       key='get_consumption_power', unit='kWh', in_diagram=True))
        sensors.append(Sensor(device=tc, name='Warm Water Consumption',
                       key='get_warmwater_consumption_power', unit='kWh', in_diagram=True))
        sensors.append(Sensor(device=tc, name='Outside Temperature',
                       key='get_outside_temperature', unit='°C', in_diagram=True))
        sensors.append(Sensor(device=ec, name='Electrical Consumption',
                       key='get_consumption_power', unit='kWh', in_diagram=True))

        Sensor.objects.bulk_create(sensors)
        print "Default sensors initialized"

        configurations = []
        configurations.append(Configuration(
            key='system_status', value='init', value_type=Configuration.STR, internal=True))
        configurations.append(Configuration(
            key='system_mode', value='', value_type=Configuration.STR, internal=True))
        configurations.append(Configuration(
            key='apartments', value='12', value_type=Configuration.INT))
        configurations.append(Configuration(
            key='avg_rooms_per_apartment', value='4', value_type=Configuration.INT, unit=''))
        configurations.append(Configuration(
            key='residents', value='22', value_type=Configuration.INT, unit=''))
        configurations.append(Configuration(
            key='avg_thermal_consumption', value='0', value_type=Configuration.FLOAT, unit='kWh'))
        configurations.append(Configuration(
            key='type_of_housing', value='0', value_type=Configuration.INT, unit=''))
        configurations.append(Configuration(
            key='location', value='Berlin', value_type=Configuration.STR, unit=''))
        configurations.append(Configuration(
            key='avg_windows_per_room', value='3', value_type=Configuration.INT, unit=''))
        configurations.append(Configuration(
            key='total_heated_floor', value='650', value_type=Configuration.FLOAT, unit='m²'))
        configurations.append(Configuration(
            key='type_of_residents', value='0', value_type=Configuration.INT, unit=''))
        configurations.append(Configuration(
            key='avg_electrical_consumption', value='0', value_type=Configuration.FLOAT, unit='kWh'))
        configurations.append(Configuration(
            key='type_of_windows', value='0', value_type=Configuration.INT, unit=''))
        configurations.append(Configuration(
            key='gas_costs', value='0.0655', value_type=Configuration.FLOAT, unit='€'))
        configurations.append(Configuration(
            key='feed_in_reward', value='0.0917', value_type=Configuration.FLOAT, unit='€'))
        configurations.append(Configuration(
            key='electrical_costs', value='0.283', value_type=Configuration.FLOAT, unit='€'))

        Configuration.objects.bulk_create(configurations)
        print "Default configurations initialized"

        device_configurations = []
        device_configurations.append(
            DeviceConfiguration(device=cu, key='max_gas_input', value='19.0', value_type=DeviceConfiguration.FLOAT, unit='kWh'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='thermal_efficiency', value='65.0', value_type=DeviceConfiguration.FLOAT, unit='%'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='electrical_efficiency', value='24.7', value_type=DeviceConfiguration.FLOAT, unit='%'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='minimal_workload', value='40.0', value_type=DeviceConfiguration.FLOAT, unit='%'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='minimal_off_time', value='600', value_type=DeviceConfiguration.INT, unit='seconds'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='purchase_price', value='15000', value_type=DeviceConfiguration.FLOAT, unit='€'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='purchase_date', value='01.01.2013', value_type=DeviceConfiguration.STR, unit=''))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='maintenance_interval_hours', value='8000', value_type=DeviceConfiguration.INT, unit='h'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='maintenance_interval_powerons', value='2000', value_type=DeviceConfiguration.INT, unit=''))

        device_configurations.append(
            DeviceConfiguration(device=plb, key='max_gas_input', value='45.0', value_type=DeviceConfiguration.FLOAT, unit='kWh'))
        device_configurations.append(
            DeviceConfiguration(device=plb, key='thermal_efficiency', value='91.0', value_type=DeviceConfiguration.FLOAT, unit='%'))

        device_configurations.append(
            DeviceConfiguration(device=hs, key='capacity', value='2500.0', value_type=DeviceConfiguration.FLOAT, unit='l'))
        device_configurations.append(
            DeviceConfiguration(device=hs, key='min_temperature', value='55.0', value_type=DeviceConfiguration.FLOAT, unit='°C'))
        device_configurations.append(
            DeviceConfiguration(device=hs, key='target_temperature', value='70.0', value_type=DeviceConfiguration.FLOAT, unit='°C'))
        device_configurations.append(
            DeviceConfiguration(device=hs, key='critical_temperature', value='90.0', value_type=DeviceConfiguration.FLOAT, unit='°C'))

        DeviceConfiguration.objects.bulk_create(device_configurations)
        print "Default device configurations initialized"


        if 'test' not in sys.argv:

            cursor = connection.cursor()
            cursor.execute('''CREATE MATERIALIZED VIEW public.server_sensorvaluehourly AS
                SELECT row_number() OVER (ORDER BY t1.timestamp) AS id,
                    t1.sensor_id,
                    t1.timestamp,
                    avg(t1.value) AS value
                   FROM ( SELECT             server_sensorvalue.sensor_id,
                            '1970-01-01 00:00:00'::timestamp without time zone + '01:00:00'::interval * (date_part('epoch'::text, server_sensorvalue."timestamp")::integer / 3600)::double precision AS timestamp,
                            server_sensorvalue.value
                           FROM server_sensorvalue) t1
                  GROUP BY  t1.timestamp, t1.sensor_id
                  ORDER BY t1.timestamp
                 WITH DATA;''')

            cursor.execute('''CREATE VIEW server_sensorvaluedaily AS
                        SELECT row_number() OVER (ORDER BY timestamp) AS id,
                            sensor_id, AVG(value) AS value,
                            date_trunc('day', server_sensorvaluehourly.timestamp) AS timestamp
                        FROM server_sensorvaluehourly INNER JOIN server_sensor ON server_sensor.id=server_sensorvaluehourly.sensor_id
                        GROUP BY sensor_id, timestamp;''')

            cursor.execute('''CREATE MATERIALIZED VIEW server_sensorvaluemonthly AS 
                         SELECT row_number() OVER (ORDER BY t1.timestamp) AS id,
                            t1.sensor_id,
                            t1.timestamp,
                            sum(t1.value) AS sum
                           FROM ( SELECT date_trunc('month'::text, server_sensorvalue."timestamp") AS timestamp,
                                    server_sensorvalue.sensor_id,
                                    server_sensorvalue.value
                                   FROM server_sensorvalue) t1
                          GROUP BY t1.timestamp, t1.sensor_id
                          ORDER BY t1.timestamp
                        WITH DATA;''')

post_syncdb.connect(install_devices)
