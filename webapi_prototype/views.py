import datetime
from flask import jsonify
from app import app
from helpers import *
from models import Measurement

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