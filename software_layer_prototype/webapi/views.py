import datetime
from flask import jsonify
from webapi import app
from webapi.helpers import crossdomain, convert_sql_to_list
from models import Measurement

# display last 10 measurements by default
@app.route('/api/measurements/', methods = ['GET'])
@crossdomain(origin='*')
def showRecentMeasurements():
	#measurements = Measurement.select().order_by(Measurement.mid.desc()).limit(10)
	#return jsonify(results=convert_sql_to_list(measurements))

# dynamic limit
@app.route('/api/measurements/<limit>/', methods = ['GET'])
@crossdomain(origin='*')
def showRecentMeasurementsLimit(limit):
	#measurements = Measurement.select().order_by(Measurement.mid.desc()).limit(limit)
	#return jsonify(results=convert_sql_to_list(measurements))

# dynamic offset and limit
@app.route('/api/measurements/<offset>/<limit>/', methods = ['GET'])
@crossdomain(origin='*')
def showRecentMeasurementsOffsetLimit(limit, offset):
	#measurements = Measurement.select().order_by(Measurement.mid.desc()).offset(offset).limit(limit)
	#return jsonify(results=convert_sql_to_list(measurements))

@app.route('/api/control/', methods = ['POST'])
@crossdomain(origin='*')
def controlSwitch():
	if 'id' in request.form and 'status' in request.form:
		# post to bhk with 'id'
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
