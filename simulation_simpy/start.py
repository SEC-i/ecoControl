import sys
import time
import collections
from threading import Thread

from flask import Flask, jsonify, make_response, render_template, request
from functools import update_wrapper
from werkzeug.serving import run_simple
app = Flask(__name__)

from simulation import env, heat_storage, electrical_infeed, cu, plb, thermal_consumer, electrical_consumer

CACHE_LIMIT = 24 * 365  # 365 days

time_values = collections.deque(maxlen=CACHE_LIMIT)
cu_workload_values = collections.deque(maxlen=CACHE_LIMIT)
plb_workload_values = collections.deque(maxlen=CACHE_LIMIT)
hs_level_values = collections.deque(maxlen=CACHE_LIMIT)
thermal_consumption_values = collections.deque(maxlen=CACHE_LIMIT)
electrical_consumption_values = collections.deque(maxlen=CACHE_LIMIT)

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
        'cu_workload': list(cu_workload_values),
        'cu_electrical_production': [round(cu.current_electrical_production, 2)],
        'cu_thermal_production': [round(cu.current_thermal_production, 2)],
        'cu_operating_costs': [round(cu.get_operating_costs(), 2)],
        'plb_workload': list(plb_workload_values),
        'plb_thermal_production': [round(plb.current_thermal_production, 2)],
        'plb_operating_costs': [round(plb.get_operating_costs(), 2)],
        'hs_level': list(hs_level_values),
        'thermal_consumption': list(thermal_consumption_values),
        'electrical_consumption': list(electrical_consumption_values),
        'infeed_reward': [round(electrical_infeed.get_reward(), 2)],
        'infeed_costs': [round(electrical_infeed.get_costs(), 2)]
    })


@app.route('/api/settings/', methods=['GET'])
@crossdomain(origin='*')
def get_settings():
    return jsonify(get_settings_json())


@app.route('/api/set/', methods=['POST'])
@crossdomain(origin='*')
def set_data():
    if 'base_thermal_demand' in request.form:
        thermal_consumer.base_demand = float(request.form['base_thermal_demand'])
    if 'varying_thermal_demand' in request.form:
        thermal_consumer.varying_demand = float(request.form['varying_thermal_demand'])
    if 'thermal_demand_noise' in request.form:
        thermal_consumer.noise = request.form['thermal_demand_noise'] == "1"
    if 'base_electrical_demand' in request.form:
        electrical_consumer.base_demand = float(request.form['base_electrical_demand'])
    if 'varying_electrical_demand' in request.form:
        electrical_consumer.varying_demand = float(request.form['varying_electrical_demand'])
    if 'electrical_demand_noise' in request.form:
        electrical_consumer.noise = request.form['electrical_demand_noise'] == "1"
    if 'hs_capacity' in request.form:
        heat_storage.capacity = float(request.form['hs_capacity'])
    if 'hs_target_energy' in request.form:
        heat_storage.target_energy = float(request.form['hs_target_energy'])
    if 'hs_undersupplied_threshold' in request.form:
        heat_storage.undersupplied_threshold = float(
            request.form['hs_undersupplied_threshold'])
    if 'cu_max_gas_input' in request.form:
        cu.max_gas_input = float(request.form['cu_max_gas_input'])
    if 'cu_minimal_workload' in request.form:
        cu.minimal_workload = float(request.form['cu_minimal_workload'])
    if 'cu_noise' in request.form:
        cu.noise = request.form['cu_noise'] == "1"
    if 'sim_forward' in request.form and request.form['sim_forward'] != "":
        env.forward = float(request.form['sim_forward']) * 60 * 60
    if 'plb_max_gas_input' in request.form:
        plb.max_gas_input = float(request.form['plb_max_gas_input'])

    daily_thermal_demand = []
    for i in range(24):
        key = 'daily_thermal_demand_' + str(i)
        if key in request.form:
            daily_thermal_demand.append(float(request.form[key]))
    if len(daily_thermal_demand) == 24:
        thermal_consumer.daily_demand = daily_thermal_demand

    daily_electrical_demand = []
    for i in range(24):
        key = 'daily_electrical_demand_' + str(i)
        if key in request.form:
            daily_electrical_demand.append(float(request.form[key]))
    if len(daily_electrical_demand) == 24:
        electrical_consumer.daily_demand = daily_electrical_demand

    return jsonify(get_settings_json())


def get_settings_json():
    return {
        'base_thermal_demand': thermal_consumer.base_demand,
        'varying_thermal_demand': thermal_consumer.varying_demand,
        'thermal_demand_noise': 1 if thermal_consumer.noise else 0,
        'base_electrical_demand': electrical_consumer.base_demand,
        'varying_electrical_demand': electrical_consumer.varying_demand,
        'electrical_demand_noise': 1 if electrical_consumer.noise else 0,
        'hs_capacity': heat_storage.capacity,
        'hs_target_energy': heat_storage.target_energy,
        'hs_undersupplied_threshold': heat_storage.undersupplied_threshold,
        'cu_max_gas_input': cu.max_gas_input,
        'cu_minimal_workload': cu.minimal_workload,
        'cu_noise': 1 if cu.noise else 0,
        'plb_max_gas_input': plb.max_gas_input,
        'sim_forward': '',
        'daily_thermal_demand': thermal_consumer.daily_demand,
        'daily_electrical_demand': electrical_consumer.daily_demand
    };

def append_measurement():
    time_values.append(env.get_time())
    cu_workload_values.append(round(cu.workload, 2))
    plb_workload_values.append(round(plb.workload, 2))
    hs_level_values.append(round(heat_storage.level(), 2))
    thermal_consumption_values.append(round(thermal_consumer.get_consumption(), 2))
    electrical_consumption_values.append(round(electrical_consumer.get_consumption(), 2))

if __name__ == '__main__':
    sim = Simulation(env)
    env.verbose = len(sys.argv) > 1
    env.step_function = append_measurement
    sim.start()
    app.run(host="0.0.0.0", debug=True, port=7000, use_reloader=False)
