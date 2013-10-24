from flask import Flask, request, jsonify, make_response
from functools import update_wrapper
import os, json, time
import wiringpi2
import django
wiringpi2.wiringPiSetup

app = Flask(__name__)

version = "0.2"

def crossdomain(origin=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/api/', methods = ['GET'])
@crossdomain(origin='*')
def showVersion():
    return jsonify( { 'version': version } )

@app.route('/api/login/', methods = ['POST'])
@crossdomain(origin='*')
def login():
	if request.method == 'POST':
		if 'password' in request.form and request.form['password'] == "Hirsch":
			return "s3cr3t"
        return ""

@app.route('/api/switches/', methods = ['GET', 'POST'])
@crossdomain(origin='*')
def controlSwitches():
	if request.method == 'GET':
		return "api key needed"
	if request.method == 'POST':
		if 'api_key' in request.form and request.form['api_key']=="s3cr3t":
			if 'switch_number' in request.form:
				try:
					switch_number = request.form['switch_number']
					if int(switch_number) in range(1,5):
						if 'switch_state' in request.form:
							if request.form['switch_state'] == "on":
								os.system("sudo sispmctl -q -o " + switch_number)
							else:
								os.system("sudo sispmctl -q -f " + switch_number)
						else:
							os.system("sudo sispmctl -q -t " + switch_number)
					return "true"
				except ValueError:
					return "false"
			else:
				currentStates = os.popen("sudo sispmctl -q -n -g all").readlines()
				return jsonify({(i+1): currentStates[i][0]=="1" for i in range(0,4)})
		else:
			return "0"

@app.route('/api/temp/', methods = ['GET'])
@crossdomain(origin='*')
def showTemperature():
	cpuValue = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
	cpuTemperature = str(round((float(cpuValue) / 1000), 1)) +"'C"
	gpuValue = os.popen("/opt/vc/bin/vcgencmd measure_temp").readline()
	gpuTemperature = gpuValue[5:-1]

	return jsonify( {
		'cpu_temperature': cpuTemperature,
		'gpu_temperature': gpuTemperature } )

@app.route('/api/uptime/', methods = ['GET'])
@crossdomain(origin='*')
def showUptime():
	uptimeValue = os.popen("/usr/bin/uptime").readline().split(",")
	timeData = uptimeValue[0][1:9]
	uptimeData = uptimeValue[0][13:] + "," + uptimeValue[1]
	userData = uptimeValue[2][2:-5]
	loadData = uptimeValue[3][16:] + uptimeValue[4] + uptimeValue[5][:-1]
	return jsonify( {
		'time': timeData,
		'uptime': uptimeData,
		'active_user': userData,
		'load': loadData } )

@app.route('/api/network/', methods = ['GET'])
@crossdomain(origin='*')
def showNetwork():
	hwaddValue = os.popen("/sbin/ifconfig eth0 | /bin/grep HWadd").readline().split()
	inetValue = os.popen("/sbin/ifconfig eth0 | /bin/grep inet").readline().split()
	return jsonify( {
		'name': hwaddValue[0],
		'mac': hwaddValue[4],
		'ip': inetValue[1][5:],
		'mask': inetValue[3][5:] } )

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

