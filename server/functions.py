import logging

from django.core.exceptions import ObjectDoesNotExist

from models import Device, Configuration, DeviceConfiguration

from forecasting.environment import ForwardableRealtimeEnvironment
from forecasting.systems.code import CodeExecuter
from forecasting.systems.producers import CogenerationUnit, PeakLoadBoiler
from forecasting.systems.storages import HeatStorage, PowerMeter
from forecasting.systems.consumers import ThermalConsumer, ElectricalConsumer

logger = logging.getLogger('django')


def perform_configuration(data):
    configurations = []
    device_configurations = []
    for config in data:
        if all(x in config for x in ['device_id', 'key', 'value', 'value_type']):
            if config['device_id'] == '0':
                try:
                    existing_config = Configuration.objects.get(key=config['key'])
                    existing_config.value = config['value']
                    existing_config.value = value_type=int(config['value_type'])
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
                            existing_config = DeviceConfiguration.objects.get(key=config['key'])
                            existing_config.device = device
                            existing_config.value = config['value']
                            existing_config.value = value_type=int(config['value_type'])
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
