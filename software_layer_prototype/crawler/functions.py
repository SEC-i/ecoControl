import json, urllib2
from models import SensorEntry

# crawl data and save sensor data
def add_CHPUMockMeasurement():
	url = "http://172.16.22.235:5000/device/0/get"
	data = json.load(urllib2.urlopen(url))
	
	for sensor in [('electricalPower',1 ),('gasInput',2 ),('thermalPower', 3), ('workload', 4)]:
		sensor_entry =  SensorEntry()
		sensor_entry.sensor_id = sensor[1]
		sensor_entry.value = data['device'][sensor[0]]
		sensor_entry.save()
