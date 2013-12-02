#!/usr/bin/python
import serial, json

from flask import Flask, jsonify, request

# set up serial
ser = serial.Serial("/dev/ttyACM0")
ser.baudrate = 9600

app = Flask(__name__)

@app.route('/get/', methods = ['GET'])
def get_data():
	try:
		# send 0 to request data
		ser.write("0")
		# read, parse and return data
		ser_data = ser.readline()
		return jsonify(json.loads(ser_data))
	except:
		return "0"

@app.route('/set/', methods = ['POST'])
def set_data():

	if 'water_plants' in request.form:
		try:
			# send 3 to turn on relay for 20s
			if request.form['water_plants']=="1":
				ser.write("3")
			# read, parse and return data
			ser_data = ser.readline()
			return jsonify(json.loads(ser_data))
		except:
			return "0"

	# relay_state required
	if 'relay_state' in request.form:
		try:
			# send 1 to turn on relay, otherwise send 2 to turn it off
			if request.form['relay_state']=="1":
				ser.write("1")
			else:
				ser.write("2")
			# read, parse and return data
			ser_data = ser.readline()
			return jsonify(json.loads(ser_data))
		except:
			return "0"

	return "0"
	
if __name__ == '__main__':
	app.run(host="0.0.0.0",debug = True, port = 9002)