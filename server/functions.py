import logging
from datetime import datetime
import dateutil.relativedelta

from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.utils.timezone import utc

from models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueHourly

from forecasting.helpers import parse_value


logger = logging.getLogger('django')
CACHE_TIMEOUT = 120  # seconds


def get_latest_value(system, key):
    sensor = Sensor.objects.get(device=system, key=key)
    sensor_value = SensorValue.objects.filter(
        sensor=sensor).latest('timestamp')
    return sensor_value.value


def get_latest_value_with_unit(system, key):
    sensor = Sensor.objects.get(device=system, key=key)
    sensor_value = SensorValue.objects.filter(
        sensor=sensor).latest('timestamp')
    return '%s %s' % (round(sensor_value.value, 2), sensor.unit)


def get_configuration(key):
    config = cache.get(key)
    if config is None:
        config = Configuration.objects.get(key=key)
        cache.set(key, config, CACHE_TIMEOUT)
    return parse_value(config)


def get_device_configuration(system, key):
    configs = cache.get(key + str(system.id))
    if configs is None:
        configs = DeviceConfiguration.objects.filter(device=system)
        cache.set(key + str(system.id), configs, CACHE_TIMEOUT)
    for config in configs:
        if config.key == key:
            return parse_value(config)


def get_device_configuration(system, key):
    return parse_value(DeviceConfiguration.objects.get(device=system, key=key))


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
    if use_view:
        _class = SensorValueHourly
    else:
        _class = SensorValue

    try:
        latest_value = _class.objects.latest('timestamp')
        return latest_value.timestamp + \
            dateutil.relativedelta.relativedelta(
                years=-years, months=-months, days=-days)
    except _class.DoesNotExist:
        return datetime.now().replace(tzinfo=utc) + \
            dateutil.relativedelta.relativedelta(
                years=-years, months=-months, days=-days)
