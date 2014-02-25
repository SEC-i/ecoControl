import sys
import os
import time
import collections
from threading import Thread
import json

from flask import Flask, jsonify, make_response, render_template, request
from functools import update_wrapper
from werkzeug.serving import run_simple
app = Flask(__name__)

from simulation import init_simulation

(env, heat_storage, electrical_infeed, cu, plb, thermal_consumer,
 electrical_consumer, code_executer) = init_simulation()

CACHE_LIMIT = 24 * 365  # 365 days

time_values = collections.deque(maxlen=CACHE_LIMIT)
cu_workload_values = collections.deque(maxlen=CACHE_LIMIT)
plb_workload_values = collections.deque(maxlen=CACHE_LIMIT)
hs_temperature_values = collections.deque(maxlen=CACHE_LIMIT)
thermal_consumption_values = collections.deque(maxlen=CACHE_LIMIT)
outside_temperature_values = collections.deque(maxlen=CACHE_LIMIT)
electrical_consumption_values = collections.deque(maxlen=CACHE_LIMIT)


def reset_simulation():
    global env, heat_storage, electrical_infeed, cu, plb, thermal_consumer, electrical_consumer, code_executer
    try:
        env.exit(1)
    except StopIteration:
        pass
    (env, heat_storage, electrical_infeed, cu, plb, thermal_consumer,
     electrical_consumer, code_executer) = init_simulation()
    time_values.clear()
    cu_workload_values.clear()
    plb_workload_values.clear()
    hs_temperature_values.clear()
    thermal_consumption_values.clear()
    outside_temperature_values.clear()
    electrical_consumption_values.clear()

    env.step_function = append_measurement
    thread = SimulationBackgroundRunner(env)
    thread.start()


def crossdomain(origin=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        return update_wrapper(wrapped_function, f)
    return decorator


class SimulationBackgroundRunner(Thread):

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
        'cu_total_electrical_production': [round(cu.total_electrical_production, 2)],
        'cu_thermal_production': [round(cu.current_thermal_production, 2)],
        'cu_total_thermal_production': [round(cu.total_thermal_production, 2)],
        'cu_total_gas_consumption': [round(cu.total_gas_consumption, 2)],
        'cu_operating_costs': [round(cu.get_operating_costs(), 2)],
        'cu_power_ons': [cu.power_on_count],
        'cu_total_hours_of_operation': [round(cu.total_hours_of_operation, 2)],
        'plb_workload': list(plb_workload_values),
        'plb_thermal_production': [round(plb.current_thermal_production, 2)],
        'plb_total_gas_consumption': [round(plb.total_gas_consumption, 2)],
        'plb_operating_costs': [round(plb.get_operating_costs(), 2)],
        'plb_power_ons': [plb.power_on_count],
        'plb_total_hours_of_operation': [round(plb.total_hours_of_operation, 2)],
        'hs_temperature': list(hs_temperature_values),
        'hs_total_input': [round(heat_storage.input_energy, 2)],
        'hs_total_output': [round(heat_storage.output_energy, 2)],
        'hs_empty_count': [round(heat_storage.empty_count, 2)],
        'thermal_consumption': list(thermal_consumption_values),
        'total_thermal_consumption': [round(thermal_consumer.total_consumption, 2)],
        'outside_temperature': list(outside_temperature_values),
        'electrical_consumption': list(electrical_consumption_values),
        'total_electrical_consumption': [round(electrical_consumer.total_consumption, 2)],
        'infeed_reward': [round(electrical_infeed.get_reward(), 2)],
        'infeed_costs': [round(electrical_infeed.get_costs(), 2)],
        'code_execution_status': [1 if code_executer.execution_successful else 0]
    })


@app.route('/api/code/', methods=['GET', 'POST'])
@crossdomain(origin='*')
def handle_code():
    if request.method == "POST":
        if 'snippet' in request.form:
            return jsonify({'editor_code': code_executer.get_snippet_code(request.form['snippet'])})
        if 'save_snippet' in request.form and 'code' in request.form:
            if code_executer.save_snippet(request.form['save_snippet'], request.form['code']):
                return jsonify({
                    'editor_code': request.form['code'],
                    'code_snippets': code_executer.snippets_list()
                })

    return jsonify({'editor_code': code_executer.code})


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
        if 'hs_min_temperature' in request.form:
            heat_storage.min_temperature = float(
                request.form['hs_min_temperature'])
        if 'hs_max_temperature' in request.form:
            heat_storage.max_temperature = float(
                request.form['hs_max_temperature'])
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
        if 'plb_max_gas_input' in request.form:
            plb.max_gas_input = float(request.form['plb_max_gas_input'])

        if 'code' in request.form:
            code_executer.code = request.form['code']

        daily_thermal_demand = []
        for i in range(24):
            key = 'daily_thermal_demand_' + str(i)
            if key in request.form:
                daily_thermal_demand.append(float(request.form[key]))
        if len(daily_thermal_demand) == 24:
            thermal_consumer.daily_demand = daily_thermal_demand

        daily_electrical_variation = []
        for i in range(24):
            key = 'daily_electrical_variation_' + str(i)
            if key in request.form:
                daily_electrical_variation.append(float(request.form[key]))
        if len(daily_electrical_variation) == 24:
            electrical_consumer.demand_variation = daily_electrical_variation

    return jsonify({
        'base_electrical_demand': electrical_consumer.base_demand,
        'varying_electrical_demand': electrical_consumer.varying_demand,
        'hs_capacity': heat_storage.capacity,
        'hs_min_temperature': heat_storage.min_temperature,
        'hs_max_temperature': heat_storage.max_temperature,
        'cu_max_gas_input': cu.max_gas_input,
        'cu_minimal_workload': cu.minimal_workload,
        'cu_thermal_efficiency': cu.thermal_efficiency,
        'cu_electrical_efficiency': cu.electrical_efficiency,
        'plb_max_gas_input': plb.max_gas_input,
        'daily_thermal_demand': thermal_consumer.daily_demand,
        'daily_electrical_variation_': electrical_consumer.daily_demand,
        'editor_code': code_executer.code,
        'code_snippets': code_executer.snippets_list()
    })


@app.route('/api/simulation/', methods=['POST'])
@crossdomain(origin='*')
def handle_simulation():
    if 'forward' in request.form and request.form['forward'] != "":
        env.forward = float(request.form['forward']) * 60 * 60
    if 'reset' in request.form:
        reset_simulation()
    if 'export' in request.form:
        if export_data(request.form['export']):
            return "1"
        else:
            return "0"
    return "1"


def export_data(filename):
    if os.path.splitext(filename)[1] == ".json":
        data = json.dumps({
            'time': env.now,
            'cu_workload': round(cu.workload, 2),
            'cu_electrical_production': round(cu.current_electrical_production, 2),
            'cu_total_electrical_production': round(cu.total_electrical_production, 2),
            'cu_thermal_production': round(cu.current_thermal_production, 2),
            'cu_total_thermal_production': round(cu.total_thermal_production, 2),
            'cu_total_gas_consumption': round(cu.total_gas_consumption, 2),
            'cu_operating_costs': round(cu.get_operating_costs(), 2),
            'cu_power_ons': cu.power_on_count,
            'cu_total_hours_of_operation': round(cu.total_hours_of_operation, 2),
            'plb_workload': round(plb.workload, 2),
            'plb_thermal_production': round(plb.current_thermal_production, 2),
            'plb_total_gas_consumption': round(plb.total_gas_consumption, 2),
            'plb_operating_costs': round(plb.get_operating_costs(), 2),
            'plb_power_ons': plb.power_on_count,
            'plb_total_hours_of_operation': round(plb.total_hours_of_operation, 2),
            'hs_temperature': round(heat_storage.get_temperature(), 2),
            'hs_total_input': round(heat_storage.input_energy, 2),
            'hs_total_output': round(heat_storage.output_energy, 2),
            'hs_empty_count': round(heat_storage.empty_count, 2),
            'thermal_consumption': round(thermal_consumer.get_consumption(), 2),
            'total_thermal_consumption': round(thermal_consumer.total_consumption, 2),
            'outside_temperature': round(env.get_outside_temperature(), 2),
            'electrical_consumption': round(electrical_consumer.get_consumption(), 2),
            'total_electrical_consumption': round(electrical_consumer.total_consumption, 2),
            'infeed_reward': round(electrical_infeed.get_reward(), 2),
            'infeed_costs': round(electrical_infeed.get_costs(), 2),
            'code_execution_status': 1 if code_executer.execution_successful else 0
        }, sort_keys = True, indent = 4)
        with open("./exports/" + filename, "w") as export_file:
            for line in data:
                export_file.write(line)

        return True

    return False


def append_measurement():
    if env.now % env.granularity == 0:  # take measurements each hour
        time_values.append(env.now)
        cu_workload_values.append(round(cu.workload, 2))
        plb_workload_values.append(round(plb.workload, 2))
        hs_temperature_values.append(round(heat_storage.get_temperature(), 2))
        thermal_consumption_values.append(
            round(thermal_consumer.get_consumption(), 2))
        outside_temperature_values.append(
            round(env.get_outside_temperature(), 2))
        electrical_consumption_values.append(
            round(electrical_consumer.get_consumption(), 2))

if __name__ == '__main__':
    env.verbose = len(sys.argv) > 1
    env.step_function = append_measurement
    thread = SimulationBackgroundRunner(env)
    thread.start()

    app.run(host="0.0.0.0", debug=True, port=8080, use_reloader=False)
