import datetime
from flask import jsonify
from flask import Flask
from webapi.app import app
from webapi.helpers import crossdomain, convert_sql_to_list, convert_sensor_sql_to_list
from models import Sensor, SensorEntry, Device

@app.route('/api/measurements/device/<device_id>/', methods = ['GET']) # later id and name of device given?
@crossdomain(origin='*')
def showRecentMeasurements(device_id):
	sensors = Sensor.select().join(Device).where(Device.id == device_id)
	result = []
	for sens in sensors:
		sensor_dict = {sens.name: convert_sql_to_list(sens.entries.limit(10), sens.unit)}
		result.append(sensor_dict)
	return jsonify(results = result)

@app.route('/api/measurements/device/<device_id>/<limit>/', methods = ['GET']) # later id and name of device given?
@crossdomain(origin='*')
def showRecentMeasurementsLimit(device_id, limit):
	sensors = Sensor.select().join(Device).where(Device.id == device_id)
	result = []
	for sens in sensors:
		sensor_dict = {sens.name: convert_sql_to_list(sens.entries.limit(limit), sens.unit)}
		result.append(sensor_dict)
	return jsonify(results = result)

@app.route('/api/measurements/device/<device_id>/<from_timestamp>/<to_timestamp>/', methods = ['GET']) # timestamp format ???
@crossdomain(origin='*')
def showMeasurementsBetweenTimestamps(device_id, from_timestamp, to_timestamp):
	sensors = Sensor.select().join(Device).where(Device.id == device_id)
	result = []
	for sens in sensors:
		entries_between_timestamps = sens.entries.where(from_timestamp<=SensorEntry.timestamp<to_timestamp)
		sensor_dict = {sens.name: convert_sql_to_list(entries_between_timestamps, sens.unit)}
		result.append(sensor_dict)
	return jsonify(results = result)

@app.route('/api/measurements/device/<device_id>/sensor/<sensor_id>/<limit>/', methods = ['GET'])
@crossdomain(origin='*')
def showMeasurementsForSensor(device_id, sensor_id, limit):
	sensor = Sensor.select().where(Sensor.id == sensor_id).join(Device)
	result = []
	for sens in sensor:
		entries = sens.entries.limit(limit)
		sensor_dict = {sens.name: convert_sql_to_list(entries, sens.unit)}
		result.append(sensor_dict)
	return jsonify(results = result)
	

@app.route('/api/measurements/device/<device_id>/sensor/<sensor_id>/<from_timestamp>/<to_timestamp>/', methods = ['GET'])
@crossdomain(origin='*')
def showMeasurementsForSensorBetweenTimestamps(device_id, sensor_id, from_timestamp, to_timestamp):
	sensor = Sensor.select().where(Sensor.id == sensor_id).join(Device)
	result = []
	for sens in sensor:
		entries_between_timestamps = sens.entries.where(from_timestamp<=SensorEntry.timestamp<to_timestamp)
		sensor_dict = {sens.name: convert_sql_to_list(entries_between_timestamps, sens.unit)}
		result.append(sensor_dict)
	return jsonify(results = result)


@app.route('/api/control/device/<device_id>/actuator/<actuator_id>', methods = ['POST'])
@crossdomain(origin='*')
def controlSwitch():
	if 'id' in request.form and 'status' in request.form:
		# post to bhk with 'id'
		return "1"
	else:
		return "0"


@app.route('/api/settings/', methods = ['POST'])
@crossdomain(origin='*')
def setSettings():
	if 'crawler_frequency' in request.form:
		try:
			# int(request.form['crawler_frequency'])
			return "1"
		except:
			return "0"
	return "0"
