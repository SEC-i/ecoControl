import sys
import time
import collections
from threading import Thread

from flask import Flask, jsonify, make_response, render_template, request
from functools import update_wrapper
from werkzeug.serving import run_simple
app = Flask(__name__)

from simulation import env, heat_storage, electrical_infeed, cu, plb, thermal_consumer, electrical_consumer, code_executer

CACHE_LIMIT = 24 * 365  # 365 days

time_values = collections.deque(maxlen=CACHE_LIMIT)
cu_workload_values = collections.deque(maxlen=CACHE_LIMIT)
plb_workload_values = collections.deque(maxlen=CACHE_LIMIT)
hs_level_values = collections.deque(maxlen=CACHE_LIMIT)
thermal_consumption_values = collections.deque(maxlen=CACHE_LIMIT)
outside_temperature_values = collections.deque(maxlen=CACHE_LIMIT)
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


class FlaskBackgroundRunner(Thread):

    def __init__(self, app):
        Thread.__init__(self)
        self.daemon = True
        self.app = app

    def run(self):
        self.app.run(host="0.0.0.0", debug=True, port=8080, use_reloader=False)


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
        'cu_total_electrical_production': [round(cu.total_electrical_production, 2)],
        'cu_thermal_production': [round(cu.current_thermal_production, 2)],
        'cu_total_thermal_production': [round(cu.total_thermal_production, 2)],
        'cu_total_gas_consumption': [round(cu.total_gas_consumption, 2)],
        'cu_operating_costs': [round(cu.get_operating_costs(), 2)],
        'cu_power_ons': [cu.power_on_count],
        'plb_workload': list(plb_workload_values),
        'plb_thermal_production': [round(plb.current_thermal_production, 2)],
        'plb_total_gas_consumption': [round(plb.total_gas_consumption, 2)],
        'plb_operating_costs': [round(plb.get_operating_costs(), 2)],
        'plb_power_ons': [plb.power_on_count],
        'hs_level': list(hs_level_values),
        'hs_total_input': [round(heat_storage.input_energy, 2)],
        'hs_total_output': [round(heat_storage.output_energy, 2)],
        'hs_empty_count': [round(heat_storage.empty_count, 2)],
        'thermal_consumption': list(thermal_consumption_values),
        'total_thermal_consumption': [round(thermal_consumer.total_consumption, 2)],
        'outside_temperature': list(outside_temperature_values),
        'electrical_consumption': list(electrical_consumption_values),
        'total_electrical_consumption': [round(electrical_consumer.total_consumption, 2)],
        'infeed_reward': [round(electrical_infeed.get_reward(), 2)],
        'infeed_costs': [round(electrical_infeed.get_costs(), 2)]
    })


@app.route('/api/code/', methods=['GET', 'POST'])
@crossdomain(origin='*')
def handle_code():
    if request.method == "POST":
        if 'code' in request.form:
            code_executer.code = request.form['code']
    return jsonify({'code': code_executer.code})


@app.route('/api/settings/', methods=['GET', 'POST'])
@crossdomain(origin='*')
def handle_settings():
    if request.method == "POST":
        if 'base_electrical_demand' in request.form:
            electrical_consumer.base_demand = float(
                request.form['base_electrical_demand'])
        if 'varying_electrical_demand' in request.form:
            electrical_consumer.varying_demand = float(
                request.form['varying_electrical_demand'])
        if 'hs_capacity' in request.form:
            heat_storage.capacity = float(request.form['hs_capacity'])
        if 'hs_target_energy' in request.form:
            heat_storage.target_energy = float(
                request.form['hs_target_energy'])
        if 'hs_undersupplied_threshold' in request.form:
            heat_storage.undersupplied_threshold = float(
                request.form['hs_undersupplied_threshold'])
        if 'cu_max_gas_input' in request.form:
            cu.max_gas_input = float(request.form['cu_max_gas_input'])
        if 'cu_minimal_workload' in request.form:
            cu.minimal_workload = float(request.form['cu_minimal_workload'])
        if 'cu_electrical_efficiency' in request.form:
            cu.electrical_efficiency = float(
                request.form['cu_electrical_efficiency'])
        if 'cu_thermal_efficiency' in request.form:
            cu.thermal_efficiency = float(
                request.form['cu_thermal_efficiency'])
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

    return jsonify({
        'base_electrical_demand': electrical_consumer.base_demand,
        'varying_electrical_demand': electrical_consumer.varying_demand,
        'hs_capacity': heat_storage.capacity,
        'hs_target_energy': heat_storage.target_energy,
        'hs_undersupplied_threshold': heat_storage.undersupplied_threshold,
        'cu_max_gas_input': cu.max_gas_input,
        'cu_minimal_workload': cu.minimal_workload,
        'cu_thermal_efficiency': cu.thermal_efficiency,
        'cu_electrical_efficiency': cu.electrical_efficiency,
        'plb_max_gas_input': plb.max_gas_input,
        'sim_forward': '',
        'daily_thermal_demand': thermal_consumer.daily_demand,
        'daily_electrical_demand': electrical_consumer.daily_demand
    })


def append_measurement():
    if env.now % env.granularity == 0:  # take measurements each hour
        time_values.append(env.now)
        cu_workload_values.append(round(cu.workload, 2))
        plb_workload_values.append(round(plb.workload, 2))
        hs_level_values.append(round(heat_storage.level(), 2))
        thermal_consumption_values.append(
            round(thermal_consumer.get_consumption(), 2))
        outside_temperature_values.append(
            round(thermal_consumer.get_outside_temperature(), 2))
        electrical_consumption_values.append(
            round(electrical_consumer.get_consumption(), 2))

if __name__ == '__main__':
    thread = FlaskBackgroundRunner(app)
    thread.start()
    env.verbose = len(sys.argv) > 1
    env.step_function = append_measurement
    env.run()
