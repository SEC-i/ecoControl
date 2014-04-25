import logging

from django.core.exceptions import ObjectDoesNotExist

from models import Device, DeviceConfiguration

logger = logging.getLogger('django')


def parse_configurations(data):
    configurations = []
    if 'config' in data:
        for config_data in data['config']:
            for (device_name, key, value, value_type) in config_data:
                try:
                    device = Device.objects.get(name=device_name)
                    configurations.append(
                        DeviceConfiguration(device=device, key=key, value=value, value_type=int(value_type)))
                except ObjectDoesNotExist:
                    logger.error("Unknown device %s" % device_name)
                except ValueError:
                    logger.error("ValueError value_type '%s' not an int" % value_type)

    return configurations
