#!flask/bin/python
import json
from urllib import urlopen, urlencode
from threading import Timer
from flask import Flask, jsonify, request, make_response
from functools import update_wrapper
import BHKW
#from PeakLoadBoiler import PlBoiler
from HeatStorage import HeatStorage
from Simulation import Simulation
from Heating import Heating

app = Flask(__name__)


simulation = Simulation(100)
# devices.append(HeatReservoir(device_id=2))

# send_data
interval = 60.0
# device id -> target url
target_urls = { 0:"http://172.16.64.130/api/device/1/data/",
                1:"http://172.16.64.130/api/device/4/data/",
                2:"http://172.16.64.130/api/device/3/data/",
                3:"http://172.16.64.130/api/device/5/data/",
                4:"http://172.16.64.130/api/device/6/data/"}

def crossdomain(origin=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/device/<int:device_id>/sensor/<int:sensor_id>', methods = ['GET'])
@crossdomain(origin='*')
def get_sensor(device_id,sensor_id):
    device = simulation.devices[device_id]
    sensor = device.sensors[sensor_id]
    sensor_data =  {
        'device_id': device_id,
        "sensor_id": sensor_id, 
        'name': unicode(sensor.name),
        'value': sensor.value
    } 
    return jsonify( sensor_data )

@app.route('/device/<int:device_id>/get', methods = ['GET'])
@crossdomain(origin='*')
def get_data(device_id):
    device = simulation.devices[device_id]
    device_data = {}
    for key,sensor in device.sensors.items():
        device_data[sensor.name] = sensor.value
    return jsonify( device_data )

@app.route('/device/<int:device_id>/info', methods = ['GET'])
@crossdomain(origin='*')
def get_info(device_id):
    device = simulation.devices[device_id]
    device_data = {"device_name":device.name}
    for key, sensor in device.sensors.items():
        device_data[sensor.name] = sensor.unit
    return jsonify(device_data)

@app.route('/device/<int:device_id>/set', methods = ['POST'])
@crossdomain(origin='*')
def set_data(device_id):
    # set heating temperature
    if "room_temperature" in request.form:
        temperature = float(request.form['room_temperature'])
        if temperature >= 10 and temperature <= 30:
            simulation.set_heating(temperature)
            return "1"
    # set electrical consumption
    if "energy_consumption" in request.form:
        energy = float(request.form['energy_consumption'])
        simulation.set_electrical_consumption(energy)
        return "1"

    return "0"

@app.route("/")
@crossdomain(origin='*')
def hello():
    return "nothing here"


def send_data():
    # Schedule timer to execute send_data again
    Timer(interval, send_data).start()

    for device in simulation.devices.values():
        device_data = {}
        for sensor in device.sensors.values():
            device_data[sensor.name] = sensor.value

        post_data = [('data', json.dumps(device_data))]

        urlopen(target_urls[device.device_id], urlencode(post_data))



if __name__ == '__main__':
    simulation.start()
    send_data()
    app.run(host="0.0.0.0",debug = True, port = 9000, use_reloader=False)
