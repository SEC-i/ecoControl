import os
import time
import json

from flask import Flask, jsonify, render_template, request
from server.helpers import gzipped, update_simulation, export_data
app = Flask(__name__)

from core import Simulation

DEFAULT_FORECAST_INTERVAL = 3600.0 * 24 * 30

main = Simulation(time.time())  # time.time()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/start/', methods=['POST'])
def start():
    update_simulation(main, request.form.items())
    main.forward(60 * 60 * 24 * 30, blocking=True)
    main.start()
    return "1"


@app.route('/api/data/', methods=['GET'])
@gzipped
def get_data():
    future = main.get_forecasted_copy(
        DEFAULT_FORECAST_INTERVAL, blocking=True)
    return jsonify({
        'past': main.get_measurements(),
        'future': future.get_measurements(measurements)
    })


@app.route('/api/data/<int:timestamp>/')
def get_delta_data(timestamp):
    future = main.get_forecasted_copy(
        DEFAULT_FORECAST_INTERVAL, blocking=True)
    return jsonify({
        'past': main.get_measurements(start=timestamp),
        'future': future.get_measurements()
    })


@app.route('/api/forecasts/', methods=['GET', 'POST'])
@gzipped
def get_forecast_data():
    if request.method == "POST" and 'forecast_time' in request.form:
        # callback function to set different values on forecasted simulation
        def set_sim_values(simulation):
            update_simulation(simulation, request.form)
        forecast_time = int(request.form["forecast_time"])
        future = main.get_forecasted_copy(
            forecast_time, blocking=True, pre_start_callback=set_sim_values)
    else:
        future = main.get_forecasted_copy(
            DEFAULT_FORECAST_INTERVAL, blocking=True)

    return jsonify(future.get_measurements())


@app.route('/api/code/', methods=['GET', 'POST'])
def handle_code():
    if request.method == "POST":
        if 'snippet' in request.form:
            return jsonify({'editor_code': main.code_executer.get_snippet_code(request.form['snippet'])})
        if 'save_snippet' in request.form and 'code' in request.form:
            if code_executer.save_snippet(request.form['save_snippet'], request.form['code']):
                return jsonify({
                    'editor_code': request.form['code'],
                    'code_snippets': main.code_executer.snippets_list()
                })

    return jsonify({'editor_code': main.code_executer.code})


@app.route('/api/settings/', methods=['GET', 'POST'])
def handle_settings():
    if request.method == "POST":
        update_simulation(main, request.form)

    return jsonify({
        'hs_capacity': main.heat_storage.capacity,
        'hs_min_temperature': main.heat_storage.min_temperature,
        'hs_target_temperature': main.heat_storage.target_temperature,
        'cu_max_gas_input': main.cu.max_gas_input,
        'cu_mode': 0 if main.cu.thermal_driven else 1,
        'cu_minimal_workload': main.cu.minimal_workload,
        'cu_thermal_efficiency': main.cu.thermal_efficiency,
        'cu_electrical_efficiency': main.cu.electrical_efficiency,
        'cu_electrical_driven_minimal_production': main.cu.electrical_driven_minimal_production,
        'plb_max_gas_input': main.plb.max_gas_input,
        'daily_thermal_demand': main.thermal_consumer.daily_demand,
        'daily_electrical_variation': main.electrical_consumer.demand_variation,
        'editor_code': main.code_executer.code,
        'code_snippets': main.code_executer.snippets_list(),
        'simulation_running': 1 if main.running else 0
    })


@app.route('/api/simulation/', methods=['POST'])
def handle_simulation():
    if 'forward' in request.form and request.form['forward'] != "":
        main.env.forward = float(request.form['forward']) * 60 * 60
    if 'export' in request.form:
        if export_data(request.form['export']):
            return "1"
        else:
            return "0"
    return "1"
