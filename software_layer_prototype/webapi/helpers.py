from flask import make_response
from functools import update_wrapper
import calendar

# CORS decorator
def crossdomain(origin=None):
	def decorator(f):
		def wrapped_function(*args, **kwargs):
			resp = make_response(f(*args, **kwargs))
			h = resp.headers
			h['Access-Control-Allow-Origin'] = origin
			return resp
		return update_wrapper(wrapped_function, f)
	return decorator

# converts SelectQuery to jsonify-able list
def convert_sql_to_list(sensor_entries, sensor_unit):
	return [{
		"value": str(item.value)+" "+sensor_unit,
		"timestamp": str(item.timestamp) #calendar.timegm(item.timestamp.utctimetuple()) 
		} for item in sensor_entries]

def convert_sensor_sql_to_list(sensor_entries):
	return [{
		"name": item.name,
		"unit":item.unit
		} for item in sensor_entries]
