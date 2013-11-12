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
	name = CharField()
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

def add_mockup():
	device = Device()
	device.name = "BHK"
	device.save()
	device.update()
	
	for info in [("thermal power", "Watt"),("electrical power","Watt"),("workload","%"),("supply temperature", "Grad"),("return temperature", "Grad")]: # gas input?
		sensor1 = Sensor()
		sensor1.device_id = device.id
		sensor1.name = info[0]
		sensor1.unit = info[1]
		sensor1.save()
		sensor1.update()
		for k in range(10):
			add_mockupEntry(sensor1.id)
	
	actuator = Actuator()
	print actuator
	actuator.device_id = device.id
	actuator.name = "Switch1"
	actuator.type = "Switch" #eg "switch"
	actuator.command = "" # temporary
	actuator.save()


def add_mockupEntry(sens_id):
	entry = SensorEntry()
	entry.sensor_id = sens_id
	entry.value = str(random.uniform(1,50))
	entry.save()
	


	

	
