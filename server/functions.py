import logging
from datetime import datetime
import dateutil.relativedelta

from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.timezone import utc

from models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueDaily


logger = logging.getLogger('django')
CACHE_TIMEOUT = 120  # seconds


def get_latest_value(device, key):
    sensor = Sensor.objects.get(device=device, key=key)
    sensor_value = SensorValue.objects.filter(
        sensor=sensor).latest('timestamp')
    return sensor_value.value


def get_latest_value_with_unit(device, key):
    sensor = Sensor.objects.get(device=device, key=key)
    sensor_value = SensorValue.objects.filter(
        sensor=sensor).latest('timestamp')
    return '%s %s' % (round(sensor_value.value, 2), sensor.unit)


def get_configuration(key, cached=True):
    config = cache.get(key)
    if config is None or not cached:
        config = Configuration.objects.get(key=key)
        cache.set(key, config, CACHE_TIMEOUT)
    return parse_value(config)


def get_device_configuration(device, key):
    configs = cache.get(key + str(device.id))
    if configs is None:
        configs = DeviceConfiguration.objects.filter(device=device)
        cache.set(key + str(device.id), configs, CACHE_TIMEOUT)
    for config in configs:
        if config.key == key:
            return parse_value(config)




def get_configurations():
    configurations = {}
    for config in Configuration.objects.filter(internal=False):
        configurations[config.key] = {
            'value': config.value,
            'type': config.value_type,
            'unit': config.unit
        }
    return [(0, configurations)]


def get_device_configurations(tunable=None):
    output = []
    for device in Device.objects.all():
        configurations = {}
        configuration_queryset = DeviceConfiguration.objects.filter(
            device=device)
        if tunable is not None:
            configuration_queryset = configuration_queryset.filter(
                tunable=tunable)

        for config in configuration_queryset:
            configurations[config.key] = {
                'device': config.device.name,
                'value': config.value,
                'type': config.value_type,
                'unit': config.unit
            }
        if len(configurations) > 0:
            output += [(device.id, configurations)]

    return output


def get_past_time(years=0, months=0, days=0, use_view=False):
    output_time = datetime.now().replace(tzinfo=utc)

    if use_view:
        _class = SensorValueDaily
    else:
        _class = SensorValue

    try:
        output_time = _class.objects.latest('timestamp').timestamp
    except _class.DoesNotExist:
        pass

    return output_time + dateutil.relativedelta.relativedelta(years=-years, months=-months, days=-days)


def parse_value(config):
    try:
        if config.value_type == DeviceConfiguration.STR:
            return str(config.value)
        elif config.value_type == DeviceConfiguration.INT:
            return int(config.value)
        elif config.value_type == DeviceConfiguration.FLOAT:
            return float(config.value)
        elif config.value_type == DeviceConfiguration.BOOL:
            return config.value == "True"
        else:
            logger.warning(
                "Couldn't determine type of %s (%s)" % (config.value, config.value_type))
    except ValueError:
        logger.warning("ValueError parsing %s to %s" %
                       (config.value, config.value_type))
    return str(config.value)
