import sys
import time

from werkzeug.serving import run_simple

from server import app, main


if __name__ == '__main__':

    if "profile" in sys.argv:
        import cProfile
        main.env.stop_after_forward = True
        main.env.forward = 60 * 60 * 24 * 365
        cProfile.run("main.env.run()")
    elif "simple_profile" in sys.argv:
        main.env.stop_after_forward = True
        main.env.forward = 60 * 60 * 24 * 365
        start = time.time()
        main.env.run()
        print time.time() - start
    else:
        if "debug" in sys.argv:
            app.run('0.0.0.0', 8080, debug=True, use_reloader=False)
        else:
            app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
            run_simple('0.0.0.0', 8080, app, threaded=True)
