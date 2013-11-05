import datetime
from flask import Flask, jsonify, make_response
from functools import update_wrapper
from peewee import *
from flask_peewee.db import Database
from flask_peewee.auth import Auth
from flask_peewee.rest import RestAPI
import json

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

def crossdomain(origin=None):
	def decorator(f):
		def wrapped_function(*args, **kwargs):
			resp = make_response(f(*args, **kwargs))
			h = resp.headers
			h['Access-Control-Allow-Origin'] = origin
			return resp
		return update_wrapper(wrapped_function, f)
	return decorator

def convertSQLtoList(measurements):
	return [{
		"sensor_id": item.sensor_id,
		"status": item.status,
		"temperature": float(item.temperature),
		"electrical_power": float(item.electrical_power),
		"timestamp": str(item.timestamp)
		} for item in measurements]

@app.route('/api/measurements/', methods = ['GET'])
@crossdomain(origin='*')
def showRecentMeasurements():
	measurements = Measurement.select().order_by(Measurement.mid.desc()).limit(10)
	return jsonify(results=convertSQLtoList(measurements))

@app.route('/api/measurements/<limit>/', methods = ['GET'])
@crossdomain(origin='*')
def showRecentMeasurementsLimit(limit):
	measurements = Measurement.select().order_by(Measurement.mid.desc()).limit(limit)
	return jsonify(results=convertSQLtoList(measurements))

@app.route('/api/measurements/<offset>/<limit>/', methods = ['GET'])
def showRecentMeasurementsOffsetLimit(limit, offset):
	measurements = Measurement.select().order_by(Measurement.mid.desc()).offset(offset).limit(limit)
	return jsonify(results=convertSQLtoList(measurements))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)