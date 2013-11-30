import json, urllib2
import logging
from datetime import datetime

from server.models import Device, Sensor, SensorEntry
from helpers import extract_data

logger = logging.getLogger('crawler')

# crawl data and save sensor entries
def crawl_and_save_data():
    try:
        # get all devices
        devices = Device.objects.all()
        for device in devices:
            # request data for device
            data = json.load(urllib2.urlopen(device.data_source))
            # remember the time of retrieval
            time = datetime.now()

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
        logger.error("URLError in crawl function: " + str(e.code))
    except urllib2.URLError, e:
        logger.error("URLError in crawl function: " + str(e.reason))
    except ValueError:
        logger.error("Crawl function did not receive a json")
    except:
        logger.error("Crawl function failed unexpectedly")