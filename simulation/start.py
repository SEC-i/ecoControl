import sys
import os
import time
import json

from flask import Flask, jsonify, render_template, request
from werkzeug.serving import run_simple
from flask_helpers import gzipped
app = Flask(__name__)

from helpers import SimulationBackgroundRunner,  parse_hourly_demand_values
from core import SimulationManager

DEFAULT_FORECAST_INTERVAL = 3600.0 * 24 * 30

simulation_manager = SimulationManager(time.time())  # time.time()
(env, heat_storage, power_meter, cu, plb, thermal_consumer,
 electrical_consumer, code_executer) = simulation_manager.main_simulation.get_systems()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/data/', methods=['GET'])
@gzipped
def get_data():
    (sim, measurements) = simulation_manager.forecast_for(
        DEFAULT_FORECAST_INTERVAL, blocking=True)
    return jsonify({
        'past': simulation_manager.get_main_measurements(),
        'future': sim.get_measurements(measurements)
    })


@app.route('/api/data/<int:timestamp>/')
def get_delta_data(timestamp):
    (sim, measurements) = simulation_manager.forecast_for(
        DEFAULT_FORECAST_INTERVAL, blocking=True)
    return jsonify({
        'past': simulation_manager.get_main_measurements(start=timestamp),
        'future': sim.get_measurements(measurements)
    })


@app.route('/api/forecasts/', methods=['GET', 'POST'])
@gzipped
def get_forecast_data():
    if request.method == "POST" and 'forecast_time' in request.form:
        # callback function to set different values on forecasted simulation
        def set_sim_values(sim):
            set_values(request.form, sim)
        forecast_time = int(request.form["forecast_time"])
        (sim, measurements) = simulation_manager.forecast_for(
            forecast_time, blocking=True, pre_start_callback=set_sim_values)
    else:
        (sim, measurements) = simulation_manager.forecast_for(
            DEFAULT_FORECAST_INTERVAL, blocking=True)

    return jsonify(sim.get_measurements(measurements))


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


def set_values(settings_dict, simulation=None):
    if simulation == None:
        s = simulation_manager.main_simulation
    else:
        s = simulation
    if 'hs_capacity' in settings_dict:
        s.heat_storage.capacity = float(settings_dict['hs_capacity'])
    if 'hs_min_temperature' in settings_dict:
        s.heat_storage.min_temperature = float(
            settings_dict['hs_min_temperature'])
    if 'hs_critical_temperature' in settings_dict:
        s.heat_storage.critical_temperature = float(
            settings_dict['hs_critical_temperature'])
    if 'hs_target_temperature' in settings_dict:
        s.heat_storage.target_temperature = float(
            settings_dict['hs_target_temperature'])
    if 'cu_max_gas_input' in settings_dict:
        s.cu.max_gas_input = float(settings_dict['cu_max_gas_input'])
    if 'cu_mode' in settings_dict:
        s.cu.thermal_driven = settings_dict['cu_mode'] == "thermal_driven"
    if 'cu_minimal_workload' in settings_dict:
        s.cu.minimal_workload = float(settings_dict['cu_minimal_workload'])
    if 'cu_electrical_efficiency' in settings_dict:
        s.cu.electrical_efficiency = float(
            settings_dict['cu_electrical_efficiency']) / 100.0
    if 'cu_electrical_driven_minimal_production' in settings_dict:
        s.cu.electrical_driven_minimal_production = float(
            settings_dict['cu_electrical_driven_minimal_production'])
    if 'cu_thermal_efficiency' in settings_dict:
        s.cu.thermal_efficiency = float(
            settings_dict['cu_thermal_efficiency']) / 100.0
    if 'plb_max_gas_input' in settings_dict:
        s.plb.max_gas_input = float(settings_dict['plb_max_gas_input'])

    if 'password' in settings_dict and settings_dict['password'] == "InfoProfi" and 'code' in settings_dict:
        s.code_executer.create_function(settings_dict['code'])

    

    daily_thermal_demand = parse_hourly_demand_values(
        'daily_thermal_demand', settings_dict)
    if len(daily_thermal_demand) == 24:
        s.thermal_consumer.daily_demand = daily_thermal_demand

    daily_electrical_variation = parse_hourly_demand_values(
        'daily_electrical_variation', settings_dict)
    if len(daily_electrical_variation) == 24:
        s.electrical_consumer.demand_variation = daily_electrical_variation

    if 'gas_costs' in settings_dict:
        s.plb.gas_costs = float(settings_dict['gas_costs'])
        s.cu.gas_costs = float(settings_dict['gas_costs'])
    if 'electrical_costs' in settings_dict:
        s.electrical_consumer.electrical_costs = float(settings_dict['electrical_costs'])
    if 'feed_in_reward' in settings_dict:
        s.electrical_consumer.feed_in_reward = float(settings_dict['feed_in_reward'])


@app.route('/api/settings/', methods=['GET', 'POST'])
def handle_settings():
    if request.method == "POST":
        set_values(request.form)

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
        simulation_manager.forward_main(60 * 60 * 24 * 30, blocking=True)
        simulation_manager.simulation_start()
        if "debug" in sys.argv:
            app.run('0.0.0.0', 8080, debug=True, use_reloader=False)
        else:
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
            run_simple('0.0.0.0', 8080, app, threaded=True)
