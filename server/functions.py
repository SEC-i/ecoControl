import logging

from django.core.exceptions import ObjectDoesNotExist

from models import Device, DeviceConfiguration

from forecasting.environment import ForwardableRealtimeEnvironment
from forecasting.systems.code import CodeExecuter
from forecasting.systems.producers import CogenerationUnit, PeakLoadBoiler
from forecasting.systems.storages import HeatStorage, PowerMeter
from forecasting.systems.consumers import ThermalConsumer, ElectricalConsumer

logger = logging.getLogger('django')


def parse_configurations(data):
    configurations = []
    if 'config' in data:
        for device_id, key, value, value_type in data['config']:
            try:
                device = Device.objects.get(id=device_id)
                for device_type, class_name in Device.DEVICE_TYPES:
                    if device.device_type == device_type:
                        system_class = globals()[class_name]
                # Make sure that key is present in corresponding system class
                if getattr(system_class(ForwardableRealtimeEnvironment()), key, None) is not None:
                    configurations.append(
                        DeviceConfiguration(device=device, key=key, value=value, value_type=int(value_type)))
            except ObjectDoesNotExist:
                logger.error("Unknown device %s" % device_id)
            except ValueError:
                logger.error("ValueError value_type '%s' not an int" % value_type)

    return configurations
