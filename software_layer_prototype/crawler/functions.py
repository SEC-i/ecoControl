import json, urllib2
from models import SensorEntry, Sensor, Device

# crawl data and save sensor data CHPU has the id 0
def add_CHPUMockMeasurement():
	surl = "http://172.16.22.235:5000/device/0/get"
	data = json.load(urllib2.urlopen(surl))
	chpu_sensors = Sensor.select().join(Device).where(Device.id == 1)
	sensor_identifications = []
	for sensor in chpu_sensors:
		sensor_identifications.append({'name': sensor.name_original, 'id': sensor.id})

	for sensor in sensor_identifications:
		sensor_entry =  SensorEntry()
		sensor_entry.sensor_id = sensor['id']
		sensor_entry.value = data['device'][sensor['name']]
		sensor_entry.save()
	

