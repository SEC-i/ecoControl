from threading import Thread

from flask import Flask, jsonify, make_response
from functools import update_wrapper
from werkzeug.serving import run_simple
app = Flask(__name__)

from simulation import env, heat_storage, bhkw, plb

class Simulation(Thread):
    def __init__(self, env):
        Thread.__init__(self)
        self.daemon = True
        self.env = env

    def run(self):
        self.env.run()


def crossdomain(origin=None):
    def decorator(f):
        def wrapped_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            h['Access-Control-Allow-Origin'] = origin
            return resp
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route('/api/data/', methods=['GET'])
@crossdomain(origin='*')
def get_simulation_data():
    return jsonify({
        'time': env.now,
        'bhkw_workload': bhkw.get_workload(),
        'bhkw_total_gas_consumption': bhkw.total_gas_consumption,
        'plb_workload': plb.get_workload(),
        'plb_total_gas_consumption': plb.total_gas_consumption,
        'hs_level': heat_storage.level()
    })

if __name__ == '__main__':
    sim = Simulation(env)
    sim.start()
    app.run(host="0.0.0.0",debug = True, port = 7000, use_reloader=False)