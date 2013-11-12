#!flask/bin/python
from flask import Flask, jsonify, request
import BHKW

app = Flask(__name__)


devices = []
devices.append(BHKW.BHKW(device_id=0))


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

@app.route('/device/<int:device_id>', methods = ['GET','POST'])
def get_or_set_device(device_id):
    if request.method == 'POST':
        if 'workload' in request.form:
            return set_workload(device_id,request.form['workload'])
    else:
        device = next(dev for dev in devices if dev.device_id == device_id)
        device_data = { "device_id" : device_id }
        for sensor in device.sensors:
            #sensor  = device.getMappedSensor(sensor.id)
            device_data[sensor.name] = sensor.value
        return jsonify( {"device" : device_data})



def set_workload(device_id,workload):
    device = [dev for dev in devices if dev.device_id == device_id ][0]
    workload = float(workload)
    
    if workload >= 0 and workload <= 100:
        device.setcurrentWorkload(workload)
        return "1"
    else:
        return "0"




@app.route("/")
def hello():
    return "nothing here"



if __name__ == '__main__':
    app.run(debug = True)
