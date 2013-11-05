import datetime
from peewee import *
from app import db

class Measurement(db.Model):
	mid = PrimaryKeyField()
	sensor_id = IntegerField()
	status = BooleanField()
	temperature = DecimalField()
	electrical_power = DecimalField()
	timestamp = DateTimeField(default=datetime.datetime.now)