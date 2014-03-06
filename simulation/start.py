import sys
import os
import time
import json


from flask import Flask, jsonify, render_template, request
from werkzeug.serving import run_simple
app = Flask(__name__)

from simulation import get_new_simulation
from helpers import SimulationBackgroundRunner, MeasurementCache, parse_hourly_demand_values


(env, heat_storage, power_meter, cu, plb, thermal_consumer,
 electrical_consumer, code_executer) = get_new_simulation()

# initialize MeasurementCache
measurements = MeasurementCache(
    env, cu, plb, heat_storage, thermal_consumer, electrical_consumer)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data/', methods=['GET'])
def get_data():
    return jsonify(get_measurements())


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
        if 'hs_target_temperature' in request.form:
            heat_storage.target_temperature = float(
                request.form['hs_target_temperature'])
        if 'cu_max_gas_input' in request.form:
            cu.max_gas_input = float(request.form['cu_max_gas_input'])
        if 'cu_mode' in request.form:
            cu.thermal_driven = request.form['cu_mode'] == "thermal_driven"
        if 'cu_minimal_workload' in request.form:
            cu.minimal_workload = float(request.form['cu_minimal_workload'])
        if 'cu_electrical_efficiency' in request.form:
            cu.electrical_efficiency = float(
                request.form['cu_electrical_efficiency']) / 100.0
        if 'cu_electrical_driven_minimal_production' in request.form:
            cu.electrical_driven_minimal_production = float(
                request.form['cu_electrical_driven_minimal_production'])
        if 'cu_thermal_efficiency' in request.form:
            cu.thermal_efficiency = float(
                request.form['cu_thermal_efficiency']) / 100.0
        if 'plb_max_gas_input' in request.form:
            plb.max_gas_input = float(request.form['plb_max_gas_input'])

        if 'password' in request.form and request.form['password'] == "InfoProfi" and 'code' in request.form:
            code_executer.create_function(request.form['code'])

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
        'hs_target_temperature': heat_storage.target_temperature,
        'cu_max_gas_input': cu.max_gas_input,
        'cu_mode': 0 if cu.thermal_driven else 1,
        'cu_minimal_workload': cu.minimal_workload,
        'cu_thermal_efficiency': cu.thermal_efficiency * 100.0,
        'cu_electrical_efficiency': cu.electrical_efficiency * 100.0,
        'cu_electrical_driven_minimal_production': cu.electrical_driven_minimal_production,
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
    global env, heat_storage, power_meter, cu, plb, thermal_consumer, electrical_consumer, code_executer, measurements
    env.stop()

    (env, heat_storage, power_meter, cu, plb, thermal_consumer,
     electrical_consumer, code_executer) = get_new_simulation()

    measurements = MeasurementCache(
        env, cu, plb, heat_storage, thermal_consumer, electrical_consumer)

    env.step_function = measurements.take
    thread = SimulationBackgroundRunner(env)
    thread.start()


def export_data(filename):
    if os.path.splitext(filename)[1] == ".json":
        data = get_measurements()
        for key in data:
            data[key] = data[key][-1]
        data = json.dumps(data, sort_keys=True, indent=4)
        with open("./exports/" + filename, "w") as export_file:
            for line in data:
                export_file.write(line)
        return True
    return False


def get_measurements():
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
    ] + measurements.get()

    return dict(output)


def get_total_bilance():
    return cu.get_operating_costs() + plb.get_operating_costs() - \
        power_meter.get_reward() + power_meter.get_costs()


if __name__ == '__main__':

    env.step_function = measurements.take

    if "profile" in sys.argv:
        import cProfile
        env.stop_after_forward = True
        env.forward = 60 * 60 * 24 * 365
        cProfile.run("env.run()")
    elif "simple_profile" in sys.argv:
        env.stop_after_forward = True
        env.forward = 60 * 60 * 24 * 365
        start = time.time()
        env.run()
        print time.time() - start
    else:
        thread = SimulationBackgroundRunner(env)
        thread.start()
        if "debug" in sys.argv:
            app.run('0.0.0.0', 8080, debug=True, use_reloader=False)
        else:
            run_simple('0.0.0.0', 8080, app, threaded=True)
