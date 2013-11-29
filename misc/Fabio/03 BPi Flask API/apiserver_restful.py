from flask import Flask, request
from flask.ext import restful
import os
import wiringpi2
wiringpi2.wiringPiSetup

app = Flask(__name__)

api = restful.Api(app)

version = "0.1"

class main(restful.Resource):
    def get(self):
        return ""

class apiVersion(restful.Resource):
    def get(self):
        return {'version': version}

class apiLogin(restful.Resource):
    def post(self):
    	if 'password' in request.form and request.form['password'] == "Hirsch":
			return "s3cr3t", 200, {'Access-Control-Allow-Origin': '*'}
        return "", 200, {'Access-Control-Allow-Origin': '*'}

class remoteSwitch(restful.Resource):
    def get(self):
    	states = []
    	for line in os.popen("sudo sispmctl -q -n -g all").readlines():
    		states.append(line[0]=="1")
        return states, 200, {'Access-Control-Allow-Origin': '*'}
    def post(self):
    	if 'api_key' in request.form and request.form['api_key'] == "s3cr3t":
	    	if 'switch_number' in request.form:
		    	try:
		    		switch_number = request.form['switch_number']
		    		if int(switch_number) in range(1,5):
		    			if 'switch_state' in request.form:
			    			if request.form['switch_state'] == "on":
			    				os.system("sudo sispmctl -o " + switch_number)
			    			else:
			    				os.system("sudo sispmctl -f " + switch_number)
			    		else:
			    			os.system("sudo sispmctl -t " + switch_number)
			        return "true", 200, {'Access-Control-Allow-Origin': '*'}
		    	except ValueError:
			        return "false", 200, {'Access-Control-Allow-Origin': '*'}
		return "false", 200, {'Access-Control-Allow-Origin': '*'}

class piTemperature(restful.Resource):
	def get(self):
		cpuValue = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
		cpuTemperature = str(round((float(cpuValue) / 1000), 1)) +"'C"

		gpuValue = os.popen("/opt/vc/bin/vcgencmd measure_temp").readline()
		gpuTemperature = gpuValue[5:-1]

		return {'cpu_temperature': cpuTemperature, 'gpu_temperature': gpuTemperature}, 200, {'Access-Control-Allow-Origin': '*'}

class piUptime(restful.Resource):
	def get(self):
		uptimeValue = os.popen("/usr/bin/uptime").readlines().split(",")
		timeData = uptimeValue[0][1:9]
		uptimeData = uptimeValue[0][13:] + "," + uptimeValue[1]
		userData = uptimeValue[2][2:-6]
		loadData = uptimeValue[3][16:] + uptimeValue[4] + uptimeValue[5][:-1]

		return {'time': timeData, 'uptime': uptimeData, 'active_user': userData, 'load': loadData}, 200, {'Access-Control-Allow-Origin': '*'}

class piNetwork(restful.Resource):
	def get(self):
		hwaddValue = os.popen("/sbin/ifconfig eth0 | /bin/grep HWadd").readline().split()

		inetValue = os.popen("/sbin/ifconfig eth0 | /bin/grep inet").readline().split()

		return {'name': hwaddValue[0], 'mac': hwaddValue[4], 'ip': inetValue[1][5:], 'mask': inetValue[3][5:]}, 200, {'Access-Control-Allow-Origin': '*'}


class piGPIO(restful.Resource):
	def get(self, pinID):
		try:
			pinID = int(pinID)
			if pinID in range(0,20):
				return wiringpi2.digitalRead(pinID), 200, {'Access-Control-Allow-Origin': '*'}
		except ValueError:
			return "false", 200, {'Access-Control-Allow-Origin': '*'}


api.add_resource(main, '/')
api.add_resource(apiVersion, '/api/')
api.add_resource(apiLogin, '/api/login/')
api.add_resource(remoteSwitch, '/api/switches/')
api.add_resource(piTemperature, '/api/temp/')
api.add_resource(piUptime, '/api/uptime/')
api.add_resource(piNetwork, '/api/network/')
api.add_resource(piGPIO, '/api/gpio/<string:pinID>')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)

