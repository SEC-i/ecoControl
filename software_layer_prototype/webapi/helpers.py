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
def convert_sql_to_list(measurements):
	return [{
		"sensor_id": item.sensor_id,
		"status": item.status,
		"temperature": float(item.temperature),
		"electrical_power": float(item.electrical_power),
		"timestamp": calendar.timegm(item.timestamp.utctimetuple())
		} for item in measurements]