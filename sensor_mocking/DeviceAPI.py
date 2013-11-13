#!flask/bin/python
from flask import Flask, jsonify, request
import BHKW
from PeakLoadBoiler import PlBoiler
from HeatReservoir import HeatReservoir

app = Flask(__name__)


devices = []
devices.append(BHKW.BHKW(device_id=0))
devices.append(PlBoiler(device_id=1))
devices.append(HeatReservoir(device_id=2))


@app.route('/device/<int:device_id>/sensor/<int:sensor_id>', methods = ['GET'])
def get_sensor(device_id,sensor_id):
    device = next(dev for dev in devices if dev.device_id == device_id)
    sensor = device.getMappedSensor(sensor_id)
    sensor_data =  {
        'device_id': device_id,
        "sensor_id": sensor_id, 
        'name': unicode(sensor.name),
        'value': sensor.value
    } 
    return jsonify( { 'sensor': sensor_data } )

@app.route('/device/<int:device_id>/get', methods = ['GET'])
def get_data(device_id):
    device = next(dev for dev in devices if dev.device_id == device_id)
    device_data = {}
    for sensor in device.sensors:
        #sensor  = device.getMappedSensor(sensor.id)
        device_data[sensor.name] = sensor.value
    return jsonify( {"device" : device_data})

@app.route('/device/<int:device_id>/set', methods = ['POST'])
def set_data(device_id):
    if 'workload' not in request.form:
        return "0"
    device = [dev for dev in devices if dev.device_id == device_id ][0]
    workload = float(request.form['workload'])
    
    if workload >= 0 and workload <= 100:
        device.setcurrentWorkload(workload)
        return "1"
    else:
        return "0"

@app.route('/device/<int:device_id>/info', methods = ['GET'])
def get_info(device_id):
    device = next(dev for dev in devices if dev.device_id == device_id)
    device_data = {"device_name":device.name}
    for sensor in device.sensors:
        #sensor  = device.getMappedSensor(sensor.id)
        device_data[sensor.name] = sensor.unit
    return jsonify( {"device" : device_data})


@app.route("/")
def hello():
    return "nothing here"



if __name__ == '__main__':
    app.run(host="0.0.0.0",debug = True, port = 5001)
