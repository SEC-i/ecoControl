from flask import make_response
from functools import update_wrapper

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