import sys

from server.helpers import start_demo_simulation

# start demo simulation if neccessary
if sys.argv[1] == 'runserver':
    start_demo_simulation(print_visible=True)
