import cProfile
import re

import sys
import os
import time
import collections
import json
from start import *

from simulation import get_new_simulation
from helpers import SimulationBackgroundRunner, crossdomain




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



if __name__ == '__main__':
    env.step_function = append_measurement
    #thread = SimulationBackgroundRunner(env)
    #thread.start()
    #1.1.2013
	#1356998400
    #1.6.2013
    #cProfile.run('env.run(until=1359720732)') 1370088732 
    env.forward = 1370088732 - 1356998400
    cProfile.run("env.run()")

    #app.run(host="0.0.0.0", debug=True, port=8080, use_reloader=False)