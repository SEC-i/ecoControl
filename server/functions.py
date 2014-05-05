import logging
from datetime import datetime
import dateutil.relativedelta

from django.core.exceptions import ObjectDoesNotExist

from models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue

from forecasting.environment import ForwardableRealtimeEnvironment
from forecasting.systems.code import CodeExecuter
from forecasting.systems.producers import CogenerationUnit, PeakLoadBoiler
from forecasting.systems.storages import HeatStorage, PowerMeter
from forecasting.systems.consumers import ThermalConsumer, ElectricalConsumer
from forecasting.helpers import parse_value


logger = logging.getLogger('django')


def perform_configuration(data):
    configurations = []
    device_configurations = []
    for config in data:
        if all(x in config for x in ['device_id', 'key', 'value', 'value_type']):
            if config['device_id'] == '0':
                try:
                    existing_config = Configuration.objects.get(
                        key=config['key'])
                    existing_config.value = config['value']
                    existing_config.value = value_type = int(
                        config['value_type'])
                    existing_config.save()
                except Configuration.DoesNotExist:
                    configurations.append(
                        Configuration(key=config['key'], value=config['value'], value_type=int(config['value_type'])))
            else:
                try:
                    device = Device.objects.get(id=config['device_id'])
                    for device_type, class_name in Device.DEVICE_TYPES:
                        if device.device_type == device_type:
                            system_class = globals()[class_name]

                    # Make sure that key is present in corresponding system
                    # class
                    if getattr(system_class(0, ForwardableRealtimeEnvironment()), config['key'], None) is not None:
                        try:
                            existing_config = DeviceConfiguration.objects.get(
                                key=config['key'])
                            existing_config.device = device
                            existing_config.value = config['value']
                            existing_config.value = value_type = int(
                                config['value_type'])
                            existing_config.save()
                        except DeviceConfiguration.DoesNotExist:
                            device_configurations.append(
                                DeviceConfiguration(device=device, key=config['key'], value=config['value'], value_type=int(config['value_type'])))
                except ObjectDoesNotExist:
                    logger.error("Unknown device %s" % config['device_id'])
                except ValueError:
                    logger.error(
                        "ValueError value_type '%s' not an int" % config['value_type'])
        else:
            logger.error("Incomplete config data: %s" % config)

    Configuration.objects.bulk_create(configurations)
    DeviceConfiguration.objects.bulk_create(device_configurations)


def get_statistics_for_cogeneration_unit(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.CU):
            system_output = []
            system_output.append(('type', system.device_type))

            sensor = Sensor.objects.get(device=system, key='workload')
            sensor_values = SensorValue.objects.filter(sensor=sensor)
            if start is not None:
                sensor_values = sensor_values.filter(timestamp__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(timestamp__lte=end)

            hours_of_operation = sensor_values.filter(
                value__gt=0).count() * (120 / 3600.0)
            system_output.append(('hours_of_operation', hours_of_operation))

            thermal_efficiency = DeviceConfiguration.objects.get(
                device=system, key='thermal_efficiency')
            thermal_efficiency_value = parse_value(thermal_efficiency)
            electrical_efficiency = DeviceConfiguration.objects.get(
                device=system, key='electrical_efficiency')
            electrical_efficiency_value = parse_value(electrical_efficiency)
            max_gas_input = DeviceConfiguration.objects.get(
                device=system, key='max_gas_input')
            max_gas_input_value = parse_value(max_gas_input)

            total_thermal_production = 0
            total_electrical_production = 0
            total_gas_consumption = 0
            power_ons = 0

            values = list(sensor_values)
            system_output.append(('values_count', len(values)))

            last_time_on = None
            for value in values:
                step = (value.value / 100.0) * (120 / 3600.0)
                total_thermal_production += (
                    thermal_efficiency_value / 100.0) * step
                total_electrical_production += (
                    electrical_efficiency_value / 100.0) * step
                total_gas_consumption += max_gas_input_value * step

                if last_time_on is None:
                    last_time_on = value.value > 0

                if (last_time_on and value.value == 0) or (not last_time_on and value.value > 0):
                    power_ons += 1
                    last_time_on = not last_time_on

            system_output.append(
                ('total_thermal_production', total_thermal_production))
            system_output.append(
                ('total_electrical_production', total_electrical_production))
            system_output.append(
                ('total_gas_consumption', total_gas_consumption))
            system_output.append(('power_ons', power_ons))

            gas_costs = get_configuration('gas_costs')
            operating_costs = total_gas_consumption * gas_costs_value
            system_output.append(('operating_costs', operating_costs))

            output.append(('device_%s' % system.id, dict(system_output)))

    except (Device.DoesNotExist, DeviceConfiguration.DoesNotExist, Configuration.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_peak_load_boiler(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.PLB):
            system_output = []
            system_output.append(('type', system.device_type))

            sensor = Sensor.objects.get(device=system, key='workload')
            sensor_values = SensorValue.objects.filter(sensor=sensor)
            if start is not None:
                sensor_values = sensor_values.filter(timestamp__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(timestamp__lte=end)

            hours_of_operation = sensor_values.filter(
                value__gt=0).count() * (120 / 3600.0)
            system_output.append(('hours_of_operation', hours_of_operation))

            thermal_efficiency = DeviceConfiguration.objects.get(
                device=system, key='thermal_efficiency')
            thermal_efficiency_value = parse_value(thermal_efficiency)
            max_gas_input = DeviceConfiguration.objects.get(
                device=system, key='max_gas_input')
            max_gas_input_value = parse_value(max_gas_input)

            total_thermal_production = 0
            total_gas_consumption = 0
            power_ons = 0

            values = list(sensor_values)
            system_output.append(('values_count', len(values)))

            last_time_on = None
            for value in values:
                step = (value.value / 100.0) * (120 / 3600.0)
                total_thermal_production += (
                    thermal_efficiency_value / 100.0) * step
                total_gas_consumption += max_gas_input_value * step

                if last_time_on is None:
                    last_time_on = value.value > 0

                if (last_time_on and value.value == 0) or (not last_time_on and value.value > 0):
                    power_ons += 1
                    last_time_on = not last_time_on

            system_output.append(
                ('total_thermal_production', total_thermal_production))
            system_output.append(
                ('total_gas_consumption', total_gas_consumption))
            system_output.append(('power_ons', power_ons))

            gas_costs = Configuration.objects.get(key='gas_costs')
            gas_costs_value = parse_value(gas_costs)
            operating_costs = total_gas_consumption * gas_costs_value
            system_output.append(('operating_costs', operating_costs))

            output.append(('device_%s' % system.id, dict(system_output)))

    except (Device.DoesNotExist, DeviceConfiguration.DoesNotExist, Configuration.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_thermal_consumer(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.TC):
            system_output = []
            system_output.append(('type', system.device_type))

            sensor_values = SensorValue.objects.all()
            if start is not None:
                sensor_values = sensor_values.filter(timestamp__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(timestamp__lte=end)

            thermal_consumption = 0
            warmwater_consumption = 0

            sensor1 = Sensor.objects.get(
                device=system, key='get_consumption_power')
            for value in sensor_values.filter(sensor=sensor1):
                thermal_consumption += value.value * (120 / 3600.0)

            sensor2 = Sensor.objects.get(
                device=system, key='get_warmwater_consumption_power')
            for value in sensor_values.filter(sensor=sensor2):
                warmwater_consumption += value.value * (120 / 3600.0)

            system_output.append(('thermal_consumption', thermal_consumption))
            system_output.append(
                ('warmwater_consumption', warmwater_consumption))

            output.append(('device_%s' % system.id, dict(system_output)))

    except (Device.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_electrical_consumer(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.EC):
            system_output = []
            system_output.append(('type', system.device_type))

            sensor_values = SensorValue.objects.all()
            if start is not None:
                sensor_values = sensor_values.filter(timestamp__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(timestamp__lte=end)

            electrical_consumption = 0

            sensor1 = Sensor.objects.get(
                device=system, key='get_consumption_power')
            for value in sensor_values.filter(sensor=sensor1):
                electrical_consumption += value.value * (120 / 3600.0)

            system_output.append(
                ('electrical_consumption', electrical_consumption))

            output.append(('device_%s' % system.id, dict(system_output)))

    except (Device.DoesNotExist, Sensor.DoesNotExist, SensorValue.DoesNotExist) as e:
        logger.warning("DoesNotExist error: %s" % e)

    return output


def get_statistics_for_power_meter(start=None, end=None):
    output = []

    try:
        for system in Device.objects.filter(device_type=Device.PM):
            system_output = []
            system_output.append(('type', system.device_type))

            sensor_values = SensorValue.objects.all()
            if start is not None:
                sensor_values = sensor_values.filter(timestamp__gte=start)
            if end is not None:
                sensor_values = sensor_values.filter(timestamp__lte=end)

            total_purchased = 0
            total_fed_in_electricity = 0

            sensor1 = Sensor.objects.get(
                device=system, key='purchased')
            for value in sensor_values.filter(sensor=sensor1):
                total_purchased += value.value

            sensor2 = Sensor.objects.get(
                device=system, key='fed_in_electricity')
            for value in sensor_values.filter(sensor=sensor2):
                total_fed_in_electricity += value.value

            system_output.append(('total_purchased', total_purchased))
            system_output.append(
                ('total_fed_in_electricity', total_fed_in_electricity))

            output.append(('device_%s' % system.id, dict(system_output)))

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
        'time': SensorValue.objects.all().latest('timestamp').timestamp
    }
    last_month = get_last_month()

    for system in Device.objects.all():
        if system.device_type == Device.HS:
            output['hs_temperature'] = get_latest_value_with_unit(
                system, 'get_temperature')
        elif system.device_type == Device.PM:
            output['infeed_costs'] = get_latest_value_with_unit(system, 'purchased')
            output['infeed_reward'] = get_latest_value_with_unit(
                system, 'fed_in_electricity')
        elif system.device_type == Device.CU:
            output['cu_workload'] = get_latest_value_with_unit(system, 'workload')
            workload = get_latest_value(system, 'workload')
            thermal_production = round(workload * get_device_configuration(system, 'thermal_efficiency') / 100.0, 2)
            output['cu_thermal_production'] = '%s kWh' % thermal_production
            electrical_efficiency = round(workload * get_device_configuration(system, 'electrical_efficiency') / 100.0, 2)
            output['cu_electrical_production'] = '%s kWh' % electrical_efficiency
            output['cu_operating_costs'] = get_operating_costs(
                system, last_month)
        elif system.device_type == Device.PLB:
            output['plb_workload'] = get_latest_value_with_unit(system, 'workload')
            thermal_production = round(get_latest_value(system, 'workload') * get_device_configuration(system, 'thermal_efficiency') / 100.0, 2)
            output['plb_thermal_production'] = '%s kWh' % thermal_production
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

    return output


def get_latest_value(system, key):
    sensor = Sensor.objects.get(device=system, key=key)
    sensor_value = SensorValue.objects.filter(sensor=sensor).latest('timestamp')
    return sensor_value.value


def get_latest_value_with_unit(system, key):
    sensor = Sensor.objects.get(device=system, key=key)
    sensor_value = SensorValue.objects.filter(sensor=sensor).latest('timestamp')
    return '%s %s' % (round(sensor_value.value, 2), sensor.unit)


def get_configuration(key):
    return parse_value(Configuration.objects.get(key=key))


def get_device_configuration(system, key):
    return parse_value(DeviceConfiguration.objects.get(device=system, key=key))


def get_operating_costs(system, start):
    sensor = Sensor.objects.get(device=system, key='workload')
    max_gas_input = get_device_configuration(system, 'max_gas_input')
    total_gas_consumption = 0
    for value in SensorValue.objects.filter(sensor=sensor, timestamp__gte=start):
        step = (value.value / 100.0) * (120 / 3600.0)
        total_gas_consumption += max_gas_input * step
    return '%s Euro' % round(total_gas_consumption * get_configuration('gas_costs'), 2)


def get_last_month():
    try:
        latest_value = SensorValue.objects.latest('timestamp')
        return latest_value.timestamp + \
            dateutil.relativedelta.relativedelta(months=-1)
    except SensorValue.DoesNotExist:
        return None
