import os
import logging
import json

from server.models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueMonthlyAvg, SensorValueMonthlySum, SensorValueDaily
from server.functions import get_past_time, get_latest_value, get_latest_value_with_unit, get_configuration, get_device_configuration

logger = logging.getLogger('django')
SNIPPET_FOLDER = 'snippets/'


def get_snippet_list():
    output = []
    for filename in os.listdir(SNIPPET_FOLDER):
        if os.path.splitext(filename)[1] == ".py":
            output.append(filename)
    return output


def get_snippet_code(name):
    if name in get_snippet_list():
        with open(SNIPPET_FOLDER + name, "r") as snippet_file:
            return {
                'code': snippet_file.read(),
                'status': 1
            }
    return {'status': 0}


def save_snippet(name, code):
    if os.path.splitext(name)[1] == ".py" and code != "":
        with open(SNIPPET_FOLDER + name, "w") as snippet_file:
            snippet_file.write(code.encode('utf-8'))
        return {
            'code': code,
            'status': 1
        }

    return {'status': 0}


def apply_snippet(code):
    with open('server/user_code.py', "w") as snippet_file:
        snippet_file.write(code.encode('utf-8'))
    return {
        'code': code,
        'status': 1
    }


def get_current_snippet():
    with open('server/user_code.py', "r") as snippet_file:
        return {'code': snippet_file.read()}


def perform_configuration(data):
    configurations = []
    device_configurations = []
    for config in data:
        if all(x in config for x in ['device', 'key', 'value', 'type', 'unit']):
            if config['device'] == '0':
                try:
                    existing_config = Configuration.objects.get(
                        key=config['key'])
                    existing_config.value = config['value']
                    existing_config.value_type = int(
                        config['type'])
                    existing_config.unit = config['unit']
                    existing_config.save()
                except Configuration.DoesNotExist:
                    configurations.append(
                        Configuration(key=config['key'], value=config['value'], value_type=int(config['type']), unit=config['unit']))
            else:
                try:
                    device = Device.objects.get(id=config['device'])
                    for device_type, class_name in Device.DEVICE_TYPES:
                        if device.device_type == device_type:
                            system_class = globals()[class_name]

                    # Make sure that key is present in corresponding system
                    # class
                    if getattr(system_class(0, ForwardableRealtimeEnvironment()), config['key'], None) is not None:
                        try:
                            existing_config = DeviceConfiguration.objects.get(
                                device=device, key=config['key'])
                            existing_config.device = device
                            existing_config.value = config['value']
                            existing_config.value_type = int(
                                config['type'])
                            existing_config.unit = config['unit']
                            existing_config.save()
                        except DeviceConfiguration.DoesNotExist:
                            device_configurations.append(
                                DeviceConfiguration(device=device, key=config['key'], value=config['value'], value_type=int(config['type']), unit=config['unit']))
                except ObjectDoesNotExist:
                    logger.error("Unknown device %s" % config['device'])
                except ValueError:
                    logger.error(
                        "ValueError value_type '%s' not an int" % config['type'])
        else:
            logger.error("Incomplete config data: %s" % config)

    if len(configurations) > 0:
        Configuration.objects.bulk_create(configurations)
    if len(device_configurations) > 0:
        DeviceConfiguration.objects.bulk_create(device_configurations)


def get_modified_configurations(data):
    configurations = list(DeviceConfiguration.objects.all())
    for config in configurations:
        for change in data:
            if str(config.device_id) == change['device'] and config.key == change['key'] and str(config.value_type) == change['type']:
                config.value = change['value']
    return configurations


def get_statistics_for_cogeneration_unit(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.CU):
            system_output = []
            system_output.append(('type', Device.CU))
            system_output.append(('system_id', system.id))
            system_output.append(('system_name', system.name))

            sensor_workload = Sensor.objects.get(device=system, key='workload')
            sensor_consumption = Sensor.objects.get(
                device=system, key='current_gas_consumption')
            workloads = SensorValueDaily.objects.filter(sensor=sensor_workload)
            workloads_monthly_avg = SensorValueMonthlyAvg.objects.filter(
                sensor=sensor_workload)
            consumptions_monthly_sum = SensorValueMonthlySum.objects.filter(
                sensor=sensor_consumption)
            if start is not None:
                workloads = workloads.filter(date__gte=start)
                workloads_monthly_avg = workloads_monthly_avg.filter(
                    date__gte=start)
                consumptions_monthly_sum = consumptions_monthly_sum.filter(
                    date__gte=start)
            if end is not None:
                workloads = workloads.filter(date__lte=end)
                workloads_monthly_avg = workloads_monthly_avg.filter(
                    date__lte=end)
                consumptions_monthly_sum = consumptions_monthly_sum.filter(
                    date__lte=end)

            hours_of_operation = workloads.filter(
                value__gt=0).count() * 24

            system_output.append(
                ('hours_of_operation', round(hours_of_operation, 2)))

            system_output.append(
                ('average_workload', round(workloads_monthly_avg.latest('date').avg, 2)))

            thermal_efficiency = get_device_configuration(
                system, 'thermal_efficiency')
            electrical_efficiency = get_device_configuration(
                system, 'electrical_efficiency')
            max_gas_input = get_device_configuration(system, 'max_gas_input')

            total_gas_consumption = consumptions_monthly_sum.latest('date').sum
            total_electrical_production = total_gas_consumption * \
                electrical_efficiency
            total_thermal_production = total_gas_consumption * \
                thermal_efficiency
            system_output.append(
                ('total_thermal_production', round(total_thermal_production, 2)))
            system_output.append(
                ('total_electrical_production', round(total_electrical_production, 2)))
            system_output.append(
                ('total_gas_consumption', round(total_gas_consumption, 2)))

            gas_costs = get_configuration('gas_costs')
            operating_costs = total_gas_consumption * gas_costs
            system_output.append(
                ('operating_costs', round(operating_costs, 2)))

            values = list(workloads)
            system_output.append(('values_count', len(values)))

            power_ons = 0
            last_time_on = None
            for value in values:
                if last_time_on is None:
                    last_time_on = value.value > 0

                if (last_time_on and value.value == 0) or (not last_time_on and value.value > 0):
                    power_ons += 1
                    last_time_on = not last_time_on

            system_output.append(('power_ons', power_ons))

            output.append(dict(system_output))

    except (Device.DoesNotExist, DeviceConfiguration.DoesNotExist, Configuration.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist, SensorValueMonthlyAvg.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_peak_load_boiler(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.PLB):
            system_output = []
            system_output.append(('type', Device.PLB))
            system_output.append(('system_id', system.id))
            system_output.append(('system_name', system.name))

            sensor_workload = Sensor.objects.get(device=system, key='workload')
            sensor_consumption = Sensor.objects.get(
                device=system, key='current_gas_consumption')
            workloads = SensorValueDaily.objects.filter(sensor=sensor_workload)
            workloads_monthly_avg = SensorValueMonthlyAvg.objects.filter(
                sensor=sensor_workload)
            consumptions_monthly_sum = SensorValueMonthlySum.objects.filter(
                sensor=sensor_consumption)
            if start is not None:
                workloads = workloads.filter(date__gte=start)
                workloads_monthly_avg = workloads_monthly_avg.filter(
                    date__gte=start)
                consumptions_monthly_sum = consumptions_monthly_sum.filter(
                    date__gte=start)
            if end is not None:
                workloads = workloads.filter(date__lte=end)
                workloads_monthly_avg = workloads_monthly_avg.filter(
                    date__lte=end)
                consumptions_monthly_sum = consumptions_monthly_sum.filter(
                    date__lte=end)

            hours_of_operation = workloads.filter(
                value__gt=0).count() * 24

            system_output.append(
                ('hours_of_operation', round(hours_of_operation, 2)))

            system_output.append(
                ('average_workload', round(workloads_monthly_avg.latest('date').avg, 2)))

            thermal_efficiency = get_device_configuration(
                system, 'thermal_efficiency')
            max_gas_input = get_device_configuration(system, 'max_gas_input')

            total_gas_consumption = consumptions_monthly_sum.latest('date').sum
            total_thermal_production = total_gas_consumption * \
                thermal_efficiency
            system_output.append(
                ('total_thermal_production', round(total_thermal_production, 2)))
            system_output.append(
                ('total_gas_consumption', round(total_gas_consumption, 2)))

            gas_costs = get_configuration('gas_costs')
            operating_costs = total_gas_consumption * gas_costs
            system_output.append(
                ('operating_costs', round(operating_costs, 2)))

            values = list(workloads)
            system_output.append(('values_count', len(values)))

            power_ons = 0
            last_time_on = None
            for value in values:
                if last_time_on is None:
                    last_time_on = value.value > 0

                if (last_time_on and value.value == 0) or (not last_time_on and value.value > 0):
                    power_ons += 1
                    last_time_on = not last_time_on

            system_output.append(('power_ons', power_ons))

            output.append(dict(system_output))

    except (Device.DoesNotExist, DeviceConfiguration.DoesNotExist, Configuration.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist, SensorValueMonthlyAvg.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_thermal_consumer(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.TC):
            system_output = []
            system_output.append(('type', system.device_type))
            system_output.append(('system_id', system.id))
            system_output.append(('system_name', system.name))

            sensor_values = SensorValueDaily.objects.all()
            if start is not None:
                sensor_values = sensor_values.filter(date__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(date__lte=end)

            thermal_consumption = 0
            warmwater_consumption = 0

            sensor1 = Sensor.objects.get(
                device=system, key='get_consumption_power')
            for value in sensor_values.filter(sensor=sensor1):
                thermal_consumption += value.value * 24

            sensor2 = Sensor.objects.get(
                device=system, key='get_warmwater_consumption_power')
            for value in sensor_values.filter(sensor=sensor2):
                warmwater_consumption += value.value * 24

            system_output.append(
                ('thermal_consumption', round(thermal_consumption, 2)))
            system_output.append(
                ('warmwater_consumption', round(warmwater_consumption, 2)))

            output.append(dict(system_output))

    except (Device.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_electrical_consumer(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.EC):
            system_output = []
            system_output.append(('type', system.device_type))
            system_output.append(('system_id', system.id))
            system_output.append(('system_name', system.name))

            sensor_values = SensorValueMonthlySum.objects.all()
            if start is not None:
                sensor_values = sensor_values.filter(date__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(date__lte=end)

            electrical_consumption = 0

            power = Sensor.objects.get(
                device=system, key='get_consumption_power')
            for value in sensor_values.filter(sensor=power):
                electrical_consumption += value.sum

            system_output.append(
                ('electrical_consumption', electrical_consumption))

            output.append(dict(system_output))

    except (Device.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_power_meter(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.PM):
            system_output = []
            system_output.append(('type', system.device_type))
            system_output.append(('system_id', system.id))
            system_output.append(('system_name', system.name))

            sensor_values = SensorValueMonthlySum.objects.all()
            if start is not None:
                sensor_values = sensor_values.filter(date__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(date__lte=end)

            total_purchased = 0
            total_fed_in_electricity = 0

            purchase = Sensor.objects.get(
                device=system, key='purchased')
            for value in sensor_values.filter(sensor=purchase):
                total_purchased += value.sum

            feed_in = Sensor.objects.get(
                device=system, key='fed_in_electricity')
            for value in sensor_values.filter(sensor=feed_in):
                total_fed_in_electricity += value.sum

            system_output.append(('total_purchased', total_purchased))
            system_output.append(
                ('total_fed_in_electricity', total_fed_in_electricity))

            output.append(dict(system_output))

    except (Device.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_live_data():
    output = {
        'electrical_consumption': '',
        'cu_workload': '',
        'cu_thermal_production': '',
        'cu_electrical_production': '',
        'cu_operating_costs': '',
        'hs_temperature': '',
        'infeed_costs': '',
        'infeed_reward': '',
        'plb_workload': '',
        'plb_thermal_production': '',
        'plb_operating_costs': '',
        'thermal_consumption': '',
        'warmwater_consumption': '',
        'time': ''
    }

    try:
        output['time'] = SensorValue.objects.all().latest(
            'timestamp').timestamp
        last_month = get_past_time(months=1)

        for system in Device.objects.all():
            if system.device_type == Device.HS:
                output['hs_temperature'] = get_latest_value_with_unit(
                    system, 'get_temperature')
            elif system.device_type == Device.PM:
                output['infeed_costs'] = get_latest_value_with_unit(
                    system, 'purchased')
                output['infeed_reward'] = get_latest_value_with_unit(
                    system, 'fed_in_electricity')
            elif system.device_type == Device.CU:
                output['cu_workload'] = get_latest_value_with_unit(
                    system, 'workload')
                workload = get_latest_value(system, 'workload')
                thermal_production = round(
                    workload * get_device_configuration(system, 'thermal_efficiency') / 100.0, 2)
                output['cu_thermal_production'] = '%s kWh' % thermal_production
                electrical_efficiency = round(
                    workload * get_device_configuration(system, 'electrical_efficiency') / 100.0, 2)
                output[
                    'cu_electrical_production'] = '%s kWh' % electrical_efficiency
                output['cu_operating_costs'] = get_operating_costs(
                    system, last_month)
            elif system.device_type == Device.PLB:
                output['plb_workload'] = get_latest_value_with_unit(
                    system, 'workload')
                thermal_production = round(
                    get_latest_value(system, 'workload') * get_device_configuration(system, 'thermal_efficiency') / 100.0, 2)
                output[
                    'plb_thermal_production'] = '%s kWh' % thermal_production
                output['plb_operating_costs'] = get_operating_costs(
                    system, last_month)
            elif system.device_type == Device.TC:
                output['thermal_consumption'] = get_latest_value_with_unit(
                    system, 'get_consumption_power')
                output['warmwater_consumption'] = get_latest_value_with_unit(
                    system, 'get_warmwater_consumption_power')
            elif system.device_type == Device.EC:
                output['electrical_consumption'] = get_latest_value_with_unit(
                    system, 'get_consumption_power')
    except SensorValue.DoesNotExist:
        logger.debug('SensorValue.DoesNotExist')

    return output


def get_operating_costs(system, start):
    workload = Sensor.objects.get(device=system, key='workload')
    max_gas_input = get_device_configuration(system, 'max_gas_input')
    total_gas_consumption = 0
    for value in SensorValueDaily.objects.filter(sensor=workload, date__gte=start):
        step = (value.value / 100.0) * (120 / 3600.0)
        total_gas_consumption += max_gas_input * step
    return '%s Euro' % round(total_gas_consumption * get_configuration('gas_costs'), 2)
