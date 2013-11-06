from flask import make_response
from functools import update_wrapper
import calendar
import os

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

# checks if pid belongs to a running process
def pid_is_running(pid):
    try:
        os.kill(pid, 0)

    except OSError:
        return

    else:
        return pid

# writes pid to pidfile but returns false if pidfile belongs to running process
def write_pidfile_or_fail(path_to_pidfile):
    if os.path.exists(path_to_pidfile):
        pid = int(open(path_to_pidfile).read())

        if pid_is_running(pid):
            # print("Sorry, found a pidfile!  Process {0} is still running.".format(pid))
            return False

        else:
            os.remove(path_to_pidfile)

    open(path_to_pidfile, 'w').write(str(os.getpid()))
    return path_to_pidfile