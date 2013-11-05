import datetime, time
from flask import Flask
from flask_peewee.auth import Auth
from flask_peewee.db import Database
from peewee import *
import json, urllib2

DATABASE = {
    'engine': 'peewee.PostgresqlDatabase',
    'name': "protodb",
    'user': "bp2013h1",
    'password': "hirsch",
    'host': "172.16.22.247",
    'port': "5432",
}

DEBUG = True
SECRET_KEY = 'bp2013h1'

app = Flask(__name__)
app.config.from_object(__name__)

db = Database(app)


class Measurement(db.Model):
	mid = PrimaryKeyField()
	sensor_id = IntegerField()
	status = BooleanField()
	temperature = DecimalField()
	electrical_power = DecimalField()
	timestamp = DateTimeField(default=datetime.datetime.now)


def addMeasurement():
	url = "http://172.16.19.114/api/sensor/"
	data = json.load(urllib2.urlopen(url))

	sensor_data = Measurement()
	sensor_data.sensor_id = data['sensor_id']
	sensor_data.status = data['status']
	sensor_data.temperature = data['temperature']
	sensor_data.electrical_power = data['electrical_power']
	sensor_data.save()


# create an Auth object for use with our flask app and database wrapper
auth = Auth(app, db)

if __name__ == '__main__':
    # auth.User.create_table(fail_silently=True)
    # Measurement.create_table(fail_silently=True)
    while(True):
    	addMeasurement()
    	time.sleep(1)

    #app.run(host="0.0.0.0", port=5000, debug=True)