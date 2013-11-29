import os, time, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

from server.planner import *

if __name__ == '__main__':
    Planner(frequency=60)
    # wait until KeyboardInterrupt
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nStopping crawler..."
            sys.exit(1)
