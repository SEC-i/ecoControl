import sys

from server.helpers import start_worker, DemoSimulation

# start demo simulation if neccessary
if sys.argv[1] == 'runserver':
    start_worker()
    DemoSimulation.start_or_get(print_visible=True)
