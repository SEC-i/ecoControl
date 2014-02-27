import sys
import os
import time
import collections
import json

from flask import Flask, jsonify, render_template, request
from werkzeug.serving import run_simple
app = Flask(__name__)

from simulation import get_new_simulation
from helpers import SimulationBackgroundRunner

CACHE_LIMIT = 24 * 365  # 365 days
measurement_values = ['time', 'cu_workload', 'plb_workload', 'hs_temperature',
                      'thermal_consumption', 'electrical_consumption', 'outside_temperature']

# initialize empty measurement deques
measurements = {}
for i in measurement_values:
    measurements[i] = collections.deque(maxlen=CACHE_LIMIT)

(env, heat_storage, power_meter, cu, plb, thermal_consumer,
 electrical_consumer, code_executer) = get_new_simulation()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data/', methods=['GET'])
def get_data():
    return jsonify(get_measurements(multiple=True))


@app.route('/api/code/', methods=['GET', 'POST'])
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
def handle_settings():
    if request.method == "POST":
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
        if 'cu_mode' in request.form:
            cu.thermal_driven = request.form['cu_mode'] == "thermal_driven"
        if 'cu_minimal_workload' in request.form:
            cu.minimal_workload = float(request.form['cu_minimal_workload'])
        if 'cu_electrical_efficiency' in request.form:
            cu.electrical_efficiency = float(
                request.form['cu_electrical_efficiency']) / 100.0
        if 'cu_electrical_driven_overproduction' in request.form:
            cu.electrical_driven_overproduction = float(
                request.form['cu_electrical_driven_overproduction'])
        if 'cu_thermal_efficiency' in request.form:
            cu.thermal_efficiency = float(
                request.form['cu_thermal_efficiency']) / 100.0
        if 'plb_max_gas_input' in request.form:
            plb.max_gas_input = float(request.form['plb_max_gas_input'])

        if 'code' in request.form:
            code_executer.code = request.form['code']

        daily_thermal_demand = parse_hourly_demand_values(
            'daily_thermal_demand', request.form)
        if len(daily_thermal_demand) == 24:
            thermal_consumer.daily_demand = daily_thermal_demand

        daily_electrical_variation = parse_hourly_demand_values(
            'daily_electrical_variation', request.form)
        if len(daily_electrical_variation) == 24:
            electrical_consumer.demand_variation = daily_electrical_variation

    return jsonify({
        'hs_capacity': heat_storage.capacity,
        'hs_min_temperature': heat_storage.min_temperature,
        'hs_max_temperature': heat_storage.max_temperature,
        'cu_max_gas_input': cu.max_gas_input,
        'cu_mode': 0 if cu.thermal_driven else 1,
        'cu_minimal_workload': cu.minimal_workload,
        'cu_thermal_efficiency': cu.thermal_efficiency * 100.0,
        'cu_electrical_efficiency': cu.electrical_efficiency * 100.0,
        'cu_electrical_driven_overproduction': cu.electrical_driven_overproduction,
        'plb_max_gas_input': plb.max_gas_input,
        'daily_thermal_demand': thermal_consumer.daily_demand,
        'daily_electrical_variation': electrical_consumer.demand_variation,
        'editor_code': code_executer.code,
        'code_snippets': code_executer.snippets_list()
    })


@app.route('/api/simulation/', methods=['POST'])
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


def reset_simulation():
    global env, heat_storage, power_meter, cu, plb, thermal_consumer, electrical_consumer, code_executer
    try:
        env.exit(1)
    except StopIteration:
        pass
    (env, heat_storage, power_meter, cu, plb, thermal_consumer,
     electrical_consumer, code_executer) = get_new_simulation()

    # clear measurements
    for i in measurement_values:
        measurements[i].clear()

    env.step_function = append_measurement
    thread = SimulationBackgroundRunner(env)
    thread.start()


def export_data(filename):
    if os.path.splitext(filename)[1] == ".json":
        data = json.dumps(get_measurements(), sort_keys=True, indent=4)
        with open("./exports/" + filename, "w") as export_file:
            for line in data:
                export_file.write(line)
        return True
    return False


def get_measurements(multiple=False):
    output = [
        ('cu_electrical_production',
         [round(cu.current_electrical_production, 2)]),
        ('cu_total_electrical_production',
         [round(cu.total_electrical_production, 2)]),
        ('cu_thermal_production', [round(cu.current_thermal_production, 2)]),
        ('cu_total_thermal_production',
         [round(cu.total_thermal_production, 2)]),
        ('cu_total_gas_consumption', [round(cu.total_gas_consumption, 2)]),
        ('cu_operating_costs', [round(cu.get_operating_costs(), 2)]),
        ('cu_power_ons', [cu.power_on_count]),
        ('cu_total_hours_of_operation',
         [round(cu.total_hours_of_operation, 2)]),
        ('plb_thermal_production', [round(plb.current_thermal_production, 2)]),
        ('plb_total_gas_consumption', [round(plb.total_gas_consumption, 2)]),
        ('plb_operating_costs', [round(plb.get_operating_costs(), 2)]),
        ('plb_power_ons', [plb.power_on_count]),
        ('plb_total_hours_of_operation',
         [round(plb.total_hours_of_operation, 2)]),
        ('hs_total_input', [round(heat_storage.input_energy, 2)]),
        ('hs_total_output', [round(heat_storage.output_energy, 2)]),
        ('hs_empty_count', [round(heat_storage.empty_count, 2)]),
        ('total_thermal_consumption',
         [round(thermal_consumer.total_consumption, 2)]),
        ('total_electrical_consumption',
         [round(electrical_consumer.total_consumption, 2)]),
        ('infeed_reward', [round(power_meter.get_reward(), 2)]),
        ('infeed_costs', [round(power_meter.get_costs(), 2)]),
        ('total_bilance', [round(get_total_bilance(), 2)]),
        ('code_execution_status',
         [1 if code_executer.execution_successful else 0])
    ]

    for i in measurement_values:
        if multiple:
            output.append((i, list(measurements[i])))
        else:
            output += [
                ('time', env.now),
                ('cu_workload', [round(cu.workload, 2)]),
                ('plb_workload', [round(plb.workload, 2)]),
                ('hs_temperature', [round(heat_storage.get_temperature(), 2)]),
                ('thermal_consumption',
                 [round(thermal_consumer.get_consumption_power(), 2)]),
                ('outside_temperature',
                 [round(thermal_consumer.get_outside_temperature(), 2)]),
                ('electrical_consumption',
                 [round(electrical_consumer.get_consumption_power(), 2)])
            ]

    return dict(output)


def append_measurement():
    if env.now % env.granularity == 0:  # take measurements each hour
        measurements['time'].append(env.now)
        measurements['cu_workload'].append(round(cu.workload, 2))
        measurements['plb_workload'].append(round(plb.workload, 2))
        measurements['hs_temperature'].append(
            round(heat_storage.get_temperature(), 2))
        measurements['thermal_consumption'].append(
            round(thermal_consumer.get_consumption_power(), 2))
        measurements['outside_temperature'].append(
            round(thermal_consumer.get_outside_temperature(), 2))
        measurements['electrical_consumption'].append(
            round(electrical_consumer.get_consumption_power(), 2))


def get_total_bilance():
    return cu.get_operating_costs() + plb.get_operating_costs() - \
        power_meter.get_reward() + power_meter.get_costs()


def parse_hourly_demand_values(namespace, data):
    output = []
    for i in range(24):
        key = namespace + '_' + str(i)
        if key in data:
            output.append(float(request.form[key]))
    return output


if __name__ == '__main__':
    env.verbose = len(sys.argv) > 1
    env.step_function = append_measurement
    thread = SimulationBackgroundRunner(env)
    thread.start()

    run_simple('localhost', 8080, app, threaded=True)
