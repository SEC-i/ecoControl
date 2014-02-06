#!flask/bin/python
from flask import Flask, jsonify, request, make_response, render_template
from functools import update_wrapper
app = Flask(__name__)


from simulation import Simulation
simulation = Simulation(100)

def crossdomain(origin=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        return update_wrapper(wrapped_function, f)
    return decorator

@app.route('/')
@crossdomain(origin='*')
def index():
    return render_template('index.html')

@app.route('/api/data/', methods = ['GET'])
@crossdomain(origin='*')
def get_simulation_data():
    output = {}
    for i in simulation.devices:
        device = simulation.devices[i]
        device_data = {}
        for key, sensor in device.sensors.items():
            device_data[sensor.name] = sensor.value
        output[device.device_id] = device_data

    return jsonify( output )

@app.route('/api/info/', methods = ['GET'])
@crossdomain(origin='*')
def get_simulation_info():
    output = {}
    for i in simulation.devices:
        device = simulation.devices[i]
        device_data = {'name': device.name}
        for key, sensor in device.sensors.items():
            device_data[sensor.name] = sensor.unit
        output[device.device_id] = device_data

    return jsonify(output)

@app.route('/api/set/', methods = ['POST'])
@crossdomain(origin='*')
def set_data():
    # set heating temperature
    if "room_temperature" in request.form:
        temperature = float(request.form['room_temperature'])
        if temperature >= 10 and temperature <= 30:
            simulation.set_heating(temperature)
            return "1"

    # set electrical consumption
    if "electric_consumption" in request.form:
        power = float(request.form['electric_consumption'])
        simulation.set_electric_consumption(power)
        return "1"

    # set outside temperature
    if "outside_temperature" in request.form:
        temperature = float(request.form['outside_temperature'])
        simulation.set_outside_temperature(temperature)
        return "1"

    return "0"

@app.route('/api/device/<int:device_id>/get/', methods = ['GET'])
@crossdomain(origin='*')
def get_data(device_id):
    device = simulation.devices[device_id]
    device_data = {}
    for key,sensor in device.sensors.items():
        device_data[sensor.name] = sensor.value
    return jsonify( device_data )

@app.route('/api/device/<int:device_id>/info/', methods = ['GET'])
@crossdomain(origin='*')
def get_info(device_id):
    device = simulation.devices[device_id]
    device_data = {"device_name":device.name}
    for key, sensor in device.sensors.items():
        device_data[sensor.name] = sensor.unit
    return jsonify(device_data)



if __name__ == '__main__':
    simulation.start()
    app.run(host="0.0.0.0",debug = True, port = 9000, use_reloader=False)
