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


def get_statistics_for_cogeneration_unit(start):
    output = []
    for system in Device.objects.filter(device_type=Device.CU):
        system_output = []
        system_output.append(('type', system.device_type))

        sensor = Sensor.objects.get(device=system, key='workload')

        hours_of_operation = SensorValue.objects.filter(sensor=sensor, timestamp__gte=start, value__gt=0).count() * (120 / 3600.0)
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

        values = list(SensorValue.objects.filter(
            sensor=sensor, timestamp__gte=start))
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

        system_output.append(('total_thermal_production', total_thermal_production))
        system_output.append(('total_electrical_production', total_electrical_production))
        system_output.append(('total_gas_consumption', total_gas_consumption))
        system_output.append(('power_ons', power_ons))

        gas_costs = Configuration.objects.get(key='gas_costs')
        gas_costs_value = parse_value(gas_costs)
        operating_costs = total_gas_consumption * gas_costs_value
        system_output.append(('operating_costs', operating_costs))

        output.append(('device_%s' % system.id, dict(system_output)))

    return output


def get_statistics_for_peak_load_boiler(start):
    output = []
    for system in Device.objects.filter(device_type=Device.PLB):
        system_output = []
        system_output.append(('type', system.device_type))

        sensor = Sensor.objects.get(device=system, key='workload')
        hours_of_operation = SensorValue.objects.filter(sensor=sensor, timestamp__gte=start, value__gt=0).count() * (120 / 3600.0)
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

        values = list(SensorValue.objects.filter(
            sensor=sensor, timestamp__gte=start))
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

        system_output.append(('total_thermal_production', total_thermal_production))
        system_output.append(('total_gas_consumption', total_gas_consumption))
        system_output.append(('power_ons', power_ons))

        gas_costs = Configuration.objects.get(key='gas_costs')
        gas_costs_value = parse_value(gas_costs)
        operating_costs = total_gas_consumption * gas_costs_value
        system_output.append(('operating_costs', operating_costs))

        output.append(('device_%s' % system.id, dict(system_output)))

    return output


def get_statistics_for_thermal_consumer(start):
    output = []
    for system in Device.objects.filter(device_type=Device.TC):
        system_output = []
        system_output.append(('type', system.device_type))

        thermal_consumption = 0
        warmwater_consumption = 0

        sensor1 = Sensor.objects.get(
            device=system, key='get_consumption_power')
        for value in SensorValue.objects.filter(sensor=sensor1, timestamp__gte=start):
            thermal_consumption += value.value * (120 / 3600.0)

        sensor2 = Sensor.objects.get(
            device=system, key='get_warmwater_consumption_power')
        for value in SensorValue.objects.filter(sensor=sensor2, timestamp__gte=start):
            warmwater_consumption += value.value * (120 / 3600.0)

        system_output.append(('thermal_consumption', thermal_consumption))
        system_output.append(('warmwater_consumption', warmwater_consumption))

        output.append(('device_%s' % system.id, dict(system_output)))

    return output


def get_statistics_for_electrical_consumer(start):
    output = []
    for system in Device.objects.filter(device_type=Device.EC):
        system_output = []
        system_output.append(('type', system.device_type))

        electrical_consumption = 0

        sensor1 = Sensor.objects.get(
            device=system, key='get_consumption_power')
        for value in SensorValue.objects.filter(sensor=sensor1, timestamp__gte=start):
            electrical_consumption += value.value * (120 / 3600.0)

        system_output.append(('electrical_consumption', electrical_consumption))

        output.append(('device_%s' % system.id, dict(system_output)))

    return output


def get_statistics_for_power_meter(start):
    output = []
    for system in Device.objects.filter(device_type=Device.PM):
        system_output = []
        system_output.append(('type', system.device_type))

        total_purchased = 0
        total_fed_in_electricity = 0

        sensor1 = Sensor.objects.get(
            device=system, key='purchased')
        for value in SensorValue.objects.filter(sensor=sensor1, timestamp__gte=start):
            total_purchased += value.value

        sensor2 = Sensor.objects.get(
            device=system, key='fed_in_electricity')
        for value in SensorValue.objects.filter(sensor=sensor2, timestamp__gte=start):
            total_fed_in_electricity += value.value

        system_output.append(('total_purchased', total_purchased))
        system_output.append(('total_fed_in_electricity', total_fed_in_electricity))
        
        output.append(('device_%s' % system.id, dict(system_output)))

    return output


def get_last_month():
    latest_value = SensorValue.objects.latest('timestamp')
    return latest_value.timestamp + \
        dateutil.relativedelta.relativedelta(months=-1)
