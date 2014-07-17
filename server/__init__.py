import sys

from server.helpers import start_worker
from server.forecasting import DemoSimulation

# start demo simulation if neccessary
if sys.argv[1] == 'runserver':
    pass
    #start_worker()
    #DemoSimulation.start_or_get(print_visible=True)
