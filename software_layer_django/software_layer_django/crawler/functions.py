import json, urllib2
from software_layer_django.webapi.models import SensorEntry

# crawl data and save sensor data
def add_SensorEntry():
	url = "http://localhost:9000/device/0/get"
	data = json.load(urllib2.urlopen(url))
    
	sensor_entry = SensorEntry()
	sensor_entry.sensor_id = 1
	sensor_entry.value = data['device']['electricalPower']
	sensor_entry.save()
    
	sensor_entry = SensorEntry()
	sensor_entry.sensor_id = 2
	sensor_entry.value = data['device']['thermalPower']
	sensor_entry.save()
    
	sensor_entry = SensorEntry()
	sensor_entry.sensor_id = 3
	sensor_entry.value = data['device']['gasInput']
	sensor_entry.save()

	sensor_entry = SensorEntry()
	sensor_entry.sensor_id = 4
	sensor_entry.value = data['device']['workload']
	sensor_entry.save()
