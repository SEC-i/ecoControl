import json, urllib2
import logging
from datetime import datetime
from threading import Timer

from django.utils.timezone import utc

from server.models import Device, Sensor, SensorEntry
from helpers import extract_data

logger = logging.getLogger('crawler')

def start_crawling():
    devices = Device.objects.all()
    for device in devices:
        crawl_and_save_data(device)

# crawl data and save sensor entries
def crawl_and_save_data(device):
    # Schedule timer to execute crawl_and_save_data again
    Timer(device.interval, crawl_and_save_data, args=(device,)).start()
    try:
        # request data for device
        data = json.load(urllib2.urlopen(device.data_source))

        logger.debug("Crawling data from " + device.data_source)

        # remember the time of retrieval
        time = datetime.now().replace(tzinfo=utc)

        # get device's sensors
        sensors = Sensor.objects.all().filter(device_id = device.id)

        for sensor in sensors:
            # sensor.key_name needs to be present in data
            try:
                value = extract_data(data, sensor.key_name)

                sensor_entry = SensorEntry()
                sensor_entry.sensor_id = sensor.id
                sensor_entry.value = value
                sensor_entry.timestamp = time
                sensor_entry.save()
            except KeyError:
                logger.debug(sensor.key_name + "not found")
    except urllib2.HTTPError, e:
        logger.error("HTTPError in crawl function: " + str(e.code))
    except urllib2.URLError, e:
        logger.error("URLError in crawl function: " + str(e.reason))
    except ValueError:
        logger.error("Crawl function did not receive a json")



