from threading import Thread
import time

from flask import Flask, jsonify, make_response, render_template, request
from functools import update_wrapper
from werkzeug.serving import run_simple
app = Flask(__name__)


from simulation import env, heat_storage, bhkw, plb, thermal
import collections

measurements_limit = 24 * 30  # 30 days

time_values = collections.deque(maxlen=measurements_limit)
bhkw_workload_values = collections.deque(maxlen=measurements_limit)
bhkw_electrical_power_values = collections.deque(maxlen=measurements_limit)
bhkw_thermal_power_values = collections.deque(maxlen=measurements_limit)
bhkw_total_gas_consumption_values = collections.deque(
    maxlen=measurements_limit)
plb_workload_values = collections.deque(maxlen=measurements_limit)
plb_thermal_power_values = collections.deque(maxlen=measurements_limit)
plb_total_gas_consumption_values = collections.deque(maxlen=measurements_limit)
hs_level_values = collections.deque(maxlen=measurements_limit)
thermal_consumption_values = collections.deque(maxlen=measurements_limit)


def crossdomain(origin=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        return update_wrapper(wrapped_function, f)
    return decorator


class Simulation(Thread):

    def __init__(self, env):
        Thread.__init__(self)
        self.daemon = True
        self.env = env

    def run(self):
        self.env.run()


@app.route('/')
@crossdomain(origin='*')
def index():
    return render_template('index.html')


@app.route('/api/data/', methods=['GET'])
@crossdomain(origin='*')
def get_data():
    return jsonify({
        'time': list(time_values),
        'bhkw_workload': list(bhkw_workload_values),
        'bhkw_electrical_power': list(bhkw_electrical_power_values),
        'bhkw_thermal_power': list(bhkw_thermal_power_values),
        'bhkw_total_gas_consumption': list(bhkw_total_gas_consumption_values),
        'plb_workload': list(plb_workload_values),
        'plb_thermal_power': list(plb_thermal_power_values),
        'plb_total_gas_consumption': list(plb_total_gas_consumption_values),
        'hs_level': list(hs_level_values),
        'thermal_consumption': list(thermal_consumption_values)
    })


@app.route('/api/settings/', methods=['GET'])
@crossdomain(origin='*')
def get_settings():
    return jsonify({
        'average_thermal_demand': thermal.average_demand,
        'varying_thermal_demand': thermal.varying_demand,
        'thermal_demand_noise': 1 if thermal.noise else 0,
        'hs_capacity': heat_storage.capacity,
        'hs_target_energy': heat_storage.target_energy,
        'hs_undersupplied_threshold': heat_storage.undersupplied_threshold,
        'bhkw_max_gas_input': bhkw.max_gas_input,
        'bhkw_minimal_workload': bhkw.minimal_workload,
        'bhkw_noise': 1 if bhkw.noise else 0,
        'plb_max_gas_input': plb.max_gas_input,
        'sim_forward': '',
    })


@app.route('/api/set/', methods=['POST'])
@crossdomain(origin='*')
def set_data():
    if 'average_thermal_demand' in request.form:
        thermal.average_demand = float(request.form['average_thermal_demand'])
    if 'varying_thermal_demand' in request.form:
        thermal.varying_demand = float(request.form['varying_thermal_demand'])
    if 'thermal_demand_noise' in request.form:
        thermal.noise = request.form['thermal_demand_noise'] == "1"
    if 'hs_capacity' in request.form:
        heat_storage.capacity = float(request.form['hs_capacity'])
    if 'hs_target_energy' in request.form:
        heat_storage.target_energy = float(request.form['hs_target_energy'])
    if 'hs_undersupplied_threshold' in request.form:
        heat_storage.undersupplied_threshold = float(
            request.form['hs_undersupplied_threshold'])
    if 'bhkw_max_gas_input' in request.form:
        bhkw.max_gas_input = float(request.form['bhkw_max_gas_input'])
    if 'bhkw_minimal_workload' in request.form:
        bhkw.minimal_workload = float(request.form['bhkw_minimal_workload'])
    if 'bhkw_noise' in request.form:
        bhkw.noise = request.form['bhkw_noise'] == "1"
    if 'sim_forward' in request.form and request.form['sim_forward'] != "":
        env.forward = float(request.form['sim_forward']) * 60 * 60
    if 'plb_max_gas_input' in request.form:
        plb.max_gas_input = float(request.form['plb_max_gas_input'])

    return jsonify({
        'average_thermal_demand': thermal.average_demand,
        'varying_thermal_demand': thermal.varying_demand,
        'thermal_demand_noise': 1 if thermal.noise else 0,
        'hs_capacity': heat_storage.capacity,
        'hs_target_energy': heat_storage.target_energy,
        'hs_undersupplied_threshold': heat_storage.undersupplied_threshold,
        'bhkw_max_gas_input': bhkw.max_gas_input,
        'bhkw_minimal_workload': bhkw.minimal_workload,
        'bhkw_noise': 1 if bhkw.noise else 0,
        'plb_max_gas_input': plb.max_gas_input,
        'sim_forward': '',
    })


def append_measurement():
    time_values.append(env.get_time())
    bhkw_workload_values.append(round(bhkw.get_workload(), 2))
    bhkw_electrical_power_values.append(round(bhkw.get_electrical_power(), 2))
    bhkw_thermal_power_values.append(round(bhkw.get_thermal_power(), 2))
    bhkw_total_gas_consumption_values.append(
        round(bhkw.total_gas_consumption, 2))
    plb_workload_values.append(round(plb.get_workload(), 2))
    plb_thermal_power_values.append(round(plb.get_thermal_power(), 2))
    plb_total_gas_consumption_values.append(round(plb.total_gas_consumption, 2))
    hs_level_values.append(round(heat_storage.level(), 2))
    thermal_consumption_values.append(round(thermal.get_consumption(), 2))

if __name__ == '__main__':
    sim = Simulation(env)
    env.quiet = True
    env.step_function = append_measurement
    sim.start()
    app.run(host="0.0.0.0", debug=True, port=7000, use_reloader=False)
