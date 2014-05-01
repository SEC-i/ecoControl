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


def get_operating_costs(system):
    last_month = get_last_month()

    sensor = Sensor.objects.get(device=system, key='workload')
    max_gas_input = DeviceConfiguration.objects.get(
        device=system, key='max_gas_input')
    max_gas_input_value = parse_value(max_gas_input)

    total_gas_consumption = 0
    for value in SensorValue.objects.filter(sensor=sensor, timestamp__gte=last_month):
        total_gas_consumption += max_gas_input_value * (value.value / 100.0)

    gas_costs = Configuration.objects.get(key='gas_costs')
    gas_costs_value = parse_value(gas_costs)

    return ('device_%s' % system.id, total_gas_consumption * gas_costs_value)

def get_consumption(system):
    last_month = get_last_month()

    if system.device_type == Device.TC:
        total_thermal_consumption = total_warmwater_consumption = 0

        sensor1 = Sensor.objects.get(device=system, key='get_consumption_power')
        for value in SensorValue.objects.filter(sensor=sensor1, timestamp__gte=last_month):
            total_thermal_consumption += value.value

        sensor2 = Sensor.objects.get(device=system, key='get_warmwater_consumption_power')
        for value in SensorValue.objects.filter(sensor=sensor2, timestamp__gte=last_month):
            total_warmwater_consumption += value.value

        return ('device_%s' % system.id, total_thermal_consumption, total_warmwater_consumption)
    elif system.device_type == Device.EC:
        sensor = Sensor.objects.get(device=system, key='get_consumption_power')

        total_electrical_consumption = 0
        for value in SensorValue.objects.filter(sensor=sensor, timestamp__gte=last_month):
            total_electrical_consumption += value.value

        return ('device_%s' % system.id, total_electrical_consumption)
        
    return None

def get_last_month():
    latest_value = SensorValue.objects.latest('timestamp')
    return latest_value.timestamp + \
        dateutil.relativedelta.relativedelta(months=-1)

    
