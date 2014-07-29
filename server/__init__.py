import sys

from server.helpers import start_worker
from server.forecasting import DemoSimulation
from server.technician.hooks import initialize_globals


if sys.argv[1] == 'runserver':
    #initialize stuff like the demosimulation for access in hooks
    initialize_globals()
    #start_worker()
