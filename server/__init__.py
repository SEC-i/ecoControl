import sys

from server.models import Configuration
from server.helpers import write_pidfile_or_fail, start_demo_simulation


if sys.argv[1] == 'runserver':
    if not write_pidfile_or_fail("/tmp/simulation.pid"):
        # Start demo simulation if in demo mode
        system_mode = Configuration.objects.get(key='system_mode')
        if system_mode.value == 'demo':
            print 'Starting demo simulation...'
            start_demo_simulation()
