import os, time, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "software_layer_django.settings")

from software_layer_django.crawler import *

if __name__ == '__main__':
    Crawler(frequency=60)
    # wait until KeyboardInterrupt
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print "\nStopping crawler..."
            sys.exit(1)
