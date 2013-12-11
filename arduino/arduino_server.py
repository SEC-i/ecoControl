#!/usr/bin/python
import serial, json
from urllib import urlopen, urlencode
from threading import Timer
import time

from flask import Flask, jsonify, request

# set up serial
ser = serial.Serial("/dev/ttyACM0")
ser.baudrate = 9600

# send_data
interval = 60.0
target_urls = ["http://172.16.64.130/api/device/2/data/"] # list target urls here

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

def send_data():
    # Schedule timer to execute repeat_crawl_and_save_data again
    Timer(interval, send_data).start()

    # send 0 to request data
    ser.write("0")
    # read, parse and return data
    ser_data = ser.readline()

    post_data = [('data', json.dumps(json.loads(ser_data)))]

    for url in target_urls:
        urlopen(url, urlencode(post_data))
    
if __name__ == '__main__':
    # Delay first execution of send_data in order to wait for serial to get ready
    Timer(5.0, send_data).start()
    
    # Start flask webserver
    app.run(host="0.0.0.0",debug = True, port = 9002)

