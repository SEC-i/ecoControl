#!/usr/bin/python
import serial, json, os

import threading, time

from flask import Flask, jsonify, request

ser = serial.Serial("/dev/ttyACM0")
ser.baudrate = 9600

app = Flask(__name__)

class ArduinoWorker(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.data = {}
		self.start()
	def run(self):
		print " * Working..."
		while(True):
			ser_data = ser.readline()
			try:
				self.data = json.loads(ser_data)
				if int(self.data['plant1_value']) > 500:
					os.system("sudo sispmctl -q -f 1")
				else:
					os.system("sudo sispmctl -q -o 1")
				if int(self.data['plant2_value']) > 500:
					os.system("sudo sispmctl -q -f 2")
				else:
					os.system("sudo sispmctl -q -o 2")
			except:
				pass

@app.route('/data/', methods = ['GET'])
def get_data():
	return jsonify(worker.data)
	
if __name__ == '__main__':
	worker = ArduinoWorker()
	app.run(host="0.0.0.0",debug = False, use_reloader=False, port = 9002)