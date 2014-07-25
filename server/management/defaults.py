# -*- coding: utf-8 -*-
import datetime

from django.utils.timezone import utc
from django.db import connection, ProgrammingError
from django.contrib.auth.models import User

from server.forecasting.systems.data.old_demands import outside_temperatures_2013, outside_temperatures_2012
from server.models import System, Sensor, Configuration, SystemConfiguration, SensorValueDaily, SensorValueHourly, SensorValueMonthlyAvg, SensorValueMonthlySum, WeatherValue


def initialize_default_user():
    if len(User.objects.all()) == 0:
        User.objects.create_superuser('technician', 'bp2013h1@lists.myhpi.de', 'techniker')
        User.objects.create_user('manager', 'bp2013h1@lists.myhpi.de', 'verwaltung')

def initialize_default_scenario():
    if len(System.objects.all()) == 0:
        hs = System(name='Heat Storage', system_type=System.HS)
        hs.save()
        pm = System(name='Power Meter', system_type=System.PM)
        pm.save()
        cu = System(name='Cogeneration Unit', system_type=System.CU)
        cu.save()
        plb = System(name='Peak Load Boiler', system_type=System.PLB)
        plb.save()
        tc = System(name='Thermal Consumer', system_type=System.TC)
        tc.save()
        ec = System(name='Electrical Consumer', system_type=System.EC)
        ec.save()
        print "Default power systems initialized"

        sensors = []
        sensors.append(
            Sensor(system=hs, name='Temperature', key='get_temperature', setter='set_temperature', unit='°C', in_diagram=True, aggregate_avg=True))
        sensors.append(
            Sensor(system=pm, name='Purchased', key='purchased', unit='kWh', aggregate_sum=True))
        sensors.append(
            Sensor(system=pm, name='Fed in Electricity', key='fed_in_electricity', unit='kWh', aggregate_sum=True))
        sensors.append(
            Sensor(system=cu, name='Workload', key='workload', setter='workload', unit='%', in_diagram=True, aggregate_avg=True))
        sensors.append(
            Sensor(system=cu, name='Current Gas Consumption', key='current_gas_consumption', unit='kWh', aggregate_sum=True))
        sensors.append(
            Sensor(system=plb, name='Workload', key='workload', setter='workload', unit='%', in_diagram=True, aggregate_avg=True))
        sensors.append(
            Sensor(system=plb, name='Current Gas Consumption', key='current_gas_consumption', unit='kWh', aggregate_sum=True))
        sensors.append(Sensor(system=tc, name='Thermal Consumption',
                       key='get_consumption_power', setter='current_power', unit='kWh', in_diagram=True, aggregate_sum=True))
        sensors.append(Sensor(system=tc, name='Warm Water Consumption',
                       key='get_warmwater_consumption_power', unit='kWh', in_diagram=True, aggregate_sum=True))
        #necessary to initialize thermal consumer
        sensors.append(Sensor(system=tc, name='Room Temperature',
                        key='temperature_room', setter='temperature_room', unit='°C'))
        sensors.append(Sensor(system=tc, name='Outside Temperature',
                       key='get_outside_temperature', unit='°C', in_diagram=True, aggregate_avg=True))
        sensors.append(Sensor(system=ec, name='Electrical Consumption',
                       key='get_consumption_power', unit='kWh', in_diagram=True, aggregate_sum=True))

        Sensor.objects.bulk_create(sensors)
        print "Default sensors initialized"

        configurations = []
        configurations.append(Configuration(
            key='system_status', value='init', value_type=Configuration.STR, internal=True))
        configurations.append(Configuration(
            key='system_mode', value='', value_type=Configuration.STR, internal=True))
        configurations.append(Configuration(
            key='auto_optimization', value='0', value_type=Configuration.BOOL, internal=True))
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

        system_configurations = []
        system_configurations.append(
            SystemConfiguration(system=cu, key='max_gas_input', value='19.0', value_type=SystemConfiguration.FLOAT, unit='kWh'))
        system_configurations.append(
            SystemConfiguration(system=cu, key='thermal_efficiency', value='65.0', value_type=SystemConfiguration.FLOAT, unit='%'))
        system_configurations.append(
            SystemConfiguration(system=cu, key='electrical_efficiency', value='24.7', value_type=SystemConfiguration.FLOAT, unit='%'))
        system_configurations.append(
            SystemConfiguration(system=cu, key='minimal_workload', value='40.0', value_type=SystemConfiguration.FLOAT, unit='%'))
        system_configurations.append(
            SystemConfiguration(system=cu, key='minimal_off_time', value='600', value_type=SystemConfiguration.INT, unit='seconds', tunable=True))
        system_configurations.append(
            SystemConfiguration(system=cu, key='purchase_price', value='15000', value_type=SystemConfiguration.FLOAT, unit='€'))
        system_configurations.append(
            SystemConfiguration(system=cu, key='purchase_date', value='01.01.2013', value_type=SystemConfiguration.STR, unit=''))
        system_configurations.append(
            SystemConfiguration(system=cu, key='maintenance_interval_hours', value='8000', value_type=SystemConfiguration.INT, unit='h'))
        system_configurations.append(
            SystemConfiguration(system=cu, key='maintenance_interval_powerons', value='2000', value_type=SystemConfiguration.INT, unit=''))

        system_configurations.append(
            SystemConfiguration(system=plb, key='max_gas_input', value='45.0', value_type=SystemConfiguration.FLOAT, unit='kWh'))
        system_configurations.append(
            SystemConfiguration(system=plb, key='thermal_efficiency', value='91.0', value_type=SystemConfiguration.FLOAT, unit='%'))

        system_configurations.append(
            SystemConfiguration(system=hs, key='capacity', value='2500.0', value_type=SystemConfiguration.FLOAT, unit='l'))
        system_configurations.append(
            SystemConfiguration(system=hs, key='min_temperature', value='55.0', value_type=SystemConfiguration.FLOAT, unit='°C', tunable=True))
        system_configurations.append(
            SystemConfiguration(system=hs, key='target_temperature', value='70.0', value_type=SystemConfiguration.FLOAT, unit='°C', tunable=True))
        system_configurations.append(
            SystemConfiguration(system=hs, key='critical_temperature', value='90.0', value_type=SystemConfiguration.FLOAT, unit='°C', tunable=True))

        SystemConfiguration.objects.bulk_create(system_configurations)
        print "Default system configurations initialized"


def initialize_weathervalues():
    if len(WeatherValue.objects.all()) == 0:
        weather_values = []
        base_time = datetime.datetime.strptime(
            '2012-01-01 00:00:00 UTC', '%Y-%m-%d %X %Z').replace(tzinfo=utc)
        timestamp = datetime.datetime.strptime(
            '2013-12-12 23:00:00 UTC', '%Y-%m-%d %X %Z').replace(tzinfo=utc)
        hours = 0
        for temperature in outside_temperatures_2012:  # every day
            target_time = base_time + datetime.timedelta(hours=hours)
            weather_values.append(WeatherValue(timestamp=timestamp,
                                               target_time=target_time,
                                               temperature=temperature))
            hours = hours + 1
        base_time = datetime.datetime.strptime(
            '2013-01-01 00:00:00 UTC', '%Y-%m-%d %X %Z').replace(tzinfo=utc)
        timestamp = datetime.datetime.strptime(
            '2013-12-12 23:00:00 UTC', '%Y-%m-%d %X %Z').replace(tzinfo=utc)
        hours = 0
        for temperature in outside_temperatures_2013:  # every day
            target_time = base_time + datetime.timedelta(hours=hours)
            weather_values.append(WeatherValue(timestamp=timestamp,
                                               target_time=target_time,
                                               temperature=temperature))
            hours = hours + 1

        WeatherValue.objects.bulk_create(weather_values)

        print "Default weather data for 2012 and 2013 initialized"


def initialize_views():
    cursor = connection.cursor()

    try:
        len(SensorValueHourly.objects.all())
    except ProgrammingError:
        cursor.execute('''CREATE VIEW public.server_sensorvaluehourly AS
            SELECT row_number() OVER (ORDER BY t1.timestamp) AS id,
                t1.sensor_id,
                t1.timestamp,
                avg(t1.value) AS value
               FROM ( SELECT server_sensorvalue.sensor_id,
                        '1970-01-01 00:00:00'::timestamp without time zone + '01:00:00'::interval * (date_part('epoch'::text, server_sensorvalue."timestamp")::integer / 3600)::double precision AS timestamp,
                        server_sensorvalue.value
                        FROM server_sensorvalue
                        WHERE timestamp >= (SELECT timestamp from server_sensorvalue ORDER BY timestamp DESC LIMIT 1) - INTERVAL '1 month'
                    ) t1
              GROUP BY  t1.timestamp, t1.sensor_id
              ORDER BY t1.timestamp''')

    try:
        len(SensorValueDaily.objects.all())
    except ProgrammingError:
        cursor.execute('''CREATE MATERIALIZED VIEW server_sensorvaluedaily AS
                    SELECT row_number() OVER (ORDER BY timestamp) AS id,
                        sensor_id,
                        date_trunc('day', timestamp)::timestamp::date AS timestamp,
                        avg(value) AS value
                    FROM ( SELECT server_sensorvalue.sensor_id,
                        '1970-01-01 00:00:00'::timestamp without time zone + '1 day'::interval * (date_part('epoch'::text, server_sensorvalue."timestamp")::integer / 86400)::double precision AS timestamp,
                        server_sensorvalue.value
                        FROM server_sensorvalue) t1
                    GROUP BY  t1.timestamp, t1.sensor_id
                    ORDER BY t1.timestamp;''')
        cursor.execute('''CREATE INDEX server_sensorvaluedaily_date ON server_sensorvaluedaily (timestamp);''')

    try:
        len(SensorValueMonthlySum.objects.all())
    except ProgrammingError:
        cursor.execute('''CREATE MATERIALIZED VIEW server_sensorvaluemonthlysum AS
                     SELECT row_number() OVER (ORDER BY t1.timestamp) AS id,
                        t1.sensor_id,
                        t1.timestamp,
                        sum(t1.value) AS sum
                       FROM ( SELECT date_trunc('month'::text, server_sensorvalue."timestamp")::timestamp::date AS timestamp,
                                server_sensorvalue.sensor_id,
                                server_sensorvalue.value
                               FROM server_sensorvalue INNER JOIN server_sensor ON server_sensor.id=server_sensorvalue.sensor_id
                               WHERE server_sensor.aggregate_sum=TRUE) t1
                      GROUP BY t1.timestamp, t1.sensor_id
                      ORDER BY t1.timestamp
                    WITH DATA;''')

    try:
        len(SensorValueMonthlyAvg.objects.all())
    except ProgrammingError:
        # could be derived from server_sensorvaluehourly
        cursor.execute('''CREATE MATERIALIZED VIEW server_sensorvaluemonthlyavg AS
                     SELECT row_number() OVER (ORDER BY t1.timestamp) AS id,
                        t1.sensor_id,
                        t1.timestamp,
                        avg(t1.value) AS avg
                       FROM ( SELECT date_trunc('month'::text, server_sensorvalue."timestamp")::timestamp::date AS timestamp,
                                server_sensorvalue.sensor_id,
                                server_sensorvalue.value
                               FROM server_sensorvalue INNER JOIN server_sensor ON server_sensor.id=server_sensorvalue.sensor_id
                               WHERE server_sensor.aggregate_avg=TRUE) t1
                      GROUP BY t1.timestamp, t1.sensor_id
                      ORDER BY t1.timestamp
                    WITH DATA;''')
