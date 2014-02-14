from threading import Thread
import time

from flask import Flask, jsonify, make_response, render_template, request
from functools import update_wrapper
from werkzeug.serving import run_simple
app = Flask(__name__)


from simulation import env, heat_storage, bhkw, plb, thermal

start_time = time.time()

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
        'time': start_time + env.now,
        'bhkw_workload': round(bhkw.get_workload(), 2),
        'bhkw_electrical_power': round(bhkw.get_electrical_power(), 2),
        'bhkw_thermal_power': round(bhkw.get_thermal_power(), 2),
        'bhkw_total_gas_consumption': round(bhkw.total_gas_consumption, 2),
        'plb_workload': round(plb.get_workload(), 2),
        'plb_thermal_power': round(plb.get_thermal_power(), 2),
        'plb_total_gas_consumption': round(plb.total_gas_consumption, 2),
        'hs_level': round(heat_storage.level(), 2),
        'thermal_consumption': round(thermal.get_consumption(), 2)
    })

@app.route('/api/settings/', methods=['GET'])
@crossdomain(origin='*')
def get_settings():
    return jsonify({
        'average_thermal_demand': thermal.average_demand,
        'varying_thermal_demand': thermal.varying_demand,
        'hs_capacity': heat_storage.capacity,
        'hs_target_energy': heat_storage.target_energy,
        'hs_undersupplied_threshold': heat_storage.undersupplied_threshold,
        'bhkw_max_gas_input': bhkw.max_gas_input,
        'bhkw_minimal_workload': bhkw.minimal_workload,
        'plb_max_gas_input': plb.max_gas_input,
    })

@app.route('/api/set/', methods=['POST'])
@crossdomain(origin='*')
def set_data():
    thermal.average_demand = float(request.form['average_thermal_demand'])
    thermal.varying_demand = float(request.form['varying_thermal_demand'])
    heat_storage.capacity = float(request.form['hs_capacity'])
    heat_storage.target_energy = float(request.form['hs_target_energy'])
    heat_storage.undersupplied_threshold = float(request.form['hs_undersupplied_threshold'])
    bhkw.max_gas_input = float(request.form['bhkw_max_gas_input'])
    bhkw.minimal_workload = float(request.form['bhkw_minimal_workload'])
    plb.max_gas_input = float(request.form['plb_max_gas_input'])

    return jsonify({
        'average_thermal_demand': thermal.average_demand,
        'varying_thermal_demand': thermal.varying_demand,
        'hs_capacity': heat_storage.capacity,
        'hs_target_energy': heat_storage.target_energy,
        'hs_undersupplied_threshold': heat_storage.undersupplied_threshold,
        'bhkw_max_gas_input': bhkw.max_gas_input,
        'bhkw_minimal_workload': bhkw.minimal_workload,
        'plb_max_gas_input': plb.max_gas_input,
    })

if __name__ == '__main__':
    sim = Simulation(env)
    env.quiet = True
    sim.start()
    app.run(host="0.0.0.0",debug = True, port = 7000, use_reloader=False)