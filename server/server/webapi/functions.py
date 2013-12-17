import json
import logging
from datetime import datetime

from django.utils.timezone import utc

from server.models import Sensor, SensorEntry
from helpers import extract_data

logger = logging.getLogger('webapi')

def save_device_data(device, data):
    try:
        # get device's sensors
        sensors = Sensor.objects.filter(device = device)

        # parse data for device
        data = json.loads(data)

        logger.debug("Saving data for device #" + str(device.id))

        # remember the time of retrieval
        time = datetime.now().replace(tzinfo=utc)

        new_entries = []
        for sensor in sensors:
            try:
                latest_entry = SensorEntry.objects.filter(sensor = sensor).latest('timestamp')
                time_diff = time-latest_entry.timestamp
                if time_diff.total_seconds() > device.interval:
                    new_entries.append(new_sensor_entry(sensor, data, time))
                else:
                    logger.debug("Data skipped")
            except SensorEntry.DoesNotExist:
                logger.debug("No previous SensorEntry found")
                new_entries.append(new_sensor_entry(sensor, data, time))

        SensorEntry.objects.bulk_create(new_entries)
        return True

    except ValueError:
        logger.error("Function did not receive a json")
        return False

def new_sensor_entry(sensor, data, time):
    # sensor.key_name needs to be present in data
    try:
        value = extract_data(data, sensor.key_name)
        # create new sensor entries
        return SensorEntry(sensor = sensor, value = value, timestamp = time )

    except KeyError:
        logger.debug(sensor.key_name + " not found")

def dispatch_device_request(device, data):
    plugin_name = device.name.lower()
    try:
        logger.debug("Trying to load 'plugins." + plugin_name + "'")
        plugin = __import__('plugins.' + plugin_name, globals(), locals(), ['handle_post_data'], -1)
    except ImportError:
        plugin = __import__('plugins.default', globals(), locals(), ['handle_post_data'], -1)

    plugin.handle_post_data(data)
