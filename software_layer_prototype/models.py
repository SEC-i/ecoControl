import datetime
from peewee import *
from webapi.app import db
import random

class Device(db.Model):
	id = PrimaryKeyField()
	name = CharField()

class Sensor(db.Model):
	id = PrimaryKeyField()
	device_id = ForeignKeyField(Device, related_name='sensors', db_column='device_id')
	name = CharField() # the name the software layer is using and the frontend knows
	name_original = CharField() # the name the device is using
	unit = CharField()

class SensorEntry(db.Model):
	id = PrimaryKeyField()
	sensor_id = ForeignKeyField(Sensor, related_name='entries', db_column='sensor_id')
	value = CharField()
	timestamp = DateTimeField(default=datetime.datetime.now)

class Actuator(db.Model):
	id = PrimaryKeyField()
	device_id = ForeignKeyField(Device, related_name='actuators', db_column='device_id')
	name = CharField()
	type = CharField() #eg "switch"
	command = TextField() # temporary

def create_tables():
	Device.create_table(fail_silently=True)
	Sensor.create_table(fail_silently=True)
	SensorEntry.create_table(fail_silently=True)
	Actuator.create_table(fail_silently=True)

def drop_tables():
	SensorEntry.drop_table(fail_silently=True)
	Sensor.drop_table(fail_silently=True)
	Actuator.drop_table(fail_silently=True)
	Device.drop_table(fail_silently=True)

def add_CHPUMock():
	device = Device()
	device.name = "BHKW0"
	device.save()
	device.update()
	
	for info in [("electrical power","electricalPower", "kW"),("gas input", "gasInput", "kW"),("thermal power", "thermalPower" ,"kW"),("workload", "workload","%")]:
		sensor1 = Sensor()
		sensor1.device_id = device.id
		sensor1.name = info[0]
		sensor1.name_original = info[1]
		sensor1.unit = info[2]
		sensor1.save()
		sensor1.update()
	
	actuator = Actuator()
	actuator.device_id = device.id
	actuator.name = "workload control"
	actuator.type = "scroll bar" #eg "switch"
	actuator.command = "" # temporary
	actuator.save()

	


	

	
