# -*- coding: utf-8 -*-
from django.db import connection, ProgrammingError
from django.contrib.auth.models import User, Group

from server.models import Device, Sensor, Configuration, DeviceConfiguration, SensorValueDaily, SensorValueHourly, SensorValueMonthlyAvg, SensorValueMonthlySum


def initialize_default_user():
    if len(User.objects.all()) == 0:
        technician_group = Group(name="Technician")
        technician_group.save()
        manager_group = Group(name="Manager")
        manager_group.save()

        technician = User(username='bp2013h1', email='bp2013h1@lists.myhpi.de')
        technician.set_password('hirsch')
        technician.save()
        technician.groups.add(technician_group)
        technician.save()

        manager = User(username='witt', password='demo')
        manager.set_password('demo')
        manager.save()
        manager.groups.add(manager_group)
        manager.save()


def initialize_default_scenario():
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
            Sensor(device=hs, name='Temperature', key='get_temperature', setter='set_temperature', unit='°C', in_diagram=True, aggregate_avg=True))
        sensors.append(
            Sensor(device=pm, name='Purchased', key='purchased', unit='kWh', aggregate_sum=True))
        sensors.append(
            Sensor(device=pm, name='Fed in Electricity', key='fed_in_electricity', unit='kWh', aggregate_sum=True))
        sensors.append(
            Sensor(device=cu, name='Workload', key='workload', setter='workload', unit='%', in_diagram=True, aggregate_avg=True))
        sensors.append(
            Sensor(device=cu, name='Current Gas Consumption', key='current_gas_consumption', unit='kWh', aggregate_sum=True))
        sensors.append(
            Sensor(device=plb, name='Workload', key='workload', setter='workload', unit='%', in_diagram=True, aggregate_avg=True))
        sensors.append(
            Sensor(device=plb, name='Current Gas Consumption', key='current_gas_consumption', unit='kWh', aggregate_sum=True))
        sensors.append(Sensor(device=tc, name='Thermal Consumption',
                       key='current_power', setter='current_power', unit='kWh', in_diagram=True, aggregate_sum=True))
        sensors.append(Sensor(device=tc, name='Warm Water Consumption',
                       key='get_warmwater_consumption_power', unit='kWh', in_diagram=True, aggregate_sum=True))
        sensors.append(Sensor(device=tc, name='Room Temperature',
                       key='temperature_room', setter='temperature_room', unit='°C', aggregate_avg=True))
        sensors.append(Sensor(device=tc, name='Outside Temperature',
                       key='get_outside_temperature', unit='°C', in_diagram=True, aggregate_avg=True))
        sensors.append(Sensor(device=ec, name='Electrical Consumption',
                       key='get_consumption_power', unit='kWh', in_diagram=True, aggregate_sum=True))
        
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
        configurations.append(Configuration(
            key='thermal_revenues', value='0.075', value_type=Configuration.FLOAT, unit='€'))
        configurations.append(Configuration(
            key='warmwater_revenues', value='0.065', value_type=Configuration.FLOAT, unit='€'))
        configurations.append(Configuration(
            key='electrical_revenues', value='0.268', value_type=Configuration.FLOAT, unit='€'))

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
            DeviceConfiguration(device=cu, key='minimal_off_time', value='600', value_type=DeviceConfiguration.INT, unit='seconds', tunable=True))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='purchase_price', value='15000', value_type=DeviceConfiguration.FLOAT, unit='€'))
        device_configurations.append(
            DeviceConfiguration(device=cu, key='purchase_date', value='01.01.2013', value_type=DeviceConfiguration.DATE, unit=''))
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
            DeviceConfiguration(device=hs, key='min_temperature', value='55.0', value_type=DeviceConfiguration.FLOAT, unit='°C', tunable=True))
        device_configurations.append(
            DeviceConfiguration(device=hs, key='target_temperature', value='70.0', value_type=DeviceConfiguration.FLOAT, unit='°C', tunable=True))
        device_configurations.append(
            DeviceConfiguration(device=hs, key='critical_temperature', value='90.0', value_type=DeviceConfiguration.FLOAT, unit='°C', tunable=True))

        DeviceConfiguration.objects.bulk_create(device_configurations)
        print "Default device configurations initialized"


def initialize_views():
    cursor = connection.cursor()

    try:
        len(SensorValueHourly.objects.all())
    except ProgrammingError:
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

    try:
        len(SensorValueDaily.objects.all())
    except ProgrammingError:
        cursor.execute('''CREATE VIEW server_sensorvaluedaily AS
                    SELECT row_number() OVER (ORDER BY timestamp) AS id,
                        sensor_id, AVG(value) AS value,
                        date_trunc('day', server_sensorvaluehourly.timestamp)::timestamp::date AS date
                    FROM server_sensorvaluehourly INNER JOIN server_sensor ON server_sensor.id=server_sensorvaluehourly.sensor_id
                    GROUP BY sensor_id, timestamp;''')

    try:
        len(SensorValueMonthlySum.objects.all())
    except ProgrammingError:
        cursor.execute('''CREATE MATERIALIZED VIEW server_sensorvaluemonthlysum AS 
                     SELECT row_number() OVER (ORDER BY t1.date) AS id,
                        t1.sensor_id,
                        t1.date,
                        sum(t1.value) AS sum
                       FROM ( SELECT date_trunc('month'::text, server_sensorvalue."timestamp")::timestamp::date AS date,
                                server_sensorvalue.sensor_id,
                                server_sensorvalue.value
                               FROM server_sensorvalue INNER JOIN server_sensor ON server_sensor.id=server_sensorvalue.sensor_id
                               WHERE server_sensor.aggregate_sum=TRUE) t1
                      GROUP BY t1.date, t1.sensor_id
                      ORDER BY t1.date
                    WITH DATA;''')

    try:
        len(SensorValueMonthlyAvg.objects.all())
    except ProgrammingError:
        # could be derived from server_sensorvaluehourly
        cursor.execute('''CREATE MATERIALIZED VIEW server_sensorvaluemonthlyavg AS 
                     SELECT row_number() OVER (ORDER BY t1.date) AS id,
                        t1.sensor_id,
                        t1.date,
                        avg(t1.value) AS avg
                       FROM ( SELECT date_trunc('month'::text, server_sensorvalue."timestamp")::timestamp::date AS date,
                                server_sensorvalue.sensor_id,
                                server_sensorvalue.value
                               FROM server_sensorvalue INNER JOIN server_sensor ON server_sensor.id=server_sensorvalue.sensor_id
                               WHERE server_sensor.aggregate_avg=TRUE) t1
                      GROUP BY t1.date, t1.sensor_id
                      ORDER BY t1.date
                    WITH DATA;''')
