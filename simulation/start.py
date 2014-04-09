import sys
import os
import time
import json


from flask import Flask, jsonify, render_template, request
from werkzeug.serving import run_simple
app = Flask(__name__)

from helpers import SimulationBackgroundRunner,  parse_hourly_demand_values
from simulationmanager import SimulationManager

simulation_manager = SimulationManager(time.time()) #time.time()

(env, heat_storage, power_meter, cu, plb, thermal_consumer,
 electrical_consumer, code_executer) = simulation_manager.main_simulation.get_systems()



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data/', methods=['GET'])
def get_data():
    return jsonify(simulation_manager.get_main_measurements())


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
    if 'export' in request.form:
        if export_data(request.form['export']):
            return "1"
        else:
            return "0"
    return "1"


def export_data(filename):
    if os.path.splitext(filename)[1] == ".json":
        data = simulation_manager.get_main_measurements()
        for key in data:
            data[key] = data[key][-1]
        data = json.dumps(data, sort_keys=True, indent=4)
        with open("./exports/" + filename, "w") as export_file:
            for line in data:
                export_file.write(line)
        return True
    return False







if __name__ == '__main__':


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
        simulation_manager.simulation_start()
        if "debug" in sys.argv:
            app.run('0.0.0.0', 8080, debug=True, use_reloader=False)
        else:
            run_simple('0.0.0.0', 8080, app, threaded=True)
