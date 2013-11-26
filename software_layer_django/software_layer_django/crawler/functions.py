import json, urllib2
import logging
from datetime import datetime

from software_layer_django.models import Device, Sensor, SensorEntry

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
				# sensor.name needs to be present in data
				if sensor.name in data:
					sensor_entry = SensorEntry()
					sensor_entry.sensor_id = sensor.id
					sensor_entry.value = data[sensor.name]
					sensor_entry.timestamp = time
					sensor_entry.save()
	except:
		logger.error("Crawl function failed")
