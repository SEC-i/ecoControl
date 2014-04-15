import sys
import time

from werkzeug.serving import run_simple

from server import app, simulation_manager


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
